import summary from '../data/summary.json';
import { RESORTS, type Resort } from './resorts';

export interface Dep {
  date: string; available: boolean; price?: number; lowest?: number; highest?: number;
  change30?: number; change30Pct?: number; comparedWith?: string;
  trend?: 'rising' | 'falling' | 'steady' | 'new'; atLowest?: boolean; firstSeen?: string;
  history?: { d: string; p: number }[];
}
export type PartyKey = '2A' | '2A2C';
export const FAMILY: PartyKey = '2A2C';
export const COUPLE: PartyKey = '2A';

export const data = summary as any;
export const schoolWeeks: { key: string; label: string; date: string }[] = data.schoolWeeks;
export const generated: string = data.generated;

export function resortData(r: Resort) {
  return data.resorts[r.id] as { updated: string; stale: boolean; parties: Record<PartyKey, Dep[]> } | undefined;
}
export function dep(r: Resort, party: PartyKey, date: string): Dep | undefined {
  return resortData(r)?.parties[party]?.find((d) => d.date === date);
}
export function latestUpdate(): string {
  return RESORTS.map((r) => resortData(r)?.updated ?? '').sort().at(-1) ?? '';
}

export const money = (n?: number) =>
  n == null ? '-' : '£' + n.toLocaleString('en-GB', { maximumFractionDigits: 0 });

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export function niceDate(iso: string, withYear = true) {
  const [y, m, d] = iso.split('-').map(Number);
  return `${d} ${MONTHS[m - 1]}${withYear ? ' ' + y : ''}`;
}
export function weekRange(iso: string) {
  const start = new Date(iso + 'T12:00:00Z');
  const end = new Date(start.getTime() + 7 * 864e5);
  const e = end.toISOString().slice(0, 10);
  return `${niceDate(iso, false)} - ${niceDate(e)}`;
}

export const TREND = {
  rising: { word: 'Rising', line: "Prices are climbing - don't leave it too long", tone: 'up' },
  falling: { word: 'Easing', line: 'Prices have eased - worth watching', tone: 'down' },
  steady: { word: 'Steady', line: 'Prices are steady - no need to rush', tone: 'flat' },
  new: { word: 'New', line: 'Just started tracking this week', tone: 'flat' },
} as const;

export function changeText(d?: Dep) {
  if (!d || !d.available) return 'Not available online';
  if (d.change30 == null) return 'No 30-day comparison yet';
  if (d.change30 === 0) return 'No change in 30 days';
  const dir = d.change30 > 0 ? 'Up' : 'Down';
  return `${dir} ${money(Math.abs(d.change30))} (${Math.abs(d.change30Pct!)}%) in 30 days`;
}

export function changeShort(d?: Dep) {
  if (!d || !d.available) return '-';
  if (d.change30 == null) return 'New';
  if (d.change30 === 0) return 'No change';
  return `${d.change30 > 0 ? '+' : '-'}${money(Math.abs(d.change30))} (${Math.abs(d.change30Pct!)}%)`;
}
