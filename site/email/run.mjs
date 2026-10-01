#!/usr/bin/env node
// When To Book email automation. Usage:
//   node --experimental-strip-types site/email/run.mjs <check|sync|alerts|digest> [--dry-run] [--full]
// Env: KIT_API_KEY (from GitHub secret KIT_API), SUMMARY_PATH (summary.json), EMAIL_STATE_PATH (alert baselines JSON),
//      EMAIL_OUT_DIR (HTML previews), ALERT_MODE=draft|send, ALERT_PCT, ALERT_MIN_GBP.
import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { kitClient } from './kit.mjs';
import { loadSummary } from './content.mjs';
import { runCheck } from './check.mjs';
import { runSync } from './sync.mjs';
import { runAlerts } from './alerts.mjs';
import { runDigest } from './digest.mjs';

const [task, ...flags] = process.argv.slice(2);
const dryRun = flags.includes('--dry-run');
const full = flags.includes('--full');
const today = process.env.EMAIL_TODAY || new Date().toISOString().slice(0, 10);
const here = dirname(new URL(import.meta.url).pathname);
const summaryPath = process.env.SUMMARY_PATH || join(here, '../src/data/summary.json');
const statePath = process.env.EMAIL_STATE_PATH || join(here, 'out/email_state.json');
const outDir = process.env.EMAIL_OUT_DIR || join(here, 'out');
const mode = process.env.ALERT_MODE === 'send' ? 'send' : 'draft';

const lines = [];
const log = (s) => { console.log(s); lines.push(s); };
const kit = dryRun ? null : kitClient(process.env.KIT_API_KEY);

try {
  log(`## Email job: ${task}${dryRun ? ' (dry run)' : ''} - ${today}`);
  let previews = [];
  if (task === 'check') await runCheck({ kit, log });
  else if (task === 'sync') await runSync({ kit, full, log });
  else if (task === 'digest') ({ previews } = await runDigest({ kit, summary: loadSummary(summaryPath), today, dryRun, log }));
  else if (task === 'alerts') {
    const state = existsSync(statePath) ? JSON.parse(readFileSync(statePath, 'utf8')) : {};
    const res = await runAlerts({ kit, summary: loadSummary(summaryPath), state, today, dryRun, mode, log });
    previews = res.previews;
    if (!dryRun) { mkdirSync(dirname(statePath), { recursive: true }); writeFileSync(statePath, JSON.stringify(res.state, null, 1) + '\n'); }
    else log(`(dry run: baselines not saved; ${Object.keys(res.state.baselines).length} weeks would be tracked)`);
  } else throw new Error(`unknown task "${task}" (use check, sync, alerts or digest)`);
  if (previews.length) {
    mkdirSync(outDir, { recursive: true });
    for (const p of previews) writeFileSync(join(outDir, p.name), `<!doctype html><meta charset="utf-8"><title>${p.subject.replace(/</g, '&lt;')}</title><p><b>Subject:</b> ${p.subject.replace(/</g, '&lt;')}</p><hr>${p.html}`);
    log(`Previews written to ${outDir}: ${previews.map((p) => p.name).join(', ')}`);
  }
} catch (e) {
  log(`FAILED: ${e.message}`);
  process.exitCode = 1;
} finally {
  if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, lines.join('\n') + '\n');
}
