# Info: ----------------------------------------------------------------------------


"""
A tool for working with old-style NeXT plists.
Necessary for working with .xcodeproj files.
"""


# Imports: -------------------------------------------------------------------------


from __future__ import absolute_import
import hashlib


# Data: ----------------------------------------------------------------------------


def xsorted(*args, **kwargs):
    """Sorts Objects To Insure Deterministic Ordering."""
    if not "key" in kwargs:
        def _key(item):
            if isinstance(item, tuple):
                head, tail = item
                return ("t", _key(head), _key(tail))
            elif isinstance(item, (str, unicode)):
                return ("s", item.upper(), item)
            elif isinstance(item, hexid):
                return ("h", item.comment.text, item.hashout)
            elif isinstance(item, dictelem):
                return ("d", item.atts["isa"], str(len(item.atts)))
            else:
                return (repr(type(item)), item)
        kwargs["key"] = _key
    return sorted(*args, **kwargs)


# Main: ----------------------------------------------------------------------------


class converter(object):
    """Converts Objects Into NeXT plist Format."""
    linesep = "\n"
    recursion = 0

    def addtabs(self, inputstring):
        """Adds Tabbing For Readability."""
        return "    "*self.recursion + inputstring

    def convert(self, inputobject):
        """Converts A Python Object To NeXT plist Format."""

        if isinstance(inputobject, rootelem):
            return inputobject.header() +self.linesep*2+ self.convert(inputobject.atts)     # The double linesep isn't required (one linesep is), but it looks nice

        elif isinstance(inputobject, hexid):
            return self.convert(str(inputobject))

        if isinstance(inputobject, dictelem):
            return self.convert(inputobject.atts)

        elif isinstance(inputobject, (str, unicode)):
            return inputobject

        elif isinstance(inputobject, (int, long)):
            return str(inputobject)

        elif isinstance(inputobject, list):
            out = ["("]
            self.recursion += 1
            for item in xsorted(inputobject):
                out.append(self.addtabs(self.convert(item)) + ",")
            self.recursion -= 1
            out.append(self.addtabs(")"))
            return self.linesep.join(out)

        elif isinstance(inputobject, dict):
            out = ["{"]
            self.recursion += 1
            for k,v in xsorted(inputobject.items()):
                out.append(self.addtabs(self.convert(k)) +" = "+ self.convert(v) +";"+ self.linesep*(self.recursion <= 2))  # This extra linesep isn't required, but it looks nice
            self.recursion -= 1
            out.append(self.addtabs("}"))
            return self.linesep.join(out)

        else:
            raise TypeError("Unable to process plist object "+repr(inputobject))


class hexid(object):
    """A 96-bit Hex ID To Be Used In NeXT plists."""

    def __init__(self, key, text="Generic hexid"):
        """Creates The Hex ID."""
        self.hashout = hashlib.md5(text+" "+key).hexdigest()[:24].upper()
        self.comment = comment(text)

    def __str__(self):
        """Converts To A Python String."""
        out = self.hashout
        if self.comment:
            out += " "+str(self.comment)
        return out

    def __eq__(self, other):
        """Determines Whether Two Hex IDs Are The Same."""
        return self.hashout == other


class comment(object):
    """A Comment To Be Used In NeXT plists."""

    def __init__(self, text):
        """Creates The Comment."""
        self.text = text

    def __str__(self):
        """Converts To A Python String."""
        return "/* " + self.text.replace("*/", "*_/")+ " */"     # Probably not a problem, but best to prevent the file from becoming unreadable in the unlikely case that */ is used


class dictelem(object):
    """A Dictionary Element To Be Used In NeXT plists."""

    def __init__(self, isa):
        """Creates The Dictionary."""
        self.atts = {
            "isa": str(isa)
            }

    def __getitem__(self, k):
        """Gets An Attribute."""
        return self.atts[k]

    def __setitem__(self, k, v):
        """Sets An Attribute."""
        self.atts[k] = v

    def __delitem__(self, k):
        """Deletes An Attribute."""
        del self.atts[k]


# XCode: ---------------------------------------------------------------------------


def targetconfig(debug=False):
    """Assembles The Default Configuration For A Target."""     # This function only implements version 46
    out = {
        "PRODUCT_NAME" : '"$(TARGET_NAME)"',
        "OTHER_CFLAGS" : '""',
        "OTHER_LDFLAGS" : '""'
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
        "CLANG_CXX_LANGUAGE_STANDARD" : '"gnu++0x"',
        "CLANG_CXX_LIBRARY" : '"libc++"',
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
                '"DEBUG:1"',
                '"$(inherited)"'
            ],
            "ONLY_ACTIVE_ARCH" : "YES"
            })
    else:
        out.extend({
            "DEBUG_INFORMATION_FORMAT" : '"dwarf-with-dsym"',
            "ENABLE_NS_ASSERTIONS" : "NO"
            )}


