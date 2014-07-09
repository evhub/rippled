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
                head_head, head_tail = _key(head)
                tail_head, tail_tail = _key(tail)
                return ("t", head_head, head_tail, tail_head, tail_tail)
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
            return inputobject.header() +self.linesep+ self.convert(dict(inputobject))

        elif isinstance(inputobject, hexid):
            return self.convert(str(inputobject))

        if isinstance(inputobject, dictelem):
            return self.convert(dict(inputobject))

        elif isinstance(inputobject, (str, unicode)):
            return inputobject

        elif isinstance(inputobject, (int, long)):
            return str(inputobject)

        elif isinstance(inputobject, list):
            out = [self.addtabs("(")]
            self.recursion += 1
            for item in xsorted(inputobject):
                out.append(self.addtabs(self.convert(item)) + ",")
            self.recursion -= 1
            out.append(self.addtabs(")"))
            return self.linesep.join(out)

        elif isinstance(inputobject, dict):
            out = [self.addtabs("{")]
            self.recursion += 1
            for k,v in xsorted(inputobject.items()):
                out.append(self.addtabs(self.convert(k)) +" = "+ self.convert(v) +";"+ self.linesep*(self.recursion <= 2))
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
        return "/* " + self.text.replace("*/", "*_/")+ " */"


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

    def __dict__(self):
        """Converts To A Python Dictionary."""
        return self.atts


class rootelem(dictelem):
    """The Root Element Of A NeXT plist."""

    def __init__(self, rootObject, objectVersion=46, encoding="UTF8", archiveVersion=1, classes=None):
        self.encoding = str(encoding)
        self.atts = {
            "archiveVersion": archiveVersion,
            "classes": classes or {},
            "objectVersion": objectVersion,
            "objects": {},
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


class PBXContainerItemProxy(dictelem):
    """An XCode PBXContainerItemProxy Object."""

    def __init__(self, containerPortal, remoteGlobalIDString, remoteInfo, proxyType=2):
        """Creates The PBXContainerItemProxy."""
        self.atts = {
            "isa": "PBXContainerItemProxy",
            "containerPortal": containerPortal,
            "proxyType": proxyType,
            "remoteGlobalIDString": remoteGlobalIDString,
            "remoteInfo": remoteInfo
            }


class PBXFileReference(dictelem):
    """An XCode PBXFileReference Object."""

    def __init__(self, path, lastKnownFileType="text", sourceTree="<group>", fileEncoding=4):
        """Creates The PBXFileReference."""
        self.atts = {
            "isa": "PBXFileReference",
            "fileEncoding": fileEncoding,
            "lastKnownFileType": lastKnownFileType,
            "path": path,
            "sourceTree": '"'+sourceTree+'"'
            }


class PBXGroup(dictelem):
    """An XCode PBXGroup Object."""

    def __init__(self, path=None, sourceTree="<group>"):
        """Creates The PBXGroup."""
        self.atts = {
            "isa": "PBXGroup",
            "children": [],
            "sourceTree": '"'+sourceTree+'"'
            }
        if path is not None:
            self.atts["path"] = path

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


class PBXLegacyTarget(dictelem):
    """An XCode PBXLegacyTarget Object."""

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
    """An XCode PBXNativeTarget Object."""

    def __init__(self):
        """Creates The PBXNativeTarget."""
        self.atts = {
            "isa": "PBXNativeTarget"
            }


class PBXProject(dictelem):
    """An XCode PBXProject Object."""

    def __init__(self,
                 targets,
                 mainGroup,
                 ProductGroup,
                 ProjectRef,
                 buildConfigurationList,
                 ORGANIZATIONNAME,
                 projectDirPath="",
                 projectRoot="",
                 hasScannedForEncodings=0,
                 LastUpgradeCheck=0510,
                 compatibilityVersion="XCode 3.2",
                 developmentRegion="English",
                 knownRegions=None):
        """Creates The PBXProject."""

        self.atts = {
            "isa": "PBXProject",
            "attributes": {
                "LastUpgradeCheck": LastUpgradeCheck,
                "ORGANIZATIONNAME": ORGANIZATIONNAME
                },
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


class PBXReferenceProxy(dictelem):
    """An XCode PBXReferenceProxy Object."""

    def __init__(self, remoteRef, path, fileType, name=None, sourceTree="BUILT_PRODUCTS_DIR"):
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


class XCBuildConfiguration(dictelem):
    """An XCode XCBuildConfiguration Object."""

    def __init__(self, name):
        """Creates The XCBuildConfiguration."""
        self.atts = {
            "isa": "XCBuildConfiguration",
            "buildSettings": {},
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

    def __init__(self, buildConfigurations, defaultConfigurationName, defaultConfigurationIsVisible=0):
        """Creates The XCConfigurationList."""
        self.atts = {
            "isa": "XCConfigurationList",
            "buildConfigurations": buildConfigurations,
            "defaultConfigurationIsVisible": defaultConfigurationIsVisible,
            "defaultConfigurationName": defaultConfigurationName
            }
