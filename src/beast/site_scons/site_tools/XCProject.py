# Info: ----------------------------------------------------------------------------

# Portions of this file Copyright (c) 2012 Google Inc.


"""
A tool for generating .xcodeproj files by linking together SCons and gyp.
"""


# Imports: -------------------------------------------------------------------------


from __future__ import with_statement, print_function

import os

from VSProject import xsorted

import SCons.Builder
import SCons.Node.FS
import SCons.Node
import SCons.Script.Main
import SCons.Util

from gyp import xcode


# Utils: ---------------------------------------------------------------------------


def makeList(x):
    if not x:
        return []
    elif type(x) is list:
        return x
    elif type(x) is tuple:
        return list(x)
    else:
        return [x]


def unQualifyTarget(target):
    return xcode.common.ParseQualifiedTarget(target)[1]


# SCons: ---------------------------------------------------------------------------


def buildProject(target, source, env):
    if len(target) != 1:
        raise ValueError("Exactly one target must be specified")

    project_node = str(target[0])

    try:
        configs = env["XCPROJECT_CONFIGS"]
    except KeyError:
        raise ValueError("Could not find XCPROJECT_CONFIGS")

    XCProject(project_node, configs)


def projectEmitter(target, source, env):
    if len(target) != 1:
        raise ValueError("Exactly one target must be specified")

    # If source is unspecified this condition will be true
    if not source or source[0] == target[0]:
        source = []

    outputs = []
    for node in makeList(target):
        outputs.append(env.GetBuildPath(node))
    return outputs, source


projectBuilder = SCons.Builder.Builder(
    action = SCons.Action.Action(buildProject, "Building ${TARGET}"),
    emitter = projectEmitter)


def generate(env):
    try:
        env["BUILDERS"]["XCProject"]
    except KeyError:
        env["BUILDERS"]["XCProject"] = projectBuilder
    env.AddMethod(XCProjectConfig, "XCProjectConfig")


def exists(env):
    return True


# Main: ----------------------------------------------------------------------------


def XCProject(project_node, configs):
    project_node = str(project_node)
    build_file_head, build_file_tail = os.path.split(project_node)
    build_file = os.path.join(build_file_head, os.path.relpath(os.path.abspath(os.path.join(build_file_head, build_file_tail)), build_file_head))
    assert project_node == build_file, "Build file directory must be relative."

    target_configs, included_files = ConfigManager(build_file, build_file_head, configs).processConfigs()
    target_list = xsorted(target_configs.keys())

    target_dict = {}
    for target in target_list:
        target_dict[target] = {
            "toolset": "target",
            "type": "executable",
            "mac_xctest_bundle": 0,
            "mac_bundle": 0,
            "actions": [
# What a properly formatted action should look like:
##                { "message": None,
##                  "action": ["scons"],
##                  "process_outputs_as_sources": False,
##                  "process_outputs_as_mac_bundle_resources": False,
##                  "outputs": []
##                  }
                ],
            "rules": [
# What a properly formatted rule should look like:
##                { "extension": "scons",
##                  "rule_sources": [],
##                  "outputs": [],
##                  "process_outputs_as_sources": False,
##                  "process_outputs_as_mac_bundle_resources": False,
##                  "message": None,
##                  "action": "scons",
##                  "rule_name": "scons",
##                  "inputs": []
##                  }
                ],
            "mac_bundle_resources": [],
            "mac_framework_private_headers": [],
            "mac_framework_headers": [],
            "copies": [
# What a properly formatted copy should look like:
##                { "destination": "/",
##                  "files": []
##                  }
                ],
            "postbuilds": [
# What a properly formatted postbuild should look like:
##                { "action": "scons",
##                  "postbuild_name": "scons"
##                  }
                ]
            }
        if target in target_configs:
            target_dict[target].update(target_configs[target])

    target_dict_list = []
    for target in target_list:
        target_name = unQualifyTarget(target)
        target_dict_list.append({
            "xcode_create_dependents_test_runner": 0,
            "target_name": target_name,
            "toolset": None,
            "suppress_wildcard": False,
            "run_as": None
            })
    build_file_dict = {
        "xcode_settings": projectconfig(),
        "configurations": {
            "Debug": projectConfiguration(debug=True),
            "Release": projectConfiguration(debug=False)
            },
        "included_files": included_files,
        "targets": target_dict_list
        }

    params = {
        "options": Options(),
        "generator_flags": {
            "xcode_parallel_builds": True,
            "xcode_serialize_all_test_runs": True,
            "xcode_project_version": None,
            "xcode_list_excluded_files": True,
            "standalone": None,
            "support_target_suffix": " Support"
            }
        }

    return xcode.GenerateOutput(target_list, target_dict, build_file, build_file_dict, params)