class rootelem(dictelem):
    """The Root Element Of A NeXT plist."""

    def __init__(self,
                 rootObject,
                 objectVersion=46,  # Things that vary between 45 and 46 will be marked
                 encoding="UTF8",
                 archiveVersion=1,
                 classes=None,
                 objects=None):
        """Creates The Root Element."""

        self.encoding = str(encoding)
        self.atts = {
            "archiveVersion": archiveVersion,
            "classes": classes or {},
            "objectVersion": objectVersion,
            "objects": objects or {},
            "rootObject": rootObject
            }

    def __getitem__(self, k):
        """Gets An Object."""
        return self.atts["objects"][k]

    def __setitem__(self, k, v):
        """Sets An Object."""
        self.atts["objects"][k] = v

    def __delitem__(self, k):
        """Deletes An Object."""
        del self.atts["objects"][k]

    def header(self):
        """Gets The Encoding Header."""
        return "// !$*"+self.encoding+"*$!"


class parentelem(dictelem):
    """A Base Class For Parent Objects."""

    def __init__(self, isa, children=None):
        """Creates The Dictionary."""
        self.atts = {
            "isa": str(isa),
            "children": children or []
            }

    def __getitem__(self, k):
        """Gets A Child."""
        return self.atts["children"][k]

    def __setitem__(self, k, v):
        """Sets A Child."""
        self.atts["children"][k] = v

    def append(self, v):
        """Appends A Child."""
        self.atts["children"].append(v)

    def extend(self, v):
        """Extends Children."""
        self.atts["children"].extend(v)


class PBXAggregateTarget(dictelem):
    """An XCode PBXAggregateTarget Object."""   # This class only implements version 45

    def __init__(self,
                 name,
                 buildConfigurationList,
                 dependencies=None,
                 buildPhases=None,
                 productName=None):
        """Creates The PBXAggregateTarget."""

        self.atts = {
            "isa": "PBXAggregateTarget",
            "buildConfigurationList": buildConfigurationList,
            "buildPhases": buildPhases or [],
            "dependencies": dependencies or [],
            "name": name,
            "productName": productName or name
            }


class PBXBuildFile(dictelem):
    """An XCode PBXBuildFile Object."""     # This class only implements version 45

    def __init__(self,
                 fileRef,
                 settings=None):
        """Creates The PBXBuildFile."""

        self.atts = {
            "isa": "PBXBuildFile",
            "fileRef": fileRef
            }
        if settings is not None:
            self.atts["settings"] = settings


class PBXContainerItemProxy(dictelem):
    """An XCode PBXContainerItemProxy Object."""

    def __init__(self,
                 containerPortal,
                 remoteGlobalIDString,
                 remoteInfo,
                 proxyType=2):      # Changed from 1 to 2 in 46
        """Creates The PBXContainerItemProxy."""

        self.atts = {
            "isa": "PBXContainerItemProxy",
            "containerPortal": containerPortal,
            "proxyType": proxyType,
            "remoteGlobalIDString": remoteGlobalIDString,
            "remoteInfo": remoteInfo
            }


class PBXCopyFilesBuildPhase(dictelem):
    """An XCode PBXCopyFilesBuildPhase Object."""   # This class only implements version 45

    def __init__(self,
                 dstPath
                 dstSubfolderSpec,
                 files=None,
                 buildActionMask=2**32-1,
                 runOnlyForDeploymentPostprocessing=0):
        """Creates The PBXCopyFilesBuildPhase."""

        self.atts = {
            "isa": "PBXCopyFilesBuildPhase",
            "buildActionMask": buildActionMask,
            "dstPath": dstPath,
            "dstSubfolderSpec": dstSubfolderSpec,
            "files": files or [],
            "runOnlyForDeploymentPostprocessing": runOnlyForDeploymentPostprocessing
            }


class PBXFileReference(dictelem):
    """An XCode PBXFileReference Object."""

    def __init__(self,
                 path,
                 lastKnownFileType="text",
                 sourceTree="<group>",
                 name=None,     # Only appears in 46
                 fileEncoding=4):
        """Creates The PBXFileReference."""

        self.atts = {
            "isa": "PBXFileReference",
            "fileEncoding": fileEncoding,
            "lastKnownFileType": lastKnownFileType,
            "path": path,
            "sourceTree": '"'+sourceTree+'"'
            }
        if name is not None:
            self.atts[name] = name


