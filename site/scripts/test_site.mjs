// Site checks run before any deploy. Exit code 1 on any failure.
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';
const DIST = new URL('../dist/', import.meta.url).pathname;
const fails = [], warns = [];
const walk = (d) => readdirSync(d).flatMap((f) => { const p = join(d, f); return statSync(p).isDirectory() ? walk(p) : [p]; });
const files = walk(DIST);
const html = files.filter((f) => f.endsWith('.html'));

// 1. Internal links resolve
for (const f of html) {
  const s = readFileSync(f, 'utf8');
  for (const [, href] of s.matchAll(/href="(\/[^"#?]*)"/g)) {
    const p = join(DIST, href);
    if (!(existsSync(p) && statSync(p).isFile()) && !existsSync(join(p, 'index.html'))) fails.push(`broken link ${href} in ${f.replace(DIST, '')}`);
  }
}
// 2. Banned words (house style) and "Ltd" (sole trader)
for (const f of html) {
  const text = readFileSync(f, 'utf8').replace(/<script[\s\S]*?<\/script>/g, '').replace(/<[^>]+>/g, ' ');
  for (const w of ['deals', 'discounts', 'cheap', 'vouchers', 'savings']) {
    if (new RegExp(`\\b${w}\\b`, 'i').test(text)) (f.includes('/blog/') ? warns : fails).push(`banned word "${w}" in ${f.replace(DIST, '')}`);
  }
  if (/\bLtd\b|Drop Media/.test(text)) fails.push(`"Ltd"/Drop Media in ${f.replace(DIST, '')}`);
}
// 3. No secrets in output
for (const f of files.filter((f) => /\.(html|js|txt|json|xml)$/.test(f))) {
  const s = readFileSync(f, 'utf8');
  if (/kit_[A-Za-z0-9]{10,}|VvMXklLU|QalMFHrJ|api[_-]?secret/i.test(s)) fails.push(`possible secret in ${f.replace(DIST, '')}`);
}
// 4. Resort pages: real price, checked date, valid JSON-LD, signup form, outbound link
const resortPages = html.filter((f) => /\/club-med\/[^/]+\/index\.html$/.test(f));
if (resortPages.length !== 11) fails.push(`expected 11 resort pages, found ${resortPages.length}`);
for (const f of resortPages) {
  const s = readFileSync(f, 'utf8');
  if (!/£\d/.test(s)) fails.push(`no prices on ${f.replace(DIST, '')}`);
  if (!/Checked \d/.test(s)) fails.push(`no checked date on ${f.replace(DIST, '')}`);
  if (!s.includes('data-form="7f784a323c"')) fails.push(`no signup form on ${f.replace(DIST, '')}`);
  for (const [, j] of s.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) { try { JSON.parse(j); } catch { fails.push(`bad JSON-LD on ${f.replace(DIST, '')}`); } }
}
// 5. Data freshness
const summary = JSON.parse(readFileSync(new URL('../src/data/summary.json', import.meta.url), 'utf8'));
for (const p of summary.problems) fails.push(`data: ${p}`);
// 6. Analytics only behind consent: gtag script must not be in the static HTML
for (const f of html) if (/<script[^>]+googletagmanager/.test(readFileSync(f, 'utf8'))) fails.push(`GA loads without consent in ${f.replace(DIST, '')}`);

console.log(`Checked ${html.length} pages.`);
warns.forEach((w) => console.log('WARN', w));
fails.forEach((f) => console.log('FAIL', f));
console.log(fails.length ? `${fails.length} failure(s)` : 'ALL CHECKS PASSED');
process.exit(fails.length ? 1 : 0);
