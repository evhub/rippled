# Info: ----------------------------------------------------------------------------

# Portions of this file Copyright (c) 2012 Google Inc.


"""
A tool for generating .xcodeproj files by linking together SCons and gyp.
"""


# Imports: -------------------------------------------------------------------------


from __future__ import with_statement, print_function

import os
import posixpath

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


def itemList(items):
    out = []
    for item in items:
        if isinstance(item, dict):
            for k,v in item.items():
                out.append(str(k)+"="+str(v))
        else:
            out.append(str(item))
    return out


def unQualifyTarget(target):
    return xcode.common.ParseQualifiedTarget(target)[1]


def removeTargetToolset(target):
    build_file, unqualified_target, _ = xcode.common.ParseQualifiedTarget(target)
    return xcode.common.QualifiedTarget(build_file, unqualified_target, None)


def pathList(path, splitter=posixpath):
    out = []
    head, tail = path, None
    while head:
        head, tail = splitter.split(head)
        if tail:
            out = [tail]+out
        else:
            break
    return [head]+out


def convertPath(path, start=os.path, end=posixpath):
    out = pathList(path, start)
    return end.join(*out)


def localPath(path):
    return convertPath(path, posixpath, os.path)


def onlyParents(path, splitter=os.path):
    for dirname in pathList(path, splitter):
        if dirname and dirname != os.pardir:
            return False
    return True


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
    project_node = convertPath(os.path.normpath(str(project_node)))
    build_file_head, build_file_tail = posixpath.split(project_node)
    build_file = posixpath.join(build_file_head, build_file_tail)

    target_configs = ConfigManager(build_file, build_file_head, configs).processConfigs()
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
            "toolset": "target",
            "suppress_wildcard": False,
            "run_as": None
            })
    build_file_dict = {
        "xcode_settings": projectconfig(),
        "configurations": {
            "Debug": projectConfiguration(True),
            "Release": projectConfiguration(False)
            },
        "included_files": [],
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
        self.build_file_head = os.path.abspath(str(build_file_head))
        self.printdebug("Directory: "+self.build_file_head)
        self.configs = configs

    def processConfigs(self):
        self.target_configs = {}
        self.all_files = []
        self.include_dirs = []
        self.library_dirs = []
        self.defines_dict = {}
        self.printdebug("Configs:")
        self.recursion += 1
        debug = None
        release = None
        for config in self.configs:
            self.printdebug("Config: "+str(config))
            if config["variant"] == "debug":
                if debug:
                    raise ValueError("Multiple debug targets found")
                else:
                    debug = config
            elif config["variant"] == "release":
                if release:
                    raise ValueError("Multiple release targets found")
                else:
                    release = config
            else:
                raise ValueError("Unkown variant "+str(config["variant"]))
        self.recursion -= 1
        self.printdebug("Debug:")
        self.recursion += 1
        self.env = debug["env"]
        debug_cflags = xsorted(self.env["CCFLAGS"])
        debug_ldflags = xsorted(self.env["LINKFLAGS"])
        self.update()
        self.walk(debug["target"])
        self.recursion -= 1
        if release is not None:
            self.printdebug("Release:")
            self.recursion += 1
            self.env = release["env"]
            release_cflags = xsorted(self.env["CCFLAGS"])
            release_ldflags = xsorted(self.env["LINKFLAGS"])
            self.walk(self.formatTarget(debug["target"]), self.addTarget(release["target"], "Release"))
            self.recursion -= 1
        else:
            release_cflags = debug_cflags
            release_ldflags = debug_ldflags
        self.printdebug("Extras:")
        self.recursion += 1
        extras = [
            ("/usr/local/bin/",     [self.library_dirs]),
            ("/usr/bin/",           [self.library_dirs]),
            ("/usr/local/include/", [self.include_dirs]),
            ("/usr/include/",       [self.include_dirs]),
            ("/usr/local/lib/",     [self.library_dirs]),
            ("/usr/lib/",           [self.library_dirs])
            ]
        for path, addtos in extras:
            self.addItem(localPath(path), None, addtos)
        self.recursion -= 1
        self.sort()
        for target in self.target_configs:
            self.target_configs[target]["configurations"] = {
                "Release": targetConfiguration(False, release_cflags, release_ldflags, self.include_dirs, self.library_dirs, self.defines_dict[target]),
                "Debug": targetConfiguration(True, debug_cflags, debug_ldflags, self.include_dirs, self.library_dirs, self.defines_dict[target])
                }
        return self.target_configs

    def update(self):
        self.printdebug("Environment:")
        self.recursion += 1
        for include_path in self.env["CPPPATH"]:
            self.addItem(include_path, None, [self.include_dirs])
        for library_path in self.env["LIBPATH"]:
            self.addItem(library_path, None, [self.library_dirs])
        self.recursion -= 1

    def sort(self):
        self.include_dirs = xsorted(self.include_dirs)
        self.library_dirs = xsorted(self.library_dirs)
        for target in self.target_configs:
            self.target_configs[target]["sources"] = xsorted(self.target_configs[target]["sources"])
            self.target_configs[target]["libraries"] = xsorted(self.target_configs[target]["libraries"])
            self.target_configs[target]["dependencies"] = xsorted(self.target_configs[target]["dependencies"])
        for target in self.defines_dict:
            self.defines_dict[target] = xsorted(self.defines_dict[target])

    def formatPath(self, path):
        return convertPath(os.path.relpath(os.path.abspath(str(path)), self.build_file_head))

    def formatTarget(self, target):
        return xcode.common.QualifiedTarget(self.build_file, self.formatPath(target), "target")

    def addTarget(self, target, default_configuration="Debug"):
        name = str(target)
        target = self.formatTarget(target)
        self.printdebug("Target: "+str(target)+" (Name: "+name+")")
        self.recursion += 1
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
        if target not in self.defines_dict:
            self.defines_dict[target] = itemList(self.env["CPPDEFINES"])
        self.printdebug("Libraries:")
        self.recursion += 1
        for lib in self.env["LIBS"]:
            self.addItem(lib, target, False, [self.target_configs[target]["libraries"]])
        self.recursion -= 2
        return target

    def addItem(self, child, target=None, head_addtos=None, tail_addtos=None, depth=2):
        if target is not None:
            target = str(target)
        if tail_addtos is None:
            if head_addtos:
                tail_addtos = head_addtos
            else:
                tail_addtos = False
        if head_addtos is None:
            head_addtos = [self.include_dirs]
        head, tail = self.formatPath(child), None
        while depth and head and head != os.curdir and not onlyParents(head, posixpath):
            self.printdebug("Adding: "+head+(" (Tail: "+str(tail)+")")*bool(tail))
            do = False
            if tail is None:
                if tail_addtos:
                    item = head
                    if item in self.all_files:
                        self.recursion += 1
                        self.printdebug("Duplicate.")
                        self.recursion -= 1
                        break
                    else:
                        addtos = tail_addtos+[self.all_files]
                else:
                    addtos = []
                    do = True
            elif head_addtos:
                item = head+os.sep
                addtos = head_addtos
            else:
                break
            self.printaddtos(addtos, target)
            for addto in addtos:
                if item not in addto:
                    addto.append(item)
                    do = True
            if do:
                head, tail = posixpath.split(head)
            else:
                self.recursion += 1
                self.printdebug("Duplicate.")
                self.recursion -= 1
                break
            depth -= 1

    def printaddtos(self, addtos, target=None):
        out = []
        for addto in addtos:
            if addto is self.all_files:
                out.append("All Files")
            elif addto is self.include_dirs:
                out.append("Include Directories")
            elif addto is self.library_dirs:
                out.append("Library Directories")
            elif target and addto is self.target_configs[target]["sources"]:
                out.append("Sources")
            elif target and addto is self.target_configs[target]["libraries"]:
                out.append("Libraries")
            elif target and addto is self.target_configs[target]["dependencies"]:
                out.append("Dependencies")
            else:
                print("XCProject Warning: Adding to unknown file list "+repr(addto))
                out.append("Unknown")
        self.recursion += 1
        if out:
            self.printdebug("To: "+", ".join(out))
        self.recursion -= 1

    def getBuilder(self, target):
        test = target.get_builder()
        if test is not None:
            return str(test.get_name(self.env))
        else:
            return test

    def walk(self, target, root=None, addtos=False):
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
                builder = self.getBuilder(target)
                self.printdebug("Builder: "+str(builder))
                if builder == "Program":
                    addtos = [self.target_configs[root]["sources"]]
                self.printdebug("Items:")
                self.recursion += 1
                for child in target.get_binfo().bsources:
                    child_builder = self.getBuilder(child)
                    if child_builder == "Object":
                        self.printdebug("Object: "+str(child))
                        self.recursion += 1
                    else:
                        self.printdebug("Source: "+str(child)+(" (Builder: "+str(child_builder)+")")*bool(child_builder))
                        self.recursion += 1
                        self.addItem(child, root, False, addtos)
                    if child_builder:
                        self.walk(child, root, addtos)
                    self.recursion -= 1
                self.recursion -= 1
                self.printdebug("Children:")
                self.recursion += 1
                for child in target.children(scan=1):
                    child_builder = self.getBuilder(child)
                    self.printdebug("Child: "+str(child)+(" (Builder: "+str(child_builder)+")")*bool(child_builder))
                    self.recursion += 1
                    self.addItem(child, root)
                    if child_builder:
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
    generator_output = None


def targetConfiguration(debug=None,
                        cflags="",
                        ldflags="",
                        include_dirs=None,
                        library_dirs=None,
                        defines=None,
                        mac_framework_dirs=None
                        ):
    """Wraps targetconfig."""
    return {
        "mac_framework_dirs": mac_framework_dirs or [],
        "include_dirs": include_dirs or [],
        "library_dirs": library_dirs or [],
        "defines": defines or [],
        "xcode_settings": targetconfig(debug, cflags, ldflags)
        }


def targetconfig(debug=None, cflags="", ldflags=""):
    """Assembles The Default Configuration For A Target."""     # This function only implements version 46
    out = {
        "PRODUCT_NAME" : "$(TARGET_NAME)",
        "OTHER_CFLAGS" : cflags,
        "OTHER_LDFLAGS" : ldflags
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
        "xcode_settings": projectconfig(debug)
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
