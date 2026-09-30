import summary from '../data/summary.json';
import { COLLECTIONS, type Resort, type CollectionKey } from './resorts';

export interface Dep {
  date: string; available: boolean; price?: number; lowest?: number; highest?: number;
  change30?: number; change30Pct?: number; comparedWith?: string;
  trend?: 'rising' | 'falling' | 'steady' | 'new'; atLowest?: boolean; firstSeen?: string;
  history?: { d: string; p: number }[];
}
export type PartyKey = '2A' | '2A2C';
export const FAMILY: PartyKey = '2A2C';
export const COUPLE: PartyKey = '2A';
import type { Week } from './weeks';
export type { Week };

const data = summary as any;
export const generated: string = data.generated;
export const problems: Record<string, string[]> = data.problems;

import { WEEKS } from './weeks';
export { WEEKS };

export const weeksFor = (r: Resort) => WEEKS[COLLECTIONS[r.collection].season];
export const featureWeek = (r: Resort) => weeksFor(r).find((w) => w.key === COLLECTIONS[r.collection].featureWeek)!;

export function resortData(r: Resort) {
  return data.collections[r.collection]?.[r.id] as { updated: string; stale: boolean; parties: Record<PartyKey, Dep[]> } | undefined;
}
export function deps(r: Resort, party: PartyKey): Dep[] {
  return resortData(r)?.parties[party] ?? [];
}
export function weekDep(r: Resort, party: PartyKey, w: Week): Dep | undefined {
  const inWeek = deps(r, party).filter((d) => d.date >= w.from && d.date <= w.to);
  return inWeek.find((d) => d.available) ?? inWeek[0];
}
export function hasData(r: Resort) {
  return deps(r, FAMILY).some((d) => d.available) || deps(r, COUPLE).some((d) => d.available);
}
export function latestUpdate(collection?: CollectionKey): string {
  const cols = collection ? [collection] : Object.keys(data.collections);
  return cols.flatMap((c) => Object.values(data.collections[c] ?? {}).map((r: any) => r.updated as string)).sort().at(-1) ?? '';
}

export const money = (n?: number) => (n == null ? '-' : '£' + n.toLocaleString('en-GB', { maximumFractionDigits: 0 }));
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
export function niceDate(iso: string, withYear = true) {
  if (!iso) return '-';
  const [y, m, d] = iso.split('-').map(Number);
  return `${d} ${MONTHS[m - 1]}${withYear ? ' ' + y : ''}`;
}
export function weekRange(iso: string) {
  const start = new Date(iso + 'T12:00:00Z');
  const end = new Date(start.getTime() + 7 * 864e5);
  return `${DAYS[start.getUTCDay()]} ${niceDate(iso, false)} - ${niceDate(end.toISOString().slice(0, 10))}`;
}

export const TREND = {
  rising: { word: 'Rising', line: "Prices are climbing - don't leave it too long", tone: 'up' },
  falling: { word: 'Easing', line: 'Prices have eased - worth watching', tone: 'down' },
  steady: { word: 'Steady', line: 'Prices are steady - no need to rush', tone: 'flat' },
  new: { word: 'New', line: 'We have just started tracking this week', tone: 'flat' },
} as const;

export function changeText(d?: Dep) {
  if (!d || !d.available) return 'Not available online';
  if (d.change30 == null) return 'No 30-day comparison yet';
  if (d.change30 === 0) return 'No change in 30 days';
  return `${d.change30 > 0 ? 'Up' : 'Down'} ${money(Math.abs(d.change30))} (${Math.abs(d.change30Pct!)}%) in 30 days`;
}
export function changeShort(d?: Dep) {
  if (!d || !d.available) return '-';
  if (d.change30 == null) return 'New';
  if (d.change30 === 0) return 'No change';
  return `${d.change30 > 0 ? '+' : '-'}${money(Math.abs(d.change30))} (${Math.abs(d.change30Pct!)}%)`;
}
