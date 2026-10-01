import { ALL, COLLECTIONS } from '../lib/resorts';
import { posts, slugOf } from '../lib/blog';
import { weekDep, featureWeek, hasData, FAMILY, money, changeText, latestUpdate, niceDate } from '../lib/data';

// Plain-text summary for AI answer engines (llms.txt convention).
export async function GET() {
  const guides = await posts();
  const lines = [
    '# When To Book',
    '',
    '> Independent UK site that checks Club Med and Mark Warner prices every morning and tells families when to book their school-holiday week.',
    '',
    `Last checked: ${niceDate(latestUpdate())}. Family of four = 2 adults + 2 children aged 4-11, 7 nights. Club Med prices exclude flights; Mark Warner prices include flights from London Gatwick.`,
    '',
    '## Resort pages',
    ...ALL.filter(hasData).map((r) => {
      const c = COLLECTIONS[r.collection]; const w = featureWeek(r); const d = weekDep(r, FAMILY, w);
      return `- [${c.brand} ${r.name}](https://whentobook.co.uk${c.base}${r.slug}/): ${w.label}, family of four ${d?.available ? money(d.price) : 'not available'} - ${changeText(d)}`;
    }),
    '',
    '## Key pages',
    '- [School-holiday prices by week](https://whentobook.co.uk/school-holidays/)',
    '- [Club Med](https://whentobook.co.uk/club-med/)',
    '- [Mark Warner](https://whentobook.co.uk/mark-warner/)',
    '- [Guides](https://whentobook.co.uk/blog/)',
    '- [About](https://whentobook.co.uk/about/)',
    '',
    '## Guides',
    ...guides.map((p) => `- [${p.data.title}](https://whentobook.co.uk/blog/${slugOf(p)}/)${p.data.description ? `: ${p.data.description}` : ''}`),
  ];
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
