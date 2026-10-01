// Weekly price-watch digest. Creates a DRAFT broadcast in Kit to all subscribers; the owner
// reviews it in Kit and presses send (or schedules it). Never sends on its own.
import { COLLECTIONS, VERDICT, assertClean, button, esc, layout, link, money, niceDate, resortPath, schoolWeekRows, table } from './content.mjs';

const MOVE_PCT = 3;      // same threshold the site uses for Rising/Easing
const REVIEW_PCT = 25;   // bigger weekly swings are held back for a human check (see PLAN_V3 C6)

export function buildDigest(summary, today) {
  const { rows, problems } = schoolWeekRows(summary, today);
  if (!rows.length) throw new Error('no fresh school-holiday prices; digest not built');
  const checked = rows.map((r) => r.checked).sort().at(-1);
  const held = rows.filter((r) => r.change7 && Math.abs(r.change7.pct) > REVIEW_PCT);
  const ok = rows.filter((r) => !held.includes(r));
  const moved = ok.filter((r) => r.change7 && Math.abs(r.change7.pct) >= MOVE_PCT);
  const up = moved.filter((r) => r.change7.change > 0).sort((a, b) => b.change7.pct - a.change7.pct).slice(0, 5);
  const down = moved.filter((r) => r.change7.change < 0).sort((a, b) => a.change7.pct - b.change7.pct).slice(0, 5);
  const trendCount = (t) => ok.filter((r) => r.dep.trend === t).length;
  const [nUp, nDown, nSteady] = [trendCount('rising'), trendCount('falling'), trendCount('steady')];
  const campaign = `digest-${today}`;

  const line = (r) => `<a href="${esc(link(resortPath(r.resort), campaign))}" style="color:#1a4a42">${esc(r.resort.fullName)}</a>, ${esc(r.week.label)}`;
  const moveRows = (list) => table(['Resort and week', 'Now', 'This week'], list.map((r) => [
    line(r), money(r.price), `${r.change7.change > 0 ? 'Up' : 'Down'} ${money(Math.abs(r.change7.change))} (${Math.abs(r.change7.pct)}%)`,
  ]));

  let body = `<h1 style="font-family:Georgia,serif;font-size:24px;color:#1a4a42;margin:0 0 8px">This week's price watch</h1>
<p><strong>In one line:</strong> across the ${ok.length} school-holiday weeks we watch, ${nUp} are rising, ${nDown} are easing and ${nSteady} are steady over the last 30 days.</p>`;
  body += up.length ? `<h2 style="font-size:18px;color:#1a4a42">Rising this week</h2><p>If one of these is your week, don't leave it too long.</p>${moveRows(up)}` : `<h2 style="font-size:18px;color:#1a4a42">Rising this week</h2><p>Nothing rose by ${MOVE_PCT}% or more this week.</p>`;
  body += down.length ? `<h2 style="font-size:18px;color:#1a4a42">Easing this week</h2><p>Prices have come down. Worth a look, they may not stay here.</p>${moveRows(down)}` : `<h2 style="font-size:18px;color:#1a4a42">Easing this week</h2><p>Nothing eased by ${MOVE_PCT}% or more this week.</p>`;

  // One featured week per collection, every resort, so readers can find theirs quickly.
  for (const [key, c] of Object.entries(COLLECTIONS)) {
    const feat = ok.filter((r) => r.resort.collection === key && r.week.key === c.featureWeek).sort((a, b) => a.price - b.price);
    if (!feat.length) continue;
    body += `<h2 style="font-size:18px;color:#1a4a42">${esc(c.label)}: ${esc(feat[0].week.label)} at a glance</h2>
<p style="font-size:14px;color:#5b6663">${esc(c.priceNote)}.</p>
${table(['Resort', 'Now', '30-day verdict'], feat.map((r) => [line(r).replace(`, ${esc(r.week.label)}`, ''), money(r.price), VERDICT[r.dep.trend] || '-']))}`;
  }
  body += button(link('/school-holidays/', campaign), 'See every school-holiday week');
  body += `<p>Watching a particular resort? Use the "Watch prices for me" box on its page and we'll email you when its school-holiday prices move.</p>`;

  const subject = `Price watch: ${nUp} weeks rising, ${nDown} easing (${niceDate(today)})`;
  const preheader = `${nUp} rising, ${nDown} easing, ${nSteady} steady. Checked ${niceDate(checked)}.`;
  const html = layout({ preheader, body, checked });
  assertClean(subject + html);
  return {
    subject, html, preheader, description: `wtb-digest-${today}`,
    notes: [...problems, ...held.map((r) => `HELD FOR REVIEW: ${r.resort.fullName} ${r.week.label} moved ${r.change7.pct}% in a week (${money(r.change7.from)} -> ${money(r.price)})`)],
    stats: { weeks: ok.length, rising: nUp, easing: nDown, steady: nSteady, held: held.length },
  };
}

export async function runDigest({ kit, summary, today, dryRun, log }) {
  const d = buildDigest(summary, today);
  d.notes.forEach((n) => log(`- ${n}`));
  log(`Digest: ${JSON.stringify(d.stats)}`);
  if (dryRun) return { previews: [{ name: `digest-${today}.html`, subject: d.subject, html: d.html }] };
  const existing = (await kit.broadcasts()).find((b) => b.description === d.description);
  if (existing) { log(`Draft already exists for ${today} (broadcast ${existing.id}); not creating another.`); return { previews: [] }; }
  const b = await kit.createBroadcast({ subject: d.subject, preview_text: d.preheader, content: d.html, description: d.description, public: false, send_at: null });
  log(`Created DRAFT broadcast ${b.id} "${d.subject}" - review and send it in Kit > Broadcasts.`);
  return { previews: [{ name: `digest-${today}.html`, subject: d.subject, html: d.html }] };
}
