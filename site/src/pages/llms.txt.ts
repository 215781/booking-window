import { RESORTS } from '../lib/resorts';
import { schoolWeeks, dep, FAMILY, money, changeText, latestUpdate, niceDate } from '../lib/data';

// Plain-text summary for AI answer engines (llms.txt convention).
export function GET() {
  const lines = [
    '# When To Book',
    '',
    '> Independent UK site that checks Club Med ski prices every morning and tells families when to book their school-holiday week. Prices: 7 nights, all-inclusive package without flights.',
    '',
    `Last checked: ${niceDate(latestUpdate())}. Family of four = 2 adults + 2 children aged 4-11.`,
    '',
    '## Resort pages',
    ...RESORTS.map((r) => {
      const d = dep(r, FAMILY, schoolWeeks.find((w) => w.key === 'february-half-term')!.date);
      return `- [${r.name}](https://whentobook.co.uk/club-med/${r.slug}/): February half-term 2027, family of four ${d?.available ? money(d.price) : 'not available'} - ${changeText(d)}`;
    }),
    '',
    '## Key pages',
    '- [School-holiday prices by week](https://whentobook.co.uk/school-holidays/)',
    '- [Guides](https://whentobook.co.uk/blog/)',
    '- [About](https://whentobook.co.uk/about/)',
  ];
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
