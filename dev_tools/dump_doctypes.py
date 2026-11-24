"""Print every DocType in an app with a compact field list. Usage: python3 dump_doctypes.py <app_package_dir>"""
import glob
import json
import os
import sys

root = sys.argv[1]
for p in sorted(glob.glob(os.path.join(root, "*", "doctype", "*", "*.json"))):
    if os.path.basename(os.path.dirname(p)) + ".json" != os.path.basename(p):
        continue
    d = json.load(open(p))
    fs = [f for f in d["fields"] if f["fieldtype"] not in ("Section Break", "Column Break", "Tab Break", "HTML")]
    out = []
    for f in fs:
        t, o, x = f["fieldtype"], (f.get("options") or ""), f["fieldname"]
        if t in ("Link", "Table", "Table MultiSelect", "Dynamic Link"):
            x += "->" + o
        elif t == "Select":
            x += "[" + o.replace("\n", "|")[:70] + "]"
        else:
            x += ":" + t
        if f.get("reqd"):
            x += "*"
        if f.get("read_only"):
            x += "(ro)"
        out.append(x)
    kind = "child" if d.get("istable") else (d.get("autoname") or "")
    sub = " submittable" if d.get("is_submittable") else ""
    print(f"## {d['name']} [{kind}{sub}] {len(fs)} fields")
    print("  " + ", ".join(out))
