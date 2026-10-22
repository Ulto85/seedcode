"""Merge Duplicate Candidate Profiles.

Normalise every identifier, map each one to the first profile that used it, and union profiles that share
an identifier. Time O(L log L) where L is the total number of identifiers (the log is from sorting the output),
space O(L)."""

GMAIL_DOMAINS = {"gmail.com", "googlemail.com"}


def norm_email(raw, normalize_gmail):
    e = raw.strip().lower()
    if e.count("@") != 1:
        return None
    local, domain = e.split("@")
    if normalize_gmail and domain in GMAIL_DOMAINS:
        local = local.split("+", 1)[0].replace(".", "")
        domain = "gmail.com"
    if not local or not domain:
        return None
    return local + "@" + domain


def norm_phone(raw):
    d = "".join(ch for ch in raw if ch.isdigit())
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    return d if len(d) == 10 else None


def merge_profiles(profiles, normalize_gmail=False):
    n = len(profiles)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    owner = {}                         # ("e"|"p", value) -> first profile index
    keys = []
    for i, p in enumerate(profiles):
        mine = set()
        for raw in p.get("emails", []):
            e = norm_email(raw, normalize_gmail)
            if e:
                mine.add(("e", e))
        for raw in p.get("phones", []):
            ph = norm_phone(raw)
            if ph:
                mine.add(("p", ph))
        keys.append(mine)
        for k in mine:
            if k in owner:
                a, b = find(i), find(owner[k])
                if a != b:
                    parent[a] = b
            else:
                owner[k] = i

    groups = {}
    for i in range(n):
        g = groups.setdefault(find(i), {"ids": [], "emails": set(), "phones": set()})
        g["ids"].append(profiles[i]["id"])
        for kind, v in keys[i]:
            g["emails" if kind == "e" else "phones"].add(v)
    out = [{"ids": sorted(g["ids"]), "emails": sorted(g["emails"]), "phones": sorted(g["phones"])}
           for g in groups.values()]
    out.sort(key=lambda g: g["ids"][0])
    return out