class PBXFrameworksBuildPhase(dictelem):
    """An XCode PBXFrameworksBuildPhase Object."""  # This class only implements version 45

    def __init__(self,
                 files=None,
                 buildActionMask=2**32-1,
                 runOnlyForDeploymentPostprocessing=0):
        """Creates The PBXFrameworksBuildPhase."""

        self.atts = {
            "isa": "PBXFrameworksBuildPhase",
            "buildActionMask": buildActionMask,
            "files": files or [],
            "runOnlyForDeploymentPostprocessing": runOnlyForDeploymentPostprocessing
            }


class PBXGroup(parentelem):
    """An XCode PBXGroup Object."""

    def __init__(self,
                 path=None,     # Doesn't appear in 45
                 name=None,     # Only appears in 46
                 sourceTree="<group>",
                 children=None):
        """Creates The PBXGroup."""

        self.atts = {
            "isa": "PBXGroup",
            "children": children or [],
            "sourceTree": '"'+sourceTree+'"'
            }
        if path is not None:
            self.atts["path"] = path
        if name is not None:
            self.atts["name"] = name


class PBXHeadersBuildPhase(dictelem):
    """An XCode PBXHeadersBuildPhase Object."""     # This class only implements version 45

    def __init__(self,
                 files=None,
                 buildActionMask=2**32-1,
                 runOnlyForDeploymentPostprocessing=0):
        """Creates The PBXHeadersBuildPhase."""

        self.atts = {
            "isa": "PBXHeadersBuildPhase",
            "buildActionMask": buildActionMask,
            "files": files or [],
            "runOnlyForDeploymentPostprocessing": runOnlyForDeploymentPostprocessing
            }


class PBXLegacyTarget(dictelem):    # This class should never be used because we should always be generating native targets, not legacy targets
    """An XCode PBXLegacyTarget Object."""      # This class only implements version 46

    def __init__(self,
                 name,
                 buildConfigurationList,
                 buildWorkingDirectory,
                 buildToolPath,
                 buildArgumentsString="",
                 dependencies=None,
                 buildPhases=None,
                 productName=None,
                 passBuildSettingsInEnvironment=1):
        """Creates The PBXLegacyTarget."""

        self.atts = {
            "isa": "PBXLegacyTarget",
            "buildArgumentsString": '"'+buildArgumentsString+'"',
            "buildConfigurationList": buildConfigurationList,
            "buildPhases": buildPhases or [],
            "buildToolPath":buildToolPath,
            "buildWorkingDirectory":buildWorkingDirectory,
            "dependencies": dependencies or [],
            "name": name,
            "passBuildSettingsInEnvironment": passBuildSettingsInEnvironment,
            "productName": productName or name
            }


class PBXNativeTarget(dictelem):
    """An XCode PBXNativeTarget Object."""      # This class only implements version 45

    def __init__(self,
                 name,
                 buildConfigurationList,
                 productInstallPath,
                 productReference,
                 productType,
                 dependencies=None,
                 buildPhases=None,
                 buildRules=None,
                 productName=None):
        """Creates The PBXNativeTarget."""

        self.atts = {
            "isa": "PBXNativeTarget",
            "buildConfigurationList": buildConfigurationList,
            "buildPhases": buildPhases or [],
            "buildRules": buildRules or [],
            "dependencies": dependencies or [],
            "name": name,
            "productInstallPath": productInstallPath,
            "productName": productName or name,
            "productReference": productReference,
            "productType": productType
            }


class PBXProject(dictelem):
    """An XCode PBXProject Object."""

    def __init__(self,
                 targets,
                 mainGroup,
                 ProductGroup,
                 ProjectRef,
                 buildConfigurationList,
                 attributes=None,       # Doesn't appear in 45
                 projectDirPath="",
                 projectRoot="",
                 hasScannedForEncodings=0,
                 compatibilityVersion="XCode 3.2",      # Was XCode 2.4 in 45
                 developmentRegion="English",
                 knownRegions=None):
        """Creates The PBXProject."""

        self.atts = {
            "isa": "PBXProject",
            "buildConfigurationList": buildConfigurationList,
            "compatibilityVersion": '"'+compatibilityVersion+'"',
            "developmentRegion": developmentRegion,
            "hasScannedForEncodings": hasScannedForEncodings,
            "knownRegions": knownRegions or ["en"],
            "mainGroup": mainGroup,
            "projectDirPath": '"'+projectDirPath+'"',
            "projectReferences": [
                {
                    "ProductGroup": ProductGroup,
                    "ProjectRef": ProjectRef
                    }
                ],
            "projectRoot": '"'+projectRoot+'"',
            "targets": targets
            }
        if attributes is not None:
            self.atts["attributes"] = attributes


