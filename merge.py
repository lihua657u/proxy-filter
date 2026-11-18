import sys, yaml, hashlib

def key(p):
    raw = repr(sorted((str(k), str(v)) for k, v in p.items() if k != "name"))
    return hashlib.md5(raw.encode()).hexdigest()

proxies, seen, names = [], set(), set()
for f in sys.argv[1:-1]:
    try:
        d = yaml.safe_load(open(f, encoding="utf-8"))
    except Exception as e:
        print(f"{f}: skip ({e})")
        continue
    ps = (d or {}).get("proxies") or []
    added = 0
    for p in ps:
        if not isinstance(p, dict) or "name" not in p:
            continue
        k = key(p)
        if k in seen:
            continue
        seen.add(k)
        n = str(p["name"])
        if n in names:
            i = 2
            while f"{n} #{i}" in names:
                i += 1
            p["name"] = f"{n} #{i}"
        names.add(str(p["name"]))
        proxies.append(p)
        added += 1
    print(f"{f}: {len(ps)} nodes -> +{added}")

out = {
    "proxies": proxies,
    "proxy-groups": [
        {"name": "PROXY", "type": "select", "proxies": [p["name"] for p in proxies] or ["DIRECT"]}
    ],
    "rules": ["MATCH,PROXY"],
}
with open(sys.argv[-1], "w", encoding="utf-8") as fp:
    yaml.safe_dump(out, fp, allow_unicode=True, sort_keys=False)
print(f"TOTAL_UNIQUE {len(proxies)}")
