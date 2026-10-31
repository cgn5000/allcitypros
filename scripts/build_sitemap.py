"""Build the sitemap index for every public, indexable HTML page.

Run from anywhere:

    python3 scripts/build_sitemap.py

Vercel serves this site with cleanUrls and trailingSlash disabled
(vercel.json). A file is reachable with HTTP 200 only at its extensionless
path and with no trailing slash (the homepage keeps the root slash):

    guides/hvac.html      -> https://allcitypros.com/guides/hvac
    newyork/index.html    -> https://allcitypros.com/newyork
    index.html            -> https://allcitypros.com/
    privacy-policy.html   -> https://allcitypros.com/privacy-policy

Requests for the .html form or a trailing slash 308-redirect, so those forms
are never written into the sitemap. When a page declares a canonical URL it
is used, after the same normalization (apex host, no .html, no trailing
slash). www.allcitypros.com also answers 200 today; canonicals and this
sitemap stay on https://allcitypros.com.

Pages left out:

    noindex / googlebot noindex / X-Robots-Tag noindex
    meta-refresh redirects
    404 documents
    drafts and templates (content/, templates/, drafts/, unreplaced {{ }})
    canonicals that point at a different URL or another host

Privacy and terms are included. Output:

    sitemap.xml                         sitemap index (Search Console URL)
    sitemaps/sitemap-<section>.xml      one file per section
    sitemaps/sitemap-<section>-N.xml    further splits past 50,000 URLs or 50 MB

Sections are pages, guides, city-services, cities, and listings. Empty
sections are omitted. The generators call build() after they write HTML.
"""

import datetime
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, namedtuple
from urllib.parse import urlsplit

DOMAIN = "https://allcitypros.com"
HOST = "allcitypros.com"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
NS = {"sm": SITEMAP_NS}
MAX_URLS = 50_000
MAX_BYTES = 50 * 1024 * 1024  # sitemap protocol limit, 52,428,800 bytes
ROBOTS_LINE = "Sitemap: https://allcitypros.com/sitemap.xml"

# Top-level directories that are not public pages.
DRAFT_ROOTS = {"content", "templates", "drafts"}
NONPUBLIC_ROOTS = {"scripts", "node_modules", "sitemaps"}
SECTION_ORDER = {
    "pages": 0,
    "guides": 1,
    "city-services": 2,
    "cities": 3,
    "listings": 4,
}

Entry = namedtuple("Entry", "loc lastmod priority rel section")

_META_RE = re.compile(r"<meta\b([^>]*)>", re.I | re.S)
_LINK_RE = re.compile(r"<link\b([^>]*)>", re.I | re.S)
_ATTR_RE = re.compile(
    r"""([^\s=/>]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))""",
)
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
_DATE_MOD_RE = re.compile(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})')
_LAST_UPDATED_RE = re.compile(
    r"Last updated:\s*([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})"
)
_MONTHS = {
    name: n
    for n, name in enumerate(
        [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ],
        1,
    )
}

_URLSET_HEAD = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    f'<urlset xmlns="{SITEMAP_NS}">\n'
)
_URLSET_FOOT = "</urlset>\n"


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _attrs(raw):
    out = {}
    for match in _ATTR_RE.finditer(raw):
        value = match.group(2)
        if value is None:
            value = match.group(3)
        if value is None:
            value = match.group(4) or ""
        out[match.group(1).lower()] = value
    return out


def _read_head(path, limit=65536):
    with open(path, "rb") as handle:
        data = handle.read(limit)
    return data.decode("utf-8", "replace")


def _head(text):
    end = text.lower().find("</head>")
    return text if end < 0 else text[:end]


