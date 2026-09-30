// Turns the signup form's resort_interest field into Kit tags, so alerts can target watchers.
// resort page signup -> tag "watch-<resort slug>"; brand/general signups -> "interest-<value>".
// Only known values become tags (a visitor can't create arbitrary tags by editing the form).
import { RESORTS } from './content.mjs';

const OTHER = ['general', 'club-med', 'mark-warner', 'school-holidays'];
export const watchTag = (slug) => `watch-${slug}`;

export async function ensureTags(kit, names, log) {
  const byName = new Map((await kit.tags()).map((t) => [t.name, t]));
  for (const n of names) {
    if (!byName.has(n)) { const t = await kit.createTag(n); byName.set(n, t); log(`Created tag ${n}`); }
  }
  return byName;
}

export async function runSync({ kit, full, log }) {
  const tagFor = new Map([...RESORTS.map((r) => [r.slug, watchTag(r.slug)]), ...OTHER.map((o) => [o, `interest-${o}`])]);
  const tags = await ensureTags(kit, [...new Set(tagFor.values())], log);
  // Daily pass looks at subscribers updated in the last 3 days; the weekly pass (full) checks everyone.
  const since = new Date(Date.now() - 3 * 864e5).toISOString();
  let seen = 0, tagged = 0, unknown = 0;
  for await (const s of kit.subscribers(full ? '' : `&updated_after=${encodeURIComponent(since)}`)) {
    seen++;
    const v = String(s.fields?.resort_interest || '').trim().toLowerCase();
    if (!v) continue;
    const name = tagFor.get(v);
    if (!name) { unknown++; continue; }
    await kit.tagSubscriber(tags.get(name).id, s.id);
    tagged++;
    await kit.sleep(600); // stay well under Kit's 120 requests/minute
  }
  log(`Sync: ${seen} subscribers checked, ${tagged} tag(s) applied, ${unknown} unrecognised interest value(s).`);
  return { seen, tagged };
}
