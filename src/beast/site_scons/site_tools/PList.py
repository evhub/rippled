"""
A tool for working with old-style NeXT plists.
Necessary for working with .xcodeproj files.
"""

from __future__ import absolute_import
import hashlib

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
                return ("x", item)
        kwargs["key"] = _key
    return sorted(*args, **kwargs)

class converter(object):
    """Converts Objects Into NeXT plist Format."""
    linesep = "\n"
    recursion = 0

    def addtabs(self, inputstring):
        """Adds Tabbing For Readability."""
        return "    "*self.recursion + inputstring

    def convert(self, inputobject):
        """Converts A Python Object To NeXT plist Format."""

        if isinstance(inputobject, rootobject):
            return inputobject.header() +self.linesep+ self.convert(dict(inputobject))

        elif isinstance(inputobject, hexid):
            return self.convert(str(inputobject))

        if isinstance(inputobject, dictelem):
            return self.convert(dict(inputobject))

        elif isinstance(inputobject, (str, unicode)):
            return self.addtabs(inputobject)

        elif isinstance(inputobject, list):
            out = [self.addtabs("(")]
            self.recursion += 1
            for item in xsorted(inputobject):
                out.append(self.convert(item) + ",")
            self.recursion -= 1
            out.append(self.addtabs(")"))
            return self.linesep.join(out)

        elif isinstance(inputobject, dict):
            out = [self.addtabs("{")]
            self.recursion += 1
            for k,v in xsorted(inputobject.items()):
                vs = self.convert(v).split(self.linesep, 1)
                value = vs[0].rstrip()
                if len(vs) > 1:
                    value += self.linesep+vs[1]
                out.append(self.convert(k) + " = " + value + ";" + self.linesep*(self.recursion <= 2))
            self.recursion -= 1
            out.append(self.addtabs("}"))
            return self.linesep.join(out)

        else:
            raise TypeError("Unable to process plist object "+repr(inputobject))

class hexid(object):
    """A 96-bit Hex ID To Be Used In NeXT plists."""
    def __init__(self, text, key):
        """Creates The Hex ID."""
        self.hashout = hashlib.md5(text+key).hexdigest()[:24].upper()
        self.comment = comment(text)
    def __str__(self):
        """Converts To A Python String."""
        out = self.hashout
        if self.comment:
            out += " "+str(self.comment)
        return out

class comment(object):
    """A Comment To Be Used In NeXT plists."""
    def __init__(self, text):
        """Creates The Comment."""
        self.text = text
    def __str__(self):
        """Converts To A Python String."""
        return "/* " + self.text + " */"

class dictelem(object):
    """A Dictionary Element To Be Used In NeXT plists."""
    def __init__(self, isa):
        """Creates The Dictionary."""
        self.atts = {}
        self.atts["isa"] = str(isa)
    def __getitem__(self, k):
        """Gets An Attribute."""
        return self.atts[k]
    def __setitem__(self, k, v):
        """Sets An Attribute."""
        self.atts[k] = v
    def __dict__(self):
        """Converts To A Python Dictionary."""
        return self.atts

class rootobject(dictelem):
    """The Root Element Of A NeXT plist."""
    def __init__(self, key, version=46, encoding="UTF8"):
        self.encoding = str(encoding)
        self.atts = {}
        self.atts["archiveVersion"] = 1
        self.atts["classes"] = {}
        self.atts["objectVersion"] = str(version)
        self.atts["objects"] = {}
        self.atts["rootObject"] = hexid("Project object", key)
    def __getitem__(self, k):
        """Gets An Attribute."""
        return self.atts["objects"][k]
    def __setitem__(self, k, v):
        """Sets An Attribute."""
        self.atts["objects"][k] = v
    def header(self):
        """Gets The Encoding Header."""
        return "// !$*"+self.encoding+"*$!"
