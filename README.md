# EasyProp

A sports research site: game lines, player props, price comparison, the reasons behind a line, and paper tracking.
It is for research, comparison and paper tracking only. It takes no deposits, places no wagers, and never moves money.

Live site: https://evancleveland1-droid.github.io/easyprop/

## Run it locally

There is nothing to install or build. The whole app is `index.html`.

```bash
python3 -m http.server 8124
```

Then open `http://localhost:8124/` for the app and `http://localhost:8124/tests.html` for the tests.

## Tests

`tests.html` loads the real app in a hidden frame and checks its rules. It needs no keys and no paid feeds.
It covers exact-line matching, best-price ranking, stale and suspended quotes, duplicate player names,
missing credentials, unverified news, paper grading (wins, losses, pushes, voids), odds math, and market matching.
Multi-book cases run on fixtures, because no multi-book account is connected.

## Keys and settings

There are no environment variables and no server. Nothing secret is stored in this repository.

| Setting | Where it lives | Needed? |
|---|---|---|
| The Odds API key | Typed into the app under Best odds; saved only in that browser (`wc_oddskey`) | Optional. Without it, only DraftKings is checked. |
| GitHub token for the price job | Supplied by GitHub Actions at run time | Automatic. Not a stored secret. |

Because there is no server, an odds key entered in the app is sent from the browser straight to The Odds API.
Keeping it server-side would need a backend, which this project does not have.

## Where each number comes from

| Data | Source | Status |
|---|---|---|
| Scores, schedules, team records | ESPN public scoreboard | Live |
| Game lines (spread, total, moneyline) | DraftKings, carried by ESPN | Live. Pregame only on the Games page; rows for games in progress say so. |
| Player props, milestones, 1st half, quarters, team totals | DraftKings, carried by ESPN | Live for NBA, NHL and NFL when the book has posted them |
| Live in-game prices | DraftKings live odds, carried by ESPN | Live, in Build a bet › Live now |
| Player game logs and injury report | ESPN | Live |
| Kalshi and Polymarket game prices | Each site's public data, saved every 10 minutes by `.github/workflows/kalshi.yml` | Live. Shown as exchange prices, never compared with sportsbook quotes. Hidden when older than 45 minutes. |
| Other sportsbooks (FanDuel, BetMGM and so on) | The Odds API | **Unverified.** The adapter is written and tested on fixtures; it has not been run against a live account. |
| College player props | None | **Estimate only**, labeled "est. line". No book feed. |
| Kronos | None | **Unverified provider request.** Nothing in this repo documents it, so nothing was built. |
| News, practice reports, coach comments | None | **Unsupported.** The app says so instead of guessing. |

## Coverage by league

| League | Game lines | Player props (real lines) | Why-this-line research | Paper grading | Kalshi | Polymarket |
|---|---|---|---|---|---|---|
| NBA | Live | Live | Live | Automatic | Live | Live |
| NFL | Live | Live once posted | Live | Automatic | Live | Live |
| NHL | Live | Live | Not yet (no game-log mapping) | By hand | Live | Live |
| College football | Live | Estimates only | Estimates only | No | Live | Live |
| College basketball | Live | Estimates only | Estimates only | No | Live | None found |
| WNBA, MLB | Live in season | Untested (out of season) | Untested | Untested | Untested | Untested |
| Premier League, La Liga, MLS, Champions League | Live | Scorer markets only | No | No | Live | Live |

## How "best price" works

A price is only compared with other prices for the same game, player, stat, period, side and line.
Over 24.5 at +105 beats over 24.5 at -110. Over 25.5 is a different offer and is listed separately.
Quotes that are stale (more than 12 minutes since they were fetched), suspended, missing a price, or matched to an
ambiguous player name are left out. With only one book checked there is no "best price" label at all.
The app does not know which books are legal where you are.

## What is left

- Connect and verify a multi-book feed with a real account, then check what it is allowed to display.
- NHL and MLB game-log mapping, so research and automatic paper grading work there.
- A sourced news feed. Until one exists, the research panel shows only stats and the injury report.
- A backend, if keys ever need to be kept off the device.