def public_path(rel):
    """URL path Vercel serves with HTTP 200 for this HTML file."""
    rel = rel.replace("\\", "/").lstrip("/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        parent = rel[: -len("/index.html")]
        return "/" + parent if parent else "/"
    if rel.endswith(".html"):
        rel = rel[: -len(".html")]
    return "/" + rel if rel else "/"


def normalize_path(path):
    path = path.split("?", 1)[0].split("#", 1)[0]
    if not path.startswith("/"):
        path = "/" + path
    while "//" in path:
        path = path.replace("//", "/")
    if path.lower().endswith(".html"):
        path = path[:-5]
    if path.lower().endswith("/index"):
        path = path[:-6] or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return path or "/"


def canonical_target(href):
    """Return ('path', normalized_path) or ('offsite', None)."""
    href = href.strip()
    if href.startswith("//"):
        href = "https:" + href
    if href.startswith("http://") or href.startswith("https://"):
        parts = urlsplit(href)
        host = (parts.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        if host != HOST:
            return "offsite", None
        return "path", normalize_path(parts.path or "/")
    if href.startswith("/"):
        return "path", normalize_path(href)
    return "path", normalize_path("/" + href)


def _robots_blocks(content):
    tokens = [tok for tok in re.split(r"[\s,]+", content.lower()) if tok]
    return "noindex" in tokens or "none" in tokens


def _meta_flags(head):
    noindex = False
    refresh = False
    canonical = None  # ('path', path) | ('offsite', None) | None
    for match in _META_RE.finditer(head):
        attrs = _attrs(match.group(1))
        name = attrs.get("name", "").lower()
        equiv = attrs.get("http-equiv", "").lower()
        content = attrs.get("content", "")
        if name in {"robots", "googlebot"} or equiv == "x-robots-tag":
            if _robots_blocks(content):
                noindex = True
        if equiv == "refresh":
            refresh = True
    for match in _LINK_RE.finditer(head):
        attrs = _attrs(match.group(1))
        rels = {tok for tok in re.split(r"[\s,]+", attrs.get("rel", "").lower()) if tok}
        if "canonical" in rels and attrs.get("href") and canonical is None:
            canonical = canonical_target(attrs["href"])
    return noindex, refresh, canonical


def _title(head):
    match = _TITLE_RE.search(head)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def _is_404_title(title):
    folded = title.lower()
    if folded in {"404", "404 not found", "page not found", "not found", "error 404"}:
        return True
    if folded.startswith(("404 ", "404:", "404-", "404|")):
        return True
    if "page not found" in folded and len(folded) < 80:
        return True
    return False


def _lastmod(text, path):
    match = _DATE_MOD_RE.search(text)
    if match:
        try:
            return datetime.date.fromisoformat(match.group(1))
        except ValueError:
            pass
    match = _LAST_UPDATED_RE.search(text)
    if match:
        month = _MONTHS.get(match.group(1))
        if month:
            try:
                return datetime.date(int(match.group(3)), month, int(match.group(2)))
            except ValueError:
                pass
    stamp = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(stamp, datetime.timezone.utc).date()


def _priority(section, url_path):
    if url_path == "/":
        return "1.0"
    if url_path in {"/privacy-policy", "/terms-of-service"}:
        return "0.3"
    if section == "guides":
        return "0.9"
    if section == "cities":
        return "0.6"
    if section == "city-services":
        return "0.7"
    if section == "listings":
        return "0.5"
    return "0.5"


def discover_cities(root):
    cities = []
    skip = DRAFT_ROOTS | NONPUBLIC_ROOTS | {"guides"}
    for name in os.listdir(root):
        if name.startswith(".") or name in skip:
            continue
        if os.path.isdir(os.path.join(root, name)):
            cities.append(name)
    cities.sort(key=len, reverse=True)
    return cities


def section_for(rel, cities, cities_by_len):
    parts = rel.split("/")
    if parts[0] == "guides":
        stem = parts[1] if len(parts) > 1 else ""
        if stem.endswith(".html"):
            stem = stem[:-5]
        if stem and stem != "index":
            for city in cities_by_len:
                if stem.startswith(city + "-"):
                    return "city-services"
        return "guides"
    if len(parts) == 2 and parts[1] == "index.html" and parts[0] in cities:
        return "cities"
    if parts[0] in set(cities):
        return "listings"
    return "pages"


def _skip_reason_for_path(rel):
    parts = rel.split("/")
    if any(part.startswith(".") for part in parts):
        return "hidden"
    name = parts[-1]
    if name.lower() in {"404.html", "not-found.html"} or rel.lower() in {"404.html", "404/index.html"}:
        return "not_found"
    if any(part.lower() in {"draft", "drafts"} for part in parts) or "draft" in name.lower():
        return "draft"
    if len(parts) > 1 and parts[0] in DRAFT_ROOTS:
        return "draft"
    if len(parts) > 1 and parts[0] in NONPUBLIC_ROOTS:
        return "nonpublic"
    return None


def inspect_file(root, rel, cities, cities_by_len):
    reason = _skip_reason_for_path(rel)
    if reason:
        return None, reason
    path = os.path.join(root, rel.replace("/", os.sep))
    text = _read_head(path)
    if "<html" not in text.lower():
        return None, "empty"
    head = _head(text)
    if "{{" in _title(head):
        return None, "draft"
    noindex, refresh, canonical = _meta_flags(head)
    if noindex:
        return None, "noindex"
    if refresh:
        return None, "redirect"
    if _is_404_title(_title(head)):
        return None, "not_found"
    served = public_path(rel)
    if canonical is not None:
        kind, canon_path = canonical
        if kind == "offsite":
            return None, "canonical_offsite"
        if canon_path != served:
            return None, "canonical_mismatch"
        url_path = canon_path
    else:
        url_path = served
    section = section_for(rel, cities, cities_by_len)
    entry = Entry(
        loc=DOMAIN + url_path,
        lastmod=_lastmod(text, path),
        priority=_priority(section, url_path),
        rel=rel,
        section=section,
    )
    return entry, None


def _prefer(new_rel, old_rel):
    """Choose which file owns a URL when two files normalize to the same loc."""
    def rank(rel):
        indexish = 0 if rel == "index.html" or rel.endswith("/index.html") else 1
        return (indexish, rel.count("/"), len(rel))
    return rank(new_rel) < rank(old_rel)


def collect(root):
    root = os.path.abspath(root)
    cities = discover_cities(root)
    city_set = set(cities)
    cities_by_len = cities  # already longest-first
    chosen = {}
    skipped = Counter()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if not name.startswith(".")]
        for filename in filenames:
            if not filename.endswith(".html"):
                continue
            path = os.path.join(dirpath, filename)
            rel = os.path.relpath(path, root).replace("\\", "/")
            entry, reason = inspect_file(root, rel, city_set, cities_by_len)
            if entry is None:
                skipped[reason] += 1
                continue
            previous = chosen.get(entry.loc)
            if previous is None:
                chosen[entry.loc] = entry
            elif _prefer(entry.rel, previous.rel):
                skipped["duplicate"] += 1
                chosen[entry.loc] = entry
            else:
                skipped["duplicate"] += 1
    entries = sorted(
        chosen.values(),
        key=lambda entry: (SECTION_ORDER.get(entry.section, 50), entry.section, entry.loc),
    )
    return entries, skipped


def _url_line(entry):
    loc = html.escape(entry.loc, quote=False)
    return (
        f"  <url><loc>{loc}</loc><lastmod>{entry.lastmod.isoformat()}</lastmod>"
        f"<priority>{entry.priority}</priority></url>\n"
    )


def chunk_entries(entries, max_urls, max_bytes):
    chunks = []
    current = []
    overhead = len(_URLSET_HEAD.encode("utf-8")) + len(_URLSET_FOOT.encode("utf-8"))
    size = overhead
    for entry in entries:
        line = _url_line(entry)
        nbytes = len(line.encode("utf-8"))
        if nbytes + overhead > max_bytes:
            raise SystemExit(f"single URL exceeds the sitemap byte limit: {entry.loc}")
        if current and (len(current) >= max_urls or size + nbytes > max_bytes):
            chunks.append(current)
            current = []
            size = overhead
        current.append(entry)
        size += nbytes
    if current:
        chunks.append(current)
    return chunks


def _render_urlset(entries):
    parts = [_URLSET_HEAD]
    parts.extend(_url_line(entry) for entry in entries)
    parts.append(_URLSET_FOOT)
    return "".join(parts)


def _render_index(files):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<sitemapindex xmlns="{SITEMAP_NS}">',
    ]
    for rel, _count, lastmod in files:
        loc = html.escape(f"{DOMAIN}/{rel}", quote=False)
        lines.append(
            f"  <sitemap><loc>{loc}</loc><lastmod>{lastmod.isoformat()}</lastmod></sitemap>"
        )
    lines.append("</sitemapindex>")
    return "\n".join(lines) + "\n"