class PBXReferenceProxy(dictelem):
    """An XCode PBXReferenceProxy Object."""    # This class only appears in 46

    def __init__(self,
                 remoteRef,
                 path,
                 fileType,
                 name=None,
                 sourceTree="BUILT_PRODUCTS_DIR"):
        """Creates The PBXReferenceProxy."""

        self.atts = {
            "isa": "PBXReferenceProxy",
            "fileType": '"'+fileType+'"',
            "path": path,
            "remoteRef": remoteRef,
            "sourceTree": sourceTree
            }
        if name is not None:
            self.atts["name"] = name


class PBXResourcesBuildPhase(dictelem):
    """An XCode PBXResourcesBuildPhase Object."""     # This class only implements version 45

    def __init__(self,
                 files=None,
                 buildActionMask=2**32-1,
                 runOnlyForDeploymentPostprocessing=0):
        """Creates The PBXResourcesBuildPhase."""

        self.atts = {
            "isa": "PBXResourcesBuildPhase",
            "buildActionMask": buildActionMask,
            "files": files or [],
            "runOnlyForDeploymentPostprocessing": runOnlyForDeploymentPostprocessing
            }


class PBXShellScriptBuildPhase(dictelem):
    """An XCode PBXShellScriptBuildPhase Object."""     # This class only implements version 45

    def __init__(self,
                 shellScript,
                 shellPath="/bin/sh",
                 files=None,
                 inputPaths=None,
                 outputPaths=None,
                 buildActionMask=2**32-1,
                 runOnlyForDeploymentPostprocessing=0):
        """Creates The PBXShellScriptBuildPhase."""

        self.atts = {
            "isa": "PBXShellScriptBuildPhase",
            "buildActionMask": buildActionMask,
            "files": files or [],
            "inputPaths": inputPaths or [],
            "outputPaths": outputPaths or [],
            "runOnlyForDeploymentPostprocessing": runOnlyForDeploymentPostprocessing,
            "shellPath": shellPath,
            "shellScript": shellScript
            }


class PBXSourcesBuildPhase(dictelem):
    """An XCode PBXSourcesBuildPhase Object."""     # This class only implements version 45

    def __init__(self,
                 files=None,
                 buildActionMask=2**32-1,
                 runOnlyForDeploymentPostprocessing=0):
        """Creates The PBXSourcesBuildPhase."""

        self.atts = {
            "isa": "PBXSourcesBuildPhase",
            "buildActionMask": buildActionMask,
            "files": files or [],
            "runOnlyForDeploymentPostprocessing": runOnlyForDeploymentPostprocessing
            }


class PBXTargetDependency(dictelem):
    """An XCode PBXTargetDependency Object."""      # This class only implements version 45

    def __init__(self,
                 target,
                 targetProxy):
        """Creates The PBXTargetDependency."""

        self.atts = {
            "isa": "PBXTargetDependency",
            "target": target,
            "targetProxy": targetProxy
            }


class PBXVariantGroup(parentelem):
    """An XCode PBXVariantGroup Object."""      # This class only implements version 45

    def __init__(self,
                 name,
                 sourceTree="",
                 children=None):
        """Creates The PBXVariantGroup."""

    self.atts = {
        "isa": "PBXVariantGroup",
        "children": children or [],
        "name": name,
        "sourceTree": '"'+sourceTree+'"'
        }


class XCBuildConfiguration(dictelem):
    """An XCode XCBuildConfiguration Object."""

    def __init__(self,
                 name,
                 buildSettings=None):
        """Creates The XCBuildConfiguration."""

        self.atts = {
            "isa": "XCBuildConfiguration",
            "buildSettings": buildSettings or {},
            "name": name
            }

    def __getitem__(self, k):
        """Gets A Setting."""
        return self.atts["buildSettings"][k]

    def __setitem__(self, k, v):
        """Sets A Setting."""
        self.atts["buildSettings"][k] = v

    def __delitem__(self, k):
        """Deletes A Setting."""
        del self.atts["buildSettings"][k]


class XCConfigurationList(dictelem):
    """An XCode XCConfigurationList Object."""

    def __init__(self,
                 buildConfigurations,
                 defaultConfigurationName,
                 defaultConfigurationIsVisible=0):
        """Creates The XCConfigurationList."""

        self.atts = {
            "isa": "XCConfigurationList",
            "buildConfigurations": buildConfigurations,
            "defaultConfigurationIsVisible": defaultConfigurationIsVisible,
            "defaultConfigurationName": defaultConfigurationName
            }