class ConfigManager(object):
    debug = True
    recursion = 0

    def __init__(self, build_file, build_file_head, configs):
        self.build_file = str(build_file)
        self.build_file_head = str(build_file_head)
        self.printdebug("Directory: "+self.build_file_head)
        self.configs = configs

    def processConfigs(self):
        self.target_configs = {}
        self.included_files = []
        self.include_dirs = []
        self.library_dirs = []
        release = None
        for config in self.configs:
            self.printdebug("Config: "+str(config))
            if config["variant"] == "debug":
                debug = config
            elif config["variant"] == "release":
                release = config
            else:
                raise ValueError("Unkown variant "+str(config["variant"]))
        self.env = debug["env"]
        self.walk(debug["target"])
        if release is not None:
            self.env = release["env"]
            self.walk(self.formatTarget(debug["target"]), self.addTarget(release["target"], "Release"))
        for target in self.target_configs:
            self.target_configs[target]["configurations"] = {
                "Release": targetConfiguration(self.include_dirs, self.library_dirs, debug=False),
                "Debug": targetConfiguration(self.include_dirs, self.library_dirs, debug=True)
                }
        return self.target_configs, self.included_files

    def formatPath(self, path):
        return os.path.relpath(os.path.abspath(str(path)), self.build_file_head)

    def formatTarget(self, target):
        return xcode.common.QualifiedTarget(self.build_file, self.formatPath(target), None)

    def addTarget(self, target, default_configuration="Debug"):
        name = str(target)
        target = self.formatTarget(target)
        self.printdebug("Target: "+str(target)+" (Name: "+name+")")
        if target not in self.target_configs:
            self.target_configs[target] = {
                "default_configuration": default_configuration,
                "sources": [],
                "libraries": [],
                "dependencies": [],
                "product_name": name,
                "product_dir": name,
                "product_prefix": None,
                "product_extension": None
                }
        return target

    def addItem(self, child, target):
        target = str(target)
        head, tail = self.formatPath(child), None
        while True:
            self.printdebug("Adding: "+head+(" (Tail: "+str(tail)+")")*bool(tail))
            if not head or head == os.curdir:
                break
            elif tail is None:
                item = head
                addtos = [self.target_configs[target]["sources"], self.included_files]
            else:
                item = head+os.sep
                addtos = [self.include_dirs, self.library_dirs]
            do = False
            for addto in addtos:
                if item not in addto:
                    addto.append(item)
                    do = True
            if do:
                head, tail = os.path.split(head)
            else:
                self.recursion += 1
                self.printdebug("| Duplicate")
                self.recursion -= 1
                break

    def walk(self, target, root=None):
        if root and target in self.target_configs:
            self.recursion += 1
            self.printdebug("Dependency: "+str(target))
            self.target_configs[root]["dependencies"].append(target)
            self.recursion -= 1
        else:
            if root is None:
                root = self.addTarget(target)
            else:
                self.printdebug("Item: "+str(target))
            self.recursion += 1
            if not os.path.isabs(str(target)) and target.has_builder():
                builder = target.get_builder().get_name(self.env)
                self.printdebug("Builder: "+str(builder))
                bsources = target.get_binfo().bsources
                self.printdebug("Sources:")
                self.recursion += 1
                for child in bsources:
                    self.printdebug("Source: "+str(child))
                    self.recursion += 1
                    self.addItem(child, root)
                    self.walk(child, root)
                    self.recursion -= 1
                self.recursion -= 1
                self.printdebug("Children:")
                self.recursion += 1
                for child in target.children(scan=1):
                    self.printdebug("Child: "+str(child))
                    self.recursion += 1
                    self.addItem(child, root)
                    self.walk(child, root)
                    self.recursion -= 1
                self.recursion -= 1
            self.recursion -= 1

    def printdebug(self, output):
        if self.debug:
            print("  "*self.recursion+str(output))


