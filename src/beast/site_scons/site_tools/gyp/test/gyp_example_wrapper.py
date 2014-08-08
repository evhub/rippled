#!/usr/bin/python

from __future__ import with_statement, print_function

def pretty(item):
    if isinstance(item, dict):
        out = ["{"]
        for k,v in item.iteritems():
            out.append(repr(k)+" :")
            for line in pretty(v).splitlines():
                out.append("    "+line)
            out[-1] += ","
        out[-1] = out[-1][:-1]
        out.append("}")
        return "\n    ".join(out)
    elif isinstance(item, list):
        return "[\n    "+ "\n    ".join(",\n".join(map(pretty, item)).splitlines()) +"\n    ]"
    else:
        return repr(item)

import gyp_example
top = gyp_example.GenerateOutputParams

out = {}

out["target_list"] = top.target_list

out["target_dicts"] = top.target_dicts

out["data"] = []
for build_file, build_file_dict in top.data.iteritems():
    out["data"].append({
        "build_file": build_file,
        "build_file_dict": build_file_dict
        })

out["params"] = top.params
if not isinstance(out["params"]["options"], dict):
    out["params"]["options"] = eval("{"+out["params"]["options"].split("{",1)[1].rsplit("}",1)[0]+"}")

keys = "\n".join(out.keys())

build_str = []
for build_dict in out["data"]:
    build_str.append("""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
{

    'build_file' :
        """+ repr(build_file) +""",

    'build_file_dict' :
        """+ "\n        ".join(pretty(build_file_dict).splitlines()) +"""

}
""")
build_str = "\n".join(build_str)

extra_targets = out["target_list"][:]
target_str = []
for target in out["target_dicts"]:
    absent = False
    if target in extra_targets:
        extra_targets.remove(target)
    else:
        absent = True
    target_str.append("""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
{

    'target' :
        """+ repr(target)+","+" # Not in target_list"*absent +"""

    'target_dict' :
        """+ "\n        ".join(pretty(out["target_dicts"][target]).splitlines()) +"""

}
""")
for target in extra_targets:
    target_str.append("""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
{

    'target' :
        """+ repr(target) +""" # Not in target_dicts

}
""")
target_str = "\n".join(target_str)
