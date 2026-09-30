// Offline tests for the email jobs (no Kit calls): node --experimental-strip-types site/email/test_email.mjs
import assert from 'node:assert/strict';
import { schoolWeekRows } from './content.mjs';
import { findMoves, buildAlert } from './alerts.mjs';
import { buildDigest } from './digest.mjs';

const today = '2026-10-01';
const dep = (date, price, trend = 'rising', history = []) => ({ date, available: true, price, trend, history });
const summary = { collections: {
  'clubmed-ski': {
    'tignes-val-claret': { updated: '2026-10-01', stale: false, parties: { '2A2C': [
      dep('2027-02-14', 11000, 'rising', [{ d: '2026-09-24', p: 10000 }, { d: '2026-10-01', p: 11000 }]),
      dep('2026-12-20', 9000, 'steady'),
    ] } },
    'val-disere': { updated: '2026-10-01', stale: false, parties: { '2A2C': [dep('2027-02-14', 15000, 'rising', [{ d: '2026-09-24', p: 9000 }, { d: '2026-10-01', p: 15000 }])] } },
    'les-arcs': { updated: '2026-09-20', stale: true, parties: { '2A2C': [dep('2027-02-14', 8000)] } },
  },
} };

const { rows, problems } = schoolWeekRows(summary, today);
assert.equal(rows.length, 3, 'stale resort skipped, 3 fresh weeks');
assert.ok(problems.some((p) => p.includes('Les Arcs')), 'stale resort reported');
assert.equal(rows.find((r) => r.resort.slug === 'tignes' && r.week.key === 'february-half-term').change7.change, 1000);

// First run: everything becomes a baseline, nothing sent.
let r1 = findMoves(rows, {}, today);
assert.equal(r1.byResort.size, 0);
assert.equal(Object.keys(r1.next).length, 3);

// Baselines 10% lower for Tignes Feb (alert), 2% lower for Tignes Christmas (no alert), Val d'Isère 40%+ (held).
const key = (slug, wk) => rows.find((r) => r.resort.slug === slug && r.week.key === wk).key;
const state = { baselines: {
  [key('tignes', 'february-half-term')]: { price: 10000, since: '2026-09-01' },
  [key('tignes', 'christmas')]: { price: 8820, since: '2026-09-01' },
  [key('val-disere', 'february-half-term')]: { price: 9000, since: '2026-09-01' },
} };
const r2 = findMoves(rows, state, today);
assert.deepEqual([...r2.byResort.keys()], ['tignes']);
assert.equal(r2.byResort.get('tignes').length, 1);
assert.equal(r2.held.length, 1, 'big jump held for review');

// Cooldown: alerted 3 days ago -> nothing.
assert.equal(findMoves(rows, { ...state, lastAlert: { tignes: '2026-09-28' } }, today).byResort.size, 0);

const a = buildAlert(r2.byResort.get('tignes'), today);
assert.match(a.subject, /^Tignes: February half-term is up £1,000$/);
assert.ok(a.html.includes('utm_campaign=alert-tignes-2026-10-01'));
assert.ok(a.html.includes('guidance only') || a.html.includes('Guidance only'));

const d = buildDigest(summary, today);
assert.equal(d.stats.held, 1);
assert.ok(d.html.includes('Rising this week'));
assert.ok(!/—/.test(d.html));
console.log('email tests passed');
