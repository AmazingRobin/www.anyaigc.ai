// Block internal files from being served. Cloudflare Pages serves the repo root
// as-is (no build step), so CLAUDE.md, scripts/ and similar files are otherwise
// publicly reachable. _redirects cannot return a 404, so this function does it.
// Everything else falls through to the static file via next().

const BLOCKED_EXACT = new Set(["/tihu", "/tihu.html"]);

function isBlocked(pathname) {
  const path = pathname.toLowerCase();
  if (BLOCKED_EXACT.has(path)) return true;
  if (path.endsWith(".md")) return true;
  if (path === "/scripts" || path.startsWith("/scripts/")) return true;
  if (path === "/.spec-workflow" || path.startsWith("/.spec-workflow/")) return true;
  return false;
}

export function onRequest(context) {
  const { pathname } = new URL(context.request.url);
  if (!isBlocked(pathname)) return context.next();
  return new Response("Not found", {
    status: 404,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "x-robots-tag": "noindex, nofollow",
      "cache-control": "no-store",
    },
  });
}
