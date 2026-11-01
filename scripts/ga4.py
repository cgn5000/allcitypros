"""Google Analytics 4 snippet for AllCityPros pages.

The config script is on every page, but it loads and configures gtag.js only on
the production hostnames (allcitypros.com and www.allcitypros.com). Localhost
and *.vercel.app previews do not request Google. That hostname gate is the
internal-traffic filter; leave it in place.

A second inline script records outbound clicks on every host, including
previews. On production it calls the gtag defined above. If gtag is not
defined yet, it installs the standard dataLayer stub and queues the event
there. Nothing in either script rewrites link hrefs, rel, or targets.

Idempotent stamp of already-generated HTML (run from the repo root):

    python3 scripts/ga4.py
"""
import os
import sys
from multiprocessing import Pool

MARKER = "G-4VYWLM1N6T"
CLICK_MARKER = "acp-outbound-clicks"

# Ends with a newline so it can sit between <head> and the next element.
# Do not change this block: it is the production gate and the GA4 config.
GA4_CONFIG = """\
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

# Separate from the config script so the hostname gate still skips gtag.js
# off production. The listener itself runs everywhere.
CLICK_SNIPPET = """\
  <!-- acp-outbound-clicks -->
  <script>
    (function () {
      var AMAZON = ["amazon.com", "amzn.to"];
      var AFFILIATE = [
        "angi.com", "homeadvisor.com", "thumbtack.com",
        "awin.com", "awin1.com",
        "cj.com", "anrdoezrs.net", "dpbolvw.net", "jdoqocy.com", "kqzyfj.com", "tkqlhce.com", "qksrv.net", "emjcd.com",
        "impact.com", "impactradius.com", "sjv.io", "pxf.io",
        "shareasale.com", "shareasale-analytics.com", "shrsl.com",
        "partnerize.com", "prf.hn"
      ];

      function hostIs(host, root) {
        if (!host) return false;
        host = host.toLowerCase();
        if (host === root) return true;
        var suffix = "." + root;
        return host.length > suffix.length && host.indexOf(suffix, host.length - suffix.length) === host.length - suffix.length;
      }

      function hostIn(host, roots) {
        for (var i = 0; i < roots.length; i++) {
          if (hostIs(host, roots[i])) return true;
        }
        return false;
      }

      function collapse(value) {
        return (value || "").replace(/\\s+/g, " ").trim();
      }

      function placementOf(node) {
        while (node && node !== document) {
          if (node.getAttribute) {
            var value = collapse(node.getAttribute("data-placement"));
            if (value) return value;
          }
          node = node.parentNode;
        }
        return "";
      }

      function markedAffiliate(node) {
        while (node && node !== document) {
          if (node.hasAttribute && node.hasAttribute("data-affiliate")) return true;
          node = node.parentNode;
        }
        return false;
      }

      function relSponsored(anchor) {
        var parts = (anchor.getAttribute("rel") || "").toLowerCase().split(/\\s+/);
        for (var i = 0; i < parts.length; i++) {
          if (parts[i] === "sponsored") return true;
        }
        return false;
      }

      function linkDomain(url) {
        if (url.protocol === "mailto:") {
          var addr = url.pathname || "";
          var at = addr.indexOf("@");
          return at >= 0 ? addr.slice(at + 1).toLowerCase() : "";
        }
        return (url.hostname || "").toLowerCase();
      }

      function send(name, anchor, url) {
        var params = {
          link_url: url.href,
          link_text: collapse(anchor.textContent),
          page_path: location.pathname,
          link_domain: linkDomain(url),
          transport_type: "beacon"
        };
        var placement = placementOf(anchor);
        if (placement) params.placement = placement;
        if (typeof window.gtag !== "function") {
          window.dataLayer = window.dataLayer || [];
          window.gtag = function () { window.dataLayer.push(arguments); };
        }
        window.gtag("event", name, params);
      }

      function classify(anchor) {
        var raw = anchor.getAttribute("href");
        if (!raw) return null;
        var url;
        try {
          url = new URL(raw, location.href);
        } catch (err) {
          return null;
        }
        var proto = url.protocol;
        if (proto === "tel:" || proto === "mailto:") return {name: "contact_click", url: url};
        if (proto !== "http:" && proto !== "https:") return null;
        var host = (url.hostname || "").toLowerCase();
        var here = (location.hostname || "").toLowerCase();
        if (host === here || host === "allcitypros.com" || host === "www.allcitypros.com") return null;
        if (hostIn(host, AMAZON)) return {name: "amazon_click", url: url};
        if (relSponsored(anchor) || markedAffiliate(anchor) || hostIn(host, AFFILIATE)) {
          return {name: "affiliate_click", url: url};
        }
        return null;
      }

      function onPointer(event) {
        if (event.type === "auxclick") {
          if (event.button !== 1) return;
        } else if (event.button !== 0) {
          return;
        }
        var node = event.target;
        if (!node) return;
        if (node.nodeType === 3) node = node.parentNode;
        if (!node || !node.closest) return;
        var anchor = node.closest("a");
        if (!anchor) return;
        var hit = classify(anchor);
        if (!hit) return;
        send(hit.name, anchor, hit.url);
      }

      document.addEventListener("click", onPointer);
      document.addEventListener("auxclick", onPointer);
    })();
  </script>
"""

GA4_SNIPPET = GA4_CONFIG + CLICK_SNIPPET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _insert_at_head(text, snippet):
    if "<head>\n" in text:
        return text.replace("<head>\n", "<head>\n" + snippet, 1)
    if "<head>" in text:
        return text.replace("<head>", "<head>\n" + snippet, 1)
    if "<html>" in text:
        return text.replace("<html>", "<html><head>\n" + snippet + "</head>", 1)
    raise ValueError("no <head> or <html> to attach the analytics snippet")


def _insert_after_config(text, snippet):
    idx = text.find(MARKER)
    end = text.find("</script>", idx)
    if end < 0:
        raise ValueError("measurement id without a closing script tag")
    end += len("</script>")
    if text[end:end + 1] == "\n":
        return text[:end] + "\n" + snippet + text[end + 1:]
    return text[:end] + "\n" + snippet + text[end:]


def inject_html(text):
    """Insert the config and click scripts once. Returns new text or None if unchanged."""
    has_ga = MARKER in text
    has_click = CLICK_MARKER in text
    if has_ga and has_click:
        return None
    if not has_ga and not has_click:
        updated = _insert_at_head(text, GA4_SNIPPET)
    elif not has_ga:
        updated = _insert_at_head(text, GA4_CONFIG)
    else:
        updated = _insert_after_config(text, CLICK_SNIPPET)
    if updated.count(MARKER) != 1:
        raise ValueError("expected the measurement id exactly once")
    if updated.count(CLICK_MARKER) != 1:
        raise ValueError("expected the click tracker exactly once")
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
