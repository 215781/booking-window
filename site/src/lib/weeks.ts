// No imports here: this file is also read by the email jobs (site/email) under plain Node.
export interface Week { key: string; label: string; from: string; to: string }

// Departure windows for school-holiday weeks (most schools in England, 2026/27).
// A week's price is the first bookable departure inside its window.
export const WEEKS: Record<'ski' | 'sun', Week[]> = {
  ski: [
    { key: 'christmas', label: 'Christmas', from: '2026-12-18', to: '2026-12-24' },
    { key: 'new-year', label: 'New Year', from: '2026-12-25', to: '2026-12-31' },
    { key: 'february-half-term', label: 'February half-term', from: '2027-02-12', to: '2027-02-18' },
    { key: 'easter-1', label: 'Easter (week 1)', from: '2027-03-26', to: '2027-04-01' },
    { key: 'easter-2', label: 'Easter (week 2)', from: '2027-04-02', to: '2027-04-08' },
  ],
  sun: [
    { key: 'october-half-term', label: 'October half-term', from: '2026-10-23', to: '2026-10-29' },
    { key: 'may-half-term', label: 'May half-term', from: '2027-05-28', to: '2027-06-03' },
    { key: 'summer-1', label: 'Summer holidays (week 1)', from: '2027-07-23', to: '2027-07-29' },
    { key: 'summer-2', label: 'Summer holidays (week 2)', from: '2027-07-30', to: '2027-08-05' },
    { key: 'summer-3', label: 'Summer holidays (mid-August)', from: '2027-08-06', to: '2027-08-12' },
    { key: 'summer-4', label: 'Summer holidays (week 4)', from: '2027-08-13', to: '2027-08-19' },
    { key: 'summer-5', label: 'Summer holidays (week 5)', from: '2027-08-20', to: '2027-08-26' },
  ],
};
