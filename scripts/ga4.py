"""Google Analytics 4 snippet for AllCityPros pages.

The inline script is on every page, but it loads and configures gtag.js only on
the production hostnames (allcitypros.com and www.allcitypros.com). Localhost
and *.vercel.app previews do not request Google.

Idempotent stamp of already-generated HTML (run from the repo root):

    python3 scripts/ga4.py
"""
import os
import sys
from multiprocessing import Pool

MARKER = "G-4VYWLM1N6T"

# Ends with a newline so it can sit between <head> and the next element.
GA4_SNIPPET = """\
  <!-- Google tag (gtag.js) -->
  <script>
    (function () {
      var h = location.hostname;
      if (h !== "allcitypros.com" && h !== "www.allcitypros.com") return;
      var id = "G-4VYWLM1N6T";
      var s = document.createElement("script");
      s.async = true;
      s.src = "https://www.googletagmanager.com/gtag/js?id=" + id;
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      window.gtag = gtag;
      gtag("js", new Date());
      gtag("config", id);
    })();
  </script>
"""

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def inject_html(text):
    """Insert the snippet once, immediately after <head>. Returns new text or None if unchanged."""
    if MARKER in text:
        return None
    if "<head>\n" in text:
        # Consume the newline already after <head> so the snippet does not add a blank line.
        updated = text.replace("<head>\n", "<head>\n" + GA4_SNIPPET, 1)
    elif "<head>" in text:
        updated = text.replace("<head>", "<head>\n" + GA4_SNIPPET, 1)
    elif "<html>" in text:
        updated = text.replace("<html>", "<html><head>\n" + GA4_SNIPPET + "</head>", 1)
    else:
        raise ValueError("no <head> or <html> to attach the analytics snippet")
    if updated.count(MARKER) != 1:
        raise ValueError("expected the measurement id exactly once")
    return updated


def _stamp(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    updated = inject_html(text)
    if updated is None:
        return "skip"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(updated)
    return "ok"


def main():
    paths = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            if name.endswith(".html"):
                paths.append(os.path.join(dirpath, name))
    with Pool() as pool:
        results = pool.map(_stamp, paths, chunksize=100)
    ok = results.count("ok")
    skip = results.count("skip")
    print(f"stamped {ok}, already present {skip}, of {len(paths)} html files")


if __name__ == "__main__":
    sys.exit(main() or 0)
