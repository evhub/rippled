# Info: ----------------------------------------------------------------------------

# Portions of this file Copyright (c) 2012 Google Inc.


"""
A tool for working with .pbxproj files.
Necessary for working with .xcodeproj files.
"""


# Imports: -------------------------------------------------------------------------


from __future__ import with_statement

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
    if x:
        if type(x) is list:
            return x
        else:
            return [x]
    else:
        return []


# Main: ----------------------------------------------------------------------------


class Options(object):
    suffix = ""
    generator_output = ""


def buildProject(target, source, env):
    try:
        config = env["XCPROJECT_CONFIG"]
    except KeyError:
        raise ValueError ("Missing XCPROJECT_CONFIG")
    root_dir = os.getcwd()
    root_dirs = [os.path.abspath(x) for x in makeList(env["XCPROJECT_ROOT_DIRS"])]
    project_node = "".join(list(target))
    xcode.GenerateOutput(project_node, {project_node: {
        "toolset": "target",
        "default_configuration": "Default",
        "configurations": {
            "Default": targetconfig(),
            "Debug": targetconfig(True),
            "Release": targetconfig(False)
            },
        "type": "executable",
        "sources": [source]
        }}, source, {
        "options": Options()
        }, config)


def projectEmitter(target, source, env):
    if len(target) != 1:
        raise ValueError ("Exactly one target must be specified")

    # If source is unspecified this condition will be true
    if not source or source[0] == target[0]:
        source = []

    outputs = []
    for node in list(target):
        path = env.GetBuildPath(node)
        outputs.extend([
            path + '.pbxproj'
            ])
    return outputs, source


projectBuilder = SCons.Builder.Builder(
    action = SCons.Action.Action(buildProject, "Building ${TARGET}"),
    emitter = projectEmitter)


# Config: ----------------------------------------------------------------------------


def targetconfig(debug=False):
    """Assembles The Default Configuration For A Target."""     # This function only implements version 46
    out = {
        "PRODUCT_NAME" : "$(TARGET_NAME)",
        "OTHER_CFLAGS" : "",
        "OTHER_LDFLAGS" : ""
        }
    if debug:
        out.extend({
            "DEBUGGING_SYMBOLS" : "YES",
            "GCC_GENERATE_DEBUGGING_SYMBOLS" : "YES",
            "GCC_OPTIMIZATION_LEVEL" : 0
            })


def projectconfig(debug=False):
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
        out.extend({
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
        out.extend({
            "DEBUG_INFORMATION_FORMAT" : "dwarf-with-dsym",
            "ENABLE_NS_ASSERTIONS" : "NO"
            })
