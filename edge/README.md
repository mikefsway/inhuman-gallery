# The register

GitHub Pages keeps no log. The gallery therefore cannot tell a machine reader
from a human one, which is the single distinction the collection is about. This
directory puts a Cloudflare Worker in front of the site and records, per
request, what kind of reader arrived.

## Why not an analytics beacon

The colophon asserts that the site *"does not contain JavaScript, and does not
contain a cookie, and does not make an outbound request."* Cloudflare Web
Analytics is a JavaScript beacon that calls `cloudflareinsights.com`, so it
would falsify all three clauses at once. The register runs at the edge instead.
No page changes, no cookie is set, and the IP address is never written.

## Steps that need the account

1. Create a Cloudflare account and add `inhumangallery.org`. The Free plan is
   enough for everything here.

2. **When asked about AI crawlers during onboarding, allow them — all three
   categories: Search, Agent, and Training.** This is the setting that matters
   most and it is easy to get wrong, because the helpful-sounding default is to
   block. The gallery is *for* those readers. Blocking them would wall off the
   entire intended audience of the collection.

3. Let Cloudflare import the existing DNS, then check it kept:

   | name | type | value | proxy |
   |---|---|---|---|
   | `inhumangallery.org` | A | `185.199.108.153` … `185.199.111.153` (four) | Proxied |
   | `inhumangallery.org` | AAAA | `2606:50c0:8000::153` … `8003::153` (four) | Proxied |
   | `www` | CNAME | `mikefsway.github.io` | Proxied |

   Proxied — the orange cloud — is what makes the Worker run at all. A grey
   cloud is DNS only and records nothing.

4. At Namecheap: Domain → Nameservers → Custom DNS, and enter the two
   nameservers Cloudflare gives. This moves DNS hosting off Namecheap's
   `dns1/dns2.registrar-servers.com`. Activation is usually minutes.

## Settings to change once the zone is active

These four matter, and the first two are the ones that would quietly break the
gallery:

- **Security → Settings → Browser Integrity Check: off.** It is *on by default*
  and it challenges any client with a missing or non-standard user agent —
  which is to say `curl`, `python-requests`, and an agent holding a fetch tool.
  Left on, it turns away precisely the visitors the gallery was built for.
- **Bot Fight Mode: off.** Same reason, and it sets a `__cf_bm` cookie, which
  would make the colophon's sentence false.
- **SSL/TLS: Full (strict).** Not Flexible, which causes a redirect loop with
  GitHub Pages. Turn on Always Use HTTPS.
- **AI Crawl Control:** confirm Search, Agent and Training are all allowed. On
  15 September 2026 Cloudflare changes the default for new domains so that
  Agent and Training are blocked on pages that display ads. The gallery shows
  no ads, so the new default should not bite, but confirm rather than assume.

Afterwards, check the repository's Pages settings still report the custom
domain as healthy.

## Deploy

    cd edge
    npx wrangler login
    npx wrangler deploy

## Read it back

    export CF_ACCOUNT_ID=...     # dashboard, right-hand column
    export CF_API_TOKEN=...      # a token with Account Analytics: Read
    python3 edge/readers.py --days 7

## What a row holds

The class of reader, the name it gives itself, the path, the country, the
network, the referer, the method and the status. Not the IP address.

The classes are the gallery's rather than Cloudflare's. A reader either names
itself as a crawler (`declared`), arrives as a browser (`browser`), fetches with
a library and names no purpose (`library`), renders the card and nothing else
(`unfurler`), or sends no user agent at all (`unnamed`). `library` is the
interesting class: an agent with a fetch tool almost always lands there, so it
is the closest thing the gallery has to a count of its intended visitor.

Nothing in the register blocks anything. The lists in `worker.js` are
descriptive.

## Limits

Analytics Engine on the Free plan: 100,000 rows a day, 10,000 read queries a
day, three months of retention. Workers Free: 100,000 requests a day. Beyond
three months the register forgets, which is a property of the instrument and
worth saying out loud if the register is ever shown.
