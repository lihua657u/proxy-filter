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
        if not isinstance(p, dict):
            continue
        n = p.get("name")
        if not isinstance(n, str) or not n.strip() or n.strip() == "null":
            n = "NODE-%03d" % (len(proxies) + 1)
            p["name"] = n
        k = key(p)
        if k in seen:
            continue
        seen.add(k)
        while n in names:
            n = n + " #2"
            p["name"] = n
        names.add(n)
        proxies.append(p)
        added += 1
    print(f"{f}: {len(ps)} nodes -> +{added}")

order = [p["name"] for p in proxies] or ["DIRECT"]

out = {
    "mixed-port": 7890,
    "allow-lan": False,
    "mode": "rule",
    "log-level": "info",
    "proxies": proxies,
    "proxy-groups": [
        {"name": "PROXY", "type": "select", "proxies": ["AUTO"] + order},
        {"name": "AUTO", "type": "url-test", "url": "http://www.gstatic.com/generate_204",
         "interval": 300, "tolerance": 50, "proxies": order},
    ],
    "rules": ["MATCH,PROXY"],
}

with open(sys.argv[-1], "w", encoding="utf-8") as fp:
    yaml.safe_dump(out, fp, allow_unicode=True, sort_keys=False)
print(f"TOTAL_UNIQUE {len(proxies)}")
