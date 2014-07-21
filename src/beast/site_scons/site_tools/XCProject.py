# Info: ----------------------------------------------------------------------------

# Portions of this file Copyright (c) 2012 Google Inc.


"""
A tool for working with .pbxproj files.
Necessary for working with .xcodeproj files.
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
xcodeproj = xcode.xcodeproj_file


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


# Main: ----------------------------------------------------------------------------


def buildProject(target, source, env):
    if len(target) != 1:
        raise ValueError("Unexpected len(target) != 1")
    project_node = str(target[0])
    try:
        configs = env["XCPROJECT_CONFIGS"]
    except KeyError:
        raise ValueError("Could not find XCPROJECT_CONFIGS")
    target_list = xsorted(configs.keys())
    target_dict = {}
    for target in target_list:
        target_dict[target] = {
            "toolset": "target",
            "default_configuration": "Default",
            "configurations": {
                "Default": targetConfiguration(),
                "Release": targetConfiguration(debug=False),
                "Debug": targetConfiguration(debug=True)
                },
            "type": "executable",
            "mac_xctest_bundle": 0,
            "mac_bundle": 0,
            "product_name": None,
            "product_dir": None,
            "product_prefix": None,
            "product_extension": None,
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
        if target in configs:
            target_dict[target].update(configs[target])
    target_dict_list = []
    for target in target_list:
        target_dict_list.append({
            "target_name": target,
            "toolset": None,
            "suppress_wildcard": False,
            "run_as": None
            })
    build_file_dict = {
        "xcode_settings": projectconfig(),
        "configurations": {
            "Default": projectConfiguration(),
            "Debug": projectConfiguration(debug=True),
            "Release": projectConfiguration(debug=False)
            },
        "included_files": [],
        "targets": target_dict_list
        }
    params = {
        "options": Options(configs),
        "generator_flags": {
            "xcode_parallel_builds": True,
            "xcode_serialize_all_test_runs": True,
            "xcode_project_version": None,
            "xcode_list_excluded_files": True,
            "standalone": None,
            "support_target_suffix": " Support"
            }
        }
    xcode.GenerateOutput(target_list, target_dict, os.path.join(os.getcwd(), "Builds", "XCode", "RippleD"), build_file_dict, params)


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


# Config: ----------------------------------------------------------------------------


def XCProjectConfig(self, variant, targets, env):
    items = []
    def _walk(target):
        if not os.path.isabs(str(target)) and target.has_builder():
            builder = target.get_builder().get_name(env)
            bsources = target.get_binfo().bsources
            if builder == "Program":
                for child in bsources:
                    _walk(child)
            else:
                for child in bsources:
                    items.append(str(child))
                    _walk(child)
                for child in target.children(scan=1):
                    if not os.path.isabs(str(child)):
                        items.append(str(child))
                        _walk(child)
    for target in targets:
        _walk(target)
    sources = []
    libraries = []
    dependencies = []
    for item in set(items):
        ext = os.path.splitext(item)[1]
        if ext in ['.c', '.cc', '.cpp']:
            sources.append(item)
        elif ext in ['.h', '.hpp', '.hxx', '.inl', '.inc']:
            libraries.append(item)
        else:
            libraries.append(item)
    return {
        "sources": sources,
        "libraries": libraries,
        "dependencies": []
        }


class Options(object):
    suffix = ""
    generator_output = ""
    def __init__(self, configs):
        pass


def targetConfiguration(defines=None,
                        include_dirs=None,
                        library_dirs=None,
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
