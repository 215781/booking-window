// Shared data + HTML helpers for the email jobs. Reads the same summary.json the site is built from,
// and the site's own resort list and school-holiday weeks, so email and site always agree.
import { readFileSync } from 'node:fs';
import { ALL, COLLECTIONS } from '../src/lib/resorts.ts';
import { WEEKS } from '../src/lib/weeks.ts';

export const SITE = 'https://whentobook.co.uk';
export const FAMILY = '2A2C';
export const RESORTS = ALL;
export { COLLECTIONS };

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export const money = (n) => (n == null ? '-' : '£' + Math.round(n).toLocaleString('en-GB'));
export function niceDate(iso) { const [y, m, d] = iso.split('-').map(Number); return `${d} ${MONTHS[m - 1]} ${y}`; }
export const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
export const pct = (from, to) => Math.round(((to - from) / from) * 1000) / 10;
export const VERDICT = { rising: 'Rising', falling: 'Easing', steady: 'Steady', new: 'New' };

export function loadSummary(path) {
  const s = JSON.parse(readFileSync(path, 'utf8'));
  if (!s.collections) throw new Error(`${path} is not a summary.json`);
  return s;
}

export function link(path, campaign) {
  const u = new URL(path, SITE);
  u.searchParams.set('utm_source', 'kit');
  u.searchParams.set('utm_medium', 'email');
  u.searchParams.set('utm_campaign', campaign);
  return u.toString();
}
export const resortPath = (r) => `${COLLECTIONS[r.collection].base}${r.slug}/`;

// Family-of-four, 7-night price for every future school-holiday week at every resort with fresh data.
// Rules ("works and true"): only real collected prices; stale resorts are skipped and reported.
export function schoolWeekRows(summary, today) {
  const rows = [], problems = [];
  const slugs = new Set();
  for (const r of RESORTS) {
    if (slugs.has(r.slug)) throw new Error(`duplicate resort slug ${r.slug}`);
    slugs.add(r.slug);
    const rd = summary.collections[r.collection]?.[r.id];
    if (!rd) continue;
    if (rd.stale) { problems.push(`${r.fullName}: skipped, last checked ${rd.updated}`); continue; }
    const deps = rd.parties?.[FAMILY] || [];
    for (const w of WEEKS[COLLECTIONS[r.collection].season]) {
      if (w.to < today) continue;
      const inWeek = deps.filter((d) => d.date >= w.from && d.date <= w.to);
      const d = inWeek.find((x) => x.available) ?? inWeek[0];
      if (!d || !d.available || !d.price) continue;
      rows.push({ key: `${r.collection}/${r.id}/${w.key}/${d.date}`, resort: r, week: w, dep: d, price: d.price, checked: rd.updated, change7: change7(d, rd.updated) });
    }
  }
  return { rows, problems };
}

// Change over roughly the last week, from the weekly history points (null if no point 6-10 days back).
function change7(d, updated) {
  const h = d.history || [];
  if (h.length < 2) return null;
  const now = Date.parse(updated);
  for (let i = h.length - 2; i >= 0; i--) {
    const age = (now - Date.parse(h[i].d)) / 864e5;
    if (age >= 6 && age <= 10) return { from: h[i].p, change: d.price - h[i].p, pct: pct(h[i].p, d.price) };
    if (age > 10) break;
  }
  return null;
}

// Plain HTML that survives email clients. Kit adds the unsubscribe link and postal address footer.
export function layout({ preheader, body, checked }) {
  return `<div style="display:none;max-height:0;overflow:hidden">${esc(preheader)}</div>
<div style="font-family:Inter,Arial,sans-serif;color:#1d2b28;font-size:16px;line-height:1.55;max-width:600px">
${body}
<p style="font-size:13px;color:#5b6663;border-top:1px solid #e3ddd0;padding-top:12px;margin-top:28px">
Prices are for 2 adults and 2 children, 7 nights, as shown on the holiday company's website when we checked on ${esc(niceDate(checked))}. Guidance only: prices change, so always check the price before you book. We don't sell holidays and nothing here is financial advice.<br>
When To Book is run by Connor Martin, trading as When To Book. Reply to this email if anything looks wrong.
</p></div>`;
}

export function table(headers, rows) {
  const th = headers.map((h) => `<th align="left" style="padding:6px 8px;border-bottom:2px solid #1a4a42;font-size:14px">${esc(h)}</th>`).join('');
  const tr = rows.map((cells) => `<tr>${cells.map((c) => `<td style="padding:6px 8px;border-bottom:1px solid #e3ddd0;font-size:14px">${c}</td>`).join('')}</tr>`).join('\n');
  return `<table cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%;margin:8px 0 16px">${`<tr>${th}</tr>`}\n${tr}</table>`;
}

export function button(href, label) {
  return `<p style="margin:20px 0"><a href="${esc(href)}" style="background:#1a4a42;color:#fff;text-decoration:none;padding:12px 20px;border-radius:6px;display:inline-block;font-weight:600">${esc(label)}</a></p>`;
}

// Site rule: never use these words in anything we publish or send.
const BANNED = /\b(deals?|discounts?|cheap(est|er)?|vouchers?|savings?)\b/i;
export function assertClean(text) {
  const m = text.replace(/<[^>]+>/g, ' ').match(BANNED);
  if (m) throw new Error(`banned word in email copy: "${m[0]}"`);
  if (text.includes('—')) throw new Error('em dash in email copy');
}
