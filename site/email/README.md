# Email automation (Kit)

Three automated emails, all built from the same price data as the site. We store no subscriber data:
emails, interests and tags live in Kit only. The alert baselines file (`_data/email_state.json` on main)
holds prices only.

| What | When | How it goes out |
|---|---|---|
| **Welcome sequence** (3 emails) | On signup (after double opt-in) | Kit sequence, set up once in Kit (copy below) |
| **Price-move alerts** | Daily 11:20 UTC | Kit broadcast to tag `watch-<resort>`. **Draft** until repo variable `ALERT_MODE=send` |
| **Weekly digest** | Saturday 08:00 UTC | Kit **draft** broadcast to everyone. Owner reviews and sends |

Workflow: `.github/workflows/email.yml` (on main). Code: `site/email/` (rebuild branch).

## How alerts decide

- Family of four, 7 nights, every future school-holiday week (`site/src/lib/weeks.ts`) at every resort with fresh data.
- Compared with the price when we last emailed that resort's watchers (first run just records baselines).
- Alert when a week moves at least **5% and £150** (`ALERT_PCT`, `ALERT_MIN_GBP`). One email per resort, listing every week that moved.
- Moves over **40%** are never sent: they appear as "HELD FOR REVIEW" in the run summary.
- Stale data (older than 3 days) is skipped. At most one alert per resort per 7 days.
- Nobody watching a resort yet: no email, baseline reset.

Signup form -> tags: the site sends `resort_interest` (resort slug, or `general` / `club-med` / `mark-warner` / `school-holidays`).
The daily sync turns known values into tags (`watch-tignes`, `interest-club-med`, ...). Unknown values are ignored.

## Running by hand

GitHub > Actions > "Email automation (Kit)" > Run workflow. Tasks: `check` (proves the key works), `sync`, `alerts`, `digest`.
Tick "Dry run" to build previews only (download "email-previews" from the run).

Locally: `cd site && npm run data && node --experimental-strip-types email/run.mjs digest --dry-run` (previews in `site/email/out/`).
Tests: `node --experimental-strip-types email/test_email.mjs`.

## One-off setup in Kit (owner)

1. **Kit v4 API key**: Kit > Settings > Developer > API keys (v4) > create "whentobook-automation". Save it in GitHub > repo Settings > Secrets > Actions as `KIT_API` (already exists - replace its value if it is not a v4 key starting `kit_`). Then run the workflow with task `check`.
2. **Double opt-in** on form 7f784a323c (Booking Alert): form Settings > Incentive > "Send incentive email" on. Subject: "Confirm your price watch".
3. **Welcome sequence**: Kit > Send > Sequences > New "Founding Watchers welcome". Paste the three emails below. Then Automate > Visual automations: trigger "Joins form: Booking Alert" -> "Add to sequence: Founding Watchers welcome".
4. **Sender**: From "Connor at When To Book", address admin@whentobook.co.uk (after SPF/DKIM/DMARC are set).
5. After checking a few alert drafts, set GitHub > Settings > Variables > Actions: `ALERT_MODE` = `send`.

## Welcome sequence copy

### Email 1 (send immediately)

**Subject:** You're a Founding Watcher
**Preview:** Here's what happens next.

Hi,

Thanks for joining. You're one of our first Founding Watchers, so you'll see everything first and your replies shape what we build.

Here's what happens next:

- **Every morning** we check prices at every resort we cover, for every school-holiday week.
- **If you picked a resort**, we'll email you when one of its school-holiday weeks moves by 5% or more.
- **Every weekend** you get one short email: what's rising, what's easing and what's steady.

We don't sell holidays and we'll never share your email. The decision is always yours.

One favour: hit reply and tell me which resort and which week you're thinking about. I read every reply, and it helps me decide what to track next.

Connor
When To Book

### Email 2 (2 days later)

**Subject:** Rising, Easing, Steady: how to read our emails
**Preview:** Three words, one decision.

Hi,

Every week we give each school-holiday week one word:

- **Rising**: the price is up 3% or more over the last 30 days. If it's your week, don't leave it too long.
- **Easing**: the price is down 3% or more. Worth a look now, it may not stay there.
- **Steady**: within 3% either way. No need to rush.

Every price shows the date we checked it. Prices change during the day, so always check the price on the holiday company's site before you book. Our numbers are guidance, not a quote.

Want alerts for a particular resort? Open its page on whentobook.co.uk and use the "Watch prices for me" box.

Connor

### Email 3 (5 days later)

**Subject:** Is your week on our list?
**Preview:** Tell me what to track next.

Hi,

Today we track Club Med ski in the French Alps, Club Med sun resorts and Mark Warner beach resorts, for every school-holiday week, for couples and families of four.

We're working on more holiday companies. If yours isn't here yet, reply with its name and the week you're after. The most requested ones go first.

See every school-holiday week in one place: https://whentobook.co.uk/school-holidays/

Connor
When To Book