def write_sitemaps(root, entries, max_urls=MAX_URLS, max_bytes=MAX_BYTES):
    root = os.path.abspath(root)
    os.makedirs(os.path.join(root, "sitemaps"), exist_ok=True)
    written = []
    keep = set()
    grouped = {}
    for entry in entries:
        grouped.setdefault(entry.section, []).append(entry)
    sections = sorted(grouped, key=lambda name: (SECTION_ORDER.get(name, 50), name))
    for section in sections:
        chunks = chunk_entries(grouped[section], max_urls, max_bytes)
        numbered = len(chunks) > 1
        for index, chunk in enumerate(chunks, 1):
            filename = f"sitemap-{section}-{index}.xml" if numbered else f"sitemap-{section}.xml"
            body = _render_urlset(chunk)
            path = os.path.join(root, "sitemaps", filename)
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(body)
            keep.add(filename)
            written.append((f"sitemaps/{filename}", len(chunk), max(entry.lastmod for entry in chunk)))
    index_path = os.path.join(root, "sitemap.xml")
    with open(index_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(_render_index(written))
    sitemap_dir = os.path.join(root, "sitemaps")
    for filename in os.listdir(sitemap_dir):
        if filename.startswith("sitemap-") and filename.endswith(".xml") and filename not in keep:
            os.remove(os.path.join(sitemap_dir, filename))
    return written


def ensure_robots(root):
    path = os.path.join(root, "robots.txt")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("User-agent: *\nAllow: /\n" + ROBOTS_LINE + "\n")
        return
    original = open(path, encoding="utf-8").read()
    lines = original.splitlines()
    indexes = [i for i, line in enumerate(lines) if line.lower().startswith("sitemap:")]
    if indexes and len(indexes) == 1 and lines[indexes[0]].strip() == ROBOTS_LINE:
        return
    if indexes:
        lines[indexes[0]] = ROBOTS_LINE
        for index in reversed(indexes[1:]):
            del lines[index]
    else:
        lines.append(ROBOTS_LINE)
    updated = "\n".join(lines) + "\n"
    if updated != original:
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(updated)


def _loc_path(loc):
    if not loc.startswith(DOMAIN):
        raise AssertionError(f"loc is not on {DOMAIN}: {loc}")
    return loc[len(DOMAIN):] or "/"


def validate(root, entries):
    """Raise AssertionError when the written sitemap does not match entries."""
    index_path = os.path.join(root, "sitemap.xml")
    index = ET.parse(index_path)
    if index.getroot().tag != f"{{{SITEMAP_NS}}}sitemapindex":
        raise AssertionError("sitemap.xml must be a sitemap index")
    found = []
    children = index.findall("sm:sitemap", NS)
    seen_files = set()
    for child in children:
        loc = child.find("sm:loc", NS).text
        lastmod = child.find("sm:lastmod", NS).text
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod or ""):
            raise AssertionError(f"bad sitemap lastmod: {lastmod}")
        prefix = DOMAIN + "/sitemaps/"
        if not loc or not loc.startswith(prefix):
            raise AssertionError(f"bad child sitemap loc: {loc}")
        rel = loc[len(DOMAIN) + 1:]
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            raise AssertionError(f"missing child sitemap {rel}")
        size = os.path.getsize(path)
        if size > MAX_BYTES:
            raise AssertionError(f"{rel} is {size} bytes")
        seen_files.add(rel)
        tree = ET.parse(path)
        if tree.getroot().tag != f"{{{SITEMAP_NS}}}urlset":
            raise AssertionError(f"{rel} is not a urlset")
        urls = tree.findall("sm:url", NS)
        if not urls or len(urls) > MAX_URLS:
            raise AssertionError(f"{rel} has {len(urls)} URLs")
        child_dates = []
        for node in urls:
            url = node.find("sm:loc", NS).text
            modified = node.find("sm:lastmod", NS).text
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", modified or ""):
                raise AssertionError(f"bad lastmod for {url}")
            path_part = _loc_path(url)
            if path_part != "/" and (path_part.endswith("/") or path_part.endswith(".html")):
                raise AssertionError(f"loc would redirect: {url}")
            if url.startswith("https://www."):
                raise AssertionError(f"loc uses www: {url}")
            found.append(url)
            child_dates.append(modified)
        if lastmod != max(child_dates):
            raise AssertionError(f"{rel} index lastmod {lastmod} != {max(child_dates)}")
    if len(found) != len(set(found)):
        raise AssertionError("duplicate locs in sitemap")
    expected = {entry.loc for entry in entries}
    if set(found) != expected:
        missing = sorted(expected - set(found))[:5]
        extra = sorted(set(found) - expected)[:5]
        raise AssertionError(f"sitemap locs diverged; missing {missing} extra {extra}")
    for entry in entries:
        file_path = os.path.join(root, entry.rel.replace("/", os.sep))
        if not os.path.isfile(file_path):
            raise AssertionError(f"{entry.loc} maps to missing file {entry.rel}")
        if public_path(entry.rel) != _loc_path(entry.loc):
            raise AssertionError(f"{entry.loc} does not match {entry.rel}")
    robots = open(os.path.join(root, "robots.txt"), encoding="utf-8").read()
    if ROBOTS_LINE not in robots.splitlines():
        raise AssertionError("robots.txt is missing the sitemap line")
    return seen_files


