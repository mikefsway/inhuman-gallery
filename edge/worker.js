/*
 * REGISTER - the gallery's record of who came, kept at the edge.
 *
 * GitHub Pages keeps no log, so the gallery cannot tell a machine reader from a
 * human one: the distinction the whole collection is about is the one fact the
 * gallery lacks about itself. This Worker sits in front of the origin, passes
 * every request through untouched, and writes one row per request to Workers
 * Analytics Engine.
 *
 * It runs at the edge, so the page itself is unchanged. No script is added to
 * any page, no cookie is set, and the page makes no outbound request. The
 * colophon's assurance stays true, which it would not if the gallery used a
 * JavaScript analytics beacon.
 *
 * What is written: the class of reader, the user agent, the path, the country,
 * the network, the referer, the method, and the status. What is not written:
 * the IP address, which the gallery does not need and does not want.
 *
 * The classes are the gallery's, not Cloudflare's. A reader either names itself
 * as a crawler, or arrives as a browser, or fetches with a library and names
 * nothing, or is an unfurler rendering the card. The third class is the
 * interesting one: an agent holding a fetch tool looks like a library.
 */

const DECLARED = [
  // Reader that names itself. The list is descriptive, not a policy: nothing
  // here is blocked, and the gallery is for these readers.
  "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
  "GPTBot", "OAI-SearchBot", "ChatGPT-User",
  "PerplexityBot", "Perplexity-User",
  "Googlebot", "Google-Extended", "GoogleOther",
  "bingbot", "BingPreview", "Amazonbot", "Applebot", "Bytespider",
  "CCBot", "cohere-ai", "Diffbot", "DuckDuckBot", "ImagesiftBot",
  "meta-externalagent", "FacebookBot", "YandexBot", "YouBot",
  "Timpibot", "omgili", "Kagibot", "MistralAI-User", "SemrushBot", "AhrefsBot",
];

const UNFURLER = [
  // Reader that renders the card and nothing else.
  "Slackbot", "Twitterbot", "facebookexternalhit", "Discordbot",
  "WhatsApp", "LinkedInBot", "TelegramBot", "Mastodon", "Pleroma",
  "redditbot", "SkypeUriPreview", "Iframely", "Embedly", "Bluesky",
];

const LIBRARY = [
  // Reader that fetches and names no purpose. An agent with a fetch tool
  // usually arrives here.
  "python-requests", "python-httpx", "httpx", "aiohttp", "urllib",
  "curl", "Wget", "node-fetch", "undici", "axios", "Go-http-client",
  "okhttp", "Java/", "libwww-perl", "Scrapy", "PostmanRuntime", "Guzzle",
];

function classify(ua) {
  if (!ua) return "unnamed";
  const has = (list) => list.some((n) => ua.toLowerCase().includes(n.toLowerCase()));
  if (has(DECLARED)) return "declared";
  if (has(UNFURLER)) return "unfurler";
  if (has(LIBRARY)) return "library";
  if (/headless|puppeteer|playwright|phantomjs/i.test(ua)) return "headless";
  if (/Mozilla\/5\.0/.test(ua) && /Gecko|WebKit|Trident/.test(ua)) return "browser";
  return "other";
}

/* The name a reader gives itself, cut to the token that identifies it, so a
 * hundred browser builds do not become a hundred readers. */
function readerName(ua, klass) {
  if (!ua) return "(none)";
  if (klass === "declared" || klass === "unfurler" || klass === "library") {
    for (const n of [...DECLARED, ...UNFURLER, ...LIBRARY]) {
      if (ua.toLowerCase().includes(n.toLowerCase())) return n;
    }
  }
  if (klass === "browser") {
    const m = ua.match(/(Firefox|Edg|OPR|Chrome|Safari)\/[\d.]+/);
    return m ? m[1] : "browser";
  }
  return ua.slice(0, 64);
}

export default {
  async fetch(request, env, ctx) {
    // Pass through to the origin untouched. A subrequest does not re-enter
    // this Worker, so there is no loop.
    const response = await fetch(request);

    if (env.READERS) {
      const url = new URL(request.url);
      const ua = request.headers.get("user-agent") || "";
      const klass = classify(ua);
      const cf = request.cf || {};

      ctx.waitUntil(
        Promise.resolve(
          env.READERS.writeDataPoint({
            indexes: [klass],
            blobs: [
              klass,
              readerName(ua, klass),
              url.pathname,
              cf.country || "??",
              String(cf.asOrganization || "?"),
              request.headers.get("referer") || "",
              request.method,
              request.headers.get("accept") || "",
              ua.slice(0, 512),
            ],
            doubles: [response.status],
          })
        )
      );
    }

    return response;
  },
};
