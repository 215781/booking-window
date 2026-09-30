// Connection check: proves the Kit key works and shows what the automation will see. Prints no emails.
export async function runCheck({ kit, log }) {
  const acc = await kit.account();
  log(`Kit account: ${acc.account?.name ?? '?'} (plan: ${acc.account?.plan_type ?? '?'})`);
  log(`Active subscribers: ${await kit.subscriberCount()}`);
  const forms = await kit.forms();
  log(`Forms: ${forms.map((f) => `${f.name} [${f.uid ?? f.id}]`).join(', ') || 'none'}`);
  const tags = await kit.tags();
  const watch = tags.filter((t) => t.name.startsWith('watch-') || t.name.startsWith('interest-'));
  log(`Tags: ${tags.length} in total, ${watch.length} used by the automation`);
  const drafts = (await kit.broadcasts()).filter((b) => String(b.description || '').startsWith('wtb-'));
  log(`Broadcasts created by the automation: ${drafts.length}`);
}