def build(root=None, max_urls=MAX_URLS, max_bytes=MAX_BYTES):
    root = os.path.abspath(root or repo_root())
    entries, skipped = collect(root)
    written = write_sitemaps(root, entries, max_urls=max_urls, max_bytes=max_bytes)
    ensure_robots(root)
    validate(root, entries)
    return {
        "url_count": len(entries),
        "files": [(rel, count) for rel, count, _last in written],
        "skipped": dict(skipped),
    }


def _write_html(root, rel, body):
    path = os.path.join(root, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(body)


def _self_test():
    import tempfile

    page = (
        "<!DOCTYPE html><html><head><title>{title}</title>"
        "{extra}</head><body><p>Last updated: June 28, 2026</p></body></html>\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        _write_html(tmp, "index.html", page.format(
            title="Home",
            extra='<link rel="canonical" href="https://www.allcitypros.com/">',
        ))
        _write_html(tmp, "privacy-policy.html", page.format(
            title="Privacy",
            extra='<link rel="canonical" href="https://allcitypros.com/privacy-policy.html">',
        ))
        _write_html(tmp, "guides/hvac.html", page.format(
            title="HVAC",
            extra=(
                '<link rel="canonical" href="https://allcitypros.com/guides/hvac/">'
                '<script type="application/ld+json">{"dateModified":"2026-10-17"}</script>'
            ),
        ))
        _write_html(tmp, "guides/newyork-hvac.html", page.format(
            title="NY HVAC",
            extra='<meta name="robots" content="noindex, follow">',
        ))
        _write_html(tmp, "newyork/index.html", page.format(
            title="New York",
            extra='<link rel="canonical" href="https://allcitypros.com/newyork/">',
        ))
        _write_html(tmp, "newyork/biz.html", page.format(
            title="Biz",
            extra='<meta content="noindex" name="googlebot">',
        ))
        _write_html(tmp, "404.html", page.format(title="404 Not Found", extra=""))
        _write_html(tmp, "gone.html", page.format(
            title="Gone",
            extra='<meta http-equiv="refresh" content="0;url=/">',
        ))
        _write_html(tmp, "content/tampa/index.html", page.format(title="Soon", extra=""))
        _write_html(tmp, "templates/entity.html", page.format(title="{{Name}}", extra=""))
        _write_html(tmp, "elsewhere.html", page.format(
            title="Off",
            extra='<link rel="canonical" href="https://example.com/elsewhere">',
        ))
        for name in ("a", "b", "c"):
            _write_html(tmp, f"{name}.html", page.format(
                title=name,
                extra=f'<link rel="canonical" href="https://allcitypros.com/{name}">',
            ))
        os.utime(os.path.join(tmp, "index.html"), (1_700_000_000, 1_700_000_000))

        entries, skipped = collect(tmp)
        locs = {entry.loc: entry for entry in entries}
        expect = {
            "https://allcitypros.com/",
            "https://allcitypros.com/a",
            "https://allcitypros.com/b",
            "https://allcitypros.com/c",
            "https://allcitypros.com/privacy-policy",
            "https://allcitypros.com/guides/hvac",
            "https://allcitypros.com/newyork",
        }
        if set(locs) != expect:
            raise SystemExit(f"self-test locs {sorted(locs)} != {sorted(expect)}")
        if locs["https://allcitypros.com/guides/hvac"].lastmod.isoformat() != "2026-10-17":
            raise SystemExit("dateModified was not used")
        if locs["https://allcitypros.com/privacy-policy"].lastmod.isoformat() != "2026-06-28":
            raise SystemExit("Last updated was not used")
        if locs["https://allcitypros.com/guides/hvac"].section != "guides":
            raise SystemExit("service hub section")
        if locs["https://allcitypros.com/newyork"].section != "cities":
            raise SystemExit("city section")
        for reason in ("noindex", "not_found", "redirect", "draft", "canonical_offsite"):
            if skipped[reason] < 1:
                raise SystemExit(f"expected skip {reason}, got {skipped}")

        # Force a split so the 50,000-URL path is exercised.
        info = build(tmp, max_urls=2, max_bytes=MAX_BYTES)
        if info["url_count"] != 7:
            raise SystemExit(f"unexpected count {info}")
        names = [name for name, _count in info["files"]]
        if names != [
            "sitemaps/sitemap-pages-1.xml",
            "sitemaps/sitemap-pages-2.xml",
            "sitemaps/sitemap-pages-3.xml",
            "sitemaps/sitemap-guides.xml",
            "sitemaps/sitemap-cities.xml",
        ]:
            raise SystemExit(f"unexpected files {names}")
        counts = [count for _name, count in info["files"]]
        if counts != [2, 2, 1, 1, 1]:
            raise SystemExit(f"unexpected chunk sizes {counts}")
        validate(tmp, collect(tmp)[0])

        # Byte cap splits before the URL cap. One URL is ~210 bytes with the wrapper.
        tiny = build(tmp, max_urls=50, max_bytes=250)
        if sum(count for _name, count in tiny["files"]) != 7:
            raise SystemExit(f"byte split dropped URLs: {tiny}")
        if any(count != 1 for _name, count in tiny["files"]):
            raise SystemExit(f"byte split did not isolate URLs: {tiny}")
    print("self-test ok")


def main(argv):
    if "--self-test" in argv:
        _self_test()
        return
    info = build()
    print(f"sitemap: {info['url_count']} indexable URLs")
    for name, count in info["files"]:
        print(f"  {name}: {count}")
    if info["skipped"]:
        summary = ", ".join(f"{key}={value}" for key, value in sorted(info["skipped"].items()))
        print(f"skipped: {summary}")


if __name__ == "__main__":
    main(sys.argv[1:])
