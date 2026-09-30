// Minimal Kit (ConvertKit) v4 API client. Runs only in GitHub Actions with the key from
// the KIT_API_KEY secret. Never commit a key. Kit holds all subscriber data; we store none.
const BASE = 'https://api.kit.com/v4';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export function kitClient(key) {
  if (!key) throw new Error('KIT_API_KEY is not set (needs a Kit v4 API key: Kit > Settings > Developer)');

  async function call(method, path, body) {
    for (let attempt = 1; ; attempt++) {
      const res = await fetch(BASE + path, {
        method,
        headers: { 'X-Kit-Api-Key': key, Accept: 'application/json', ...(body ? { 'Content-Type': 'application/json' } : {}) },
        body: body ? JSON.stringify(body) : undefined,
      });
      if ((res.status === 429 || res.status >= 500) && attempt < 4) { await sleep(3000 * attempt); continue; }
      const text = await res.text();
      let json = {};
      try { json = text ? JSON.parse(text) : {}; } catch { json = { raw: text }; }
      if (!res.ok) {
        const err = new Error(`Kit ${method} ${path.split('?')[0]} -> ${res.status}: ${text.slice(0, 300)}`);
        err.status = res.status;
        throw err;
      }
      return json;
    }
  }

  async function* paginate(path, listKey) {
    let after = null;
    do {
      const sep = path.includes('?') ? '&' : '?';
      const r = await call('GET', `${path}${sep}per_page=1000${after ? `&after=${encodeURIComponent(after)}` : ''}`);
      for (const item of r[listKey] || []) yield item;
      after = r.pagination?.has_next_page ? r.pagination.end_cursor : null;
    } while (after);
  }
  const all = async (path, listKey) => { const out = []; for await (const x of paginate(path, listKey)) out.push(x); return out; };

  return {
    account: () => call('GET', '/account'),
    forms: () => all('/forms', 'forms'),
    tags: () => all('/tags', 'tags'),
    broadcasts: () => all('/broadcasts', 'broadcasts'),
    createTag: async (name) => (await call('POST', '/tags', { name })).tag,
    tagSubscriber: (tagId, subscriberId) => call('POST', `/tags/${tagId}/subscribers/${subscriberId}`, {}),
    subscribers: (query = '') => paginate(`/subscribers?status=active${query}`, 'subscribers'),
    subscriberCount: async () => (await call('GET', '/subscribers?status=active&per_page=1&include_total_count=true')).pagination?.total_count ?? null,
    tagCount: async (tagId) => (await call('GET', `/tags/${tagId}/subscribers?status=active&per_page=1&include_total_count=true`)).pagination?.total_count ?? 0,
    createBroadcast: async (b) => (await call('POST', '/broadcasts', b)).broadcast,
    sleep,
  };
}
