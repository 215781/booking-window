// Price-move alerts. For each resort, compares today's family price for every school-holiday week
// with the price when we last told that resort's watchers (the "baseline"). When a week has moved
// by at least ALERT_PCT and ALERT_MIN_GBP, watchers (Kit tag watch-<slug>) get one email listing
// every week that moved. ALERT_MODE=draft (default) creates Kit drafts for the owner to check;
// ALERT_MODE=send schedules them to go out 15 minutes later.
import { COLLECTIONS, VERDICT, assertClean, button, esc, layout, link, money, niceDate, pct, resortPath, schoolWeekRows, table } from './content.mjs';
import { ensureTags, watchTag } from './sync.mjs';

const ALERT_PCT = Number(process.env.ALERT_PCT || 5);
const ALERT_MIN_GBP = Number(process.env.ALERT_MIN_GBP || 150);
const REVIEW_PCT = 40;     // bigger jumps are held for a human check, never sent automatically
const COOLDOWN_DAYS = 7;   // at most one alert per resort per week

export function findMoves(rows, state, today) {
  const baselines = state.baselines || {};
  const next = {}, moves = [], held = [];
  for (const row of rows) {
    const b = baselines[row.key];
    if (!b) { next[row.key] = { price: row.price, since: row.checked }; continue; }
    next[row.key] = b;
    const change = row.price - b.price, p = pct(b.price, row.price);
    if (Math.abs(p) > REVIEW_PCT) { held.push({ ...row, from: b, change, pct: p }); continue; }
    if (Math.abs(p) >= ALERT_PCT && Math.abs(change) >= ALERT_MIN_GBP) moves.push({ ...row, from: b, change, pct: p });
  }
  const byResort = new Map();
  for (const m of moves) {
    const last = state.lastAlert?.[m.resort.slug];
    if (last && (Date.parse(today) - Date.parse(last)) / 864e5 < COOLDOWN_DAYS) continue;
    if (!byResort.has(m.resort.slug)) byResort.set(m.resort.slug, []);
    byResort.get(m.resort.slug).push(m);
  }
  return { next, byResort, held };
}

export function buildAlert(moves, today) {
  const r = moves[0].resort;
  const checked = moves.map((m) => m.checked).sort().at(-1);
  const campaign = `alert-${r.slug}-${today}`;
  const upCount = moves.filter((m) => m.change > 0).length;
  const one = moves.length === 1 ? moves[0] : null;
  const subject = one
    ? `${r.name}: ${one.week.label} is ${one.change > 0 ? 'up' : 'down'} ${money(Math.abs(one.change))}`
    : `${r.name}: ${moves.length} school-holiday weeks have moved`;
  const verdictLine = upCount === moves.length
    ? "Prices are climbing. If one of these is your week, don't leave it too long."
    : upCount === 0 ? 'Prices have come down. Worth a look now, they may not stay here.'
    : 'Some weeks are up and some are down. Check your week below.';
  const body = `<h1 style="font-family:Georgia,serif;font-size:24px;color:#1a4a42;margin:0 0 8px">${esc(r.fullName)}: prices have moved</h1>
<p>You asked us to watch ${esc(r.fullName)}. Since we last emailed you, these school-holiday weeks have moved. ${esc(verdictLine)}</p>
<p style="font-size:14px;color:#5b6663">${esc(COLLECTIONS[r.collection].priceNote)}.</p>
${table(['Week', 'Now', 'Since our last email', '30-day verdict'], moves.map((m) => [
    esc(m.week.label), `<strong>${money(m.price)}</strong>`,
    `${m.change > 0 ? 'Up' : 'Down'} ${money(Math.abs(m.change))} (${Math.abs(m.pct)}%) from ${money(m.from.price)}`, VERDICT[m.dep.trend] || '-',
  ]))}
${button(link(resortPath(r), campaign), `See every ${r.name} week`)}
<p style="font-size:14px">The decision is always yours. We only tell you when something moves.</p>`;
  const html = layout({ preheader: `${moves.length} week${moves.length > 1 ? 's' : ''} moved. Checked ${niceDate(checked)}.`, body, checked });
  assertClean(subject + html);
  return { subject, html, description: `wtb-alert-${r.slug}-${today}`, preheader: `Checked ${niceDate(checked)}` };
}

export async function runAlerts({ kit, summary, state, today, dryRun, mode, log }) {
  const { rows, problems } = schoolWeekRows(summary, today);
  problems.forEach((p) => log(`- ${p}`));
  if (!rows.length) throw new Error('no fresh school-holiday prices; alerts not run');
  const { next, byResort, held } = findMoves(rows, state, today);
  held.forEach((h) => log(`- HELD FOR REVIEW (not sent): ${h.resort.fullName} ${h.week.label} ${h.pct}% (${money(h.from.price)} -> ${money(h.price)})`));
  log(`Alerts: ${rows.length} weeks checked, ${byResort.size} resort(s) with moves past ${ALERT_PCT}% and ${money(ALERT_MIN_GBP)}.`);

  const previews = [], lastAlert = { ...(state.lastAlert || {}) }, sent = [...(state.sent || [])];
  const tags = !dryRun && byResort.size ? await ensureTags(kit, [...byResort.keys()].map(watchTag), log) : null;
  for (const [slug, moves] of byResort) {
    const a = buildAlert(moves, today);
    previews.push({ name: `alert-${slug}-${today}.html`, subject: a.subject, html: a.html });
    let watchers = 1;
    if (!dryRun) {
      const tag = tags.get(watchTag(slug));
      watchers = await kit.tagCount(tag.id);
      if (watchers === 0) {
        log(`- ${slug}: moved, but nobody is watching yet; baseline reset.`);
      } else {
        const b = await kit.createBroadcast({
          subject: a.subject, preview_text: a.preheader, content: a.html, description: a.description, public: false,
          send_at: mode === 'send' ? new Date(Date.now() + 15 * 60e3).toISOString() : null,
          subscriber_filter: [{ all: [{ type: 'tag', ids: [tag.id] }], any: null, none: null }],
        });
        log(`- ${slug}: ${mode === 'send' ? 'SCHEDULED' : 'DRAFT'} broadcast ${b.id} to ${watchers} watcher(s): "${a.subject}"`);
        lastAlert[slug] = today;
        sent.push({ date: today, resort: slug, broadcast: b.id, mode, weeks: moves.length });
      }
    } else {
      log(`- ${slug} (dry run): "${a.subject}"`);
    }
    // Watchers have now been told (or nobody was watching): new baseline is today's price.
    for (const m of moves) next[m.key] = { price: m.price, since: m.checked };
  }
  // Keep every baseline whose departure is still ahead (a resort skipped today as stale keeps its baselines).
  const baselines = Object.fromEntries(Object.entries({ ...(state.baselines || {}), ...next }).filter(([k]) => k.split('/').at(-1) > today));
  return { previews, state: { version: 1, updated: today, baselines, lastAlert, sent: sent.slice(-300) } };
}