# Config: ----------------------------------------------------------------------------


def XCProjectConfig(self, variant, targets, env):
    if len(targets) != 1:
        raise ValueError("Exactly one target must be specified")
    return {
        "variant": str(variant),
        "target": targets[0],
        "env": env
        }


class Options(object):
    suffix = ""
    generator_output = ""


def targetConfiguration(include_dirs=None,
                        library_dirs=None,
                        defines=None,
                        mac_framework_dirs=None,
                        debug=None):
    """Wraps targetconfig."""
    return {
        "mac_framework_dirs": mac_framework_dirs or [],
        "include_dirs": include_dirs or [],
        "library_dirs": library_dirs or [],
        "defines": defines or [],
        "xcode_settings": targetconfig(debug=debug)
        }


def targetconfig(debug=None):
    """Assembles The Default Configuration For A Target."""     # This function only implements version 46
    out = {
        "PRODUCT_NAME" : "$(TARGET_NAME)",
        "OTHER_CFLAGS" : "",
        "OTHER_LDFLAGS" : ""
        }
    if debug:
        out.update({
            "DEBUGGING_SYMBOLS" : "YES",
            "GCC_GENERATE_DEBUGGING_SYMBOLS" : "YES",
            "GCC_OPTIMIZATION_LEVEL" : 0
            })
    return out


def projectConfiguration(debug=None):
    """Wraps projectconfig."""
    return {
        "xcode_settings": projectconfig(debug=debug)
        }
    

def projectconfig(debug=None):
    """Assembles The Default Configuration For A Project."""    # This function only implements version 46
    out = {
        "ALWAYS_SEARCH_USER_PATHS" : "NO",
        "CLANG_CXX_LANGUAGE_STANDARD" : "gnu++0x",
        "CLANG_CXX_LIBRARY" : "libc++",
        "CLANG_ENABLE_MODULES" : "YES",
        "CLANG_ENABLE_OBJC_ARC" : "YES",
        "CLANG_WARN_BOOL_CONVERSION" : "YES",
        "CLANG_WARN_CONSTANT_CONVERSION" : "YES",
        "CLANG_WARN_DIRECT_OBJC_ISA_USAGE" : "YES_ERROR",
        "CLANG_WARN_EMPTY_BODY" : "YES",
        "CLANG_WARN_ENUM_CONVERSION" : "YES",
        "CLANG_WARN_INT_CONVERSION" : "YES",
        "CLANG_WARN_OBJC_ROOT_CLASS" : "YES_ERROR",
        "CLANG_WARN__DUPLICATE_METHOD_MATCH" : "YES",
        "COPY_PHASE_STRIP" : "YES",
        "GCC_C_LANGUAGE_STANDARD" : "gnu99",
        "GCC_ENABLE_OBJC_EXCEPTIONS" : "YES",
        "GCC_WARN_64_TO_32_BIT_CONVERSION" : "YES",
        "GCC_WARN_ABOUT_RETURN_TYPE" : "YES_ERROR",
        "GCC_WARN_UNDECLARED_SELECTOR" : "YES",
        "GCC_WARN_UNINITIALIZED_AUTOS" : "YES_AGGRESSIVE",
        "GCC_WARN_UNUSED_FUNCTION" : "YES",
        "GCC_WARN_UNUSED_VARIABLE" : "YES",
        "MACOSX_DEPLOYMENT_TARGET" : "10.9",
        "SDKROOT" : "macosx"
        }
    if debug:
        out.update({
            "GCC_SYMBOLS_PRIVATE_EXTERN" : "NO",
            "GCC_DYNAMIC_NO_PIC" : "NO",
            "GCC_OPTIMIZATION_LEVEL" : 0,
            "GCC_PREPROCESSOR_DEFINITIONS" : [
                "DEBUG:1",
                "$(inherited)"
            ],
            "ONLY_ACTIVE_ARCH" : "YES"
            })
    else:
        out.update({
            "DEBUG_INFORMATION_FORMAT" : "dwarf-with-dsym",
            "ENABLE_NS_ASSERTIONS" : "NO"
            })
    return out
