"""Fetch Kalshi's PUBLIC game-winner market prices (no API key, no login) and write kalshi.json.
Kalshi blocks browsers from calling its API directly, so this runs on a schedule in GitHub Actions
and the EasyProp site reads the saved file instead. Read-only: it never places orders."""
import json, re, sys, time, urllib.request, urllib.parse, datetime

BASE = 'https://external-api.kalshi.com/trade-api/v2'
SERIES = {'nba': 'KXNBAGAME', 'nfl': 'KXNFLGAME', 'nhl': 'KXNHLGAME', 'ncaaf': 'KXNCAAFGAME', 'ncaam': 'KXNCAAMBGAME',
          'mlb': 'KXMLBGAME', 'wnba': 'KXWNBAGAME', 'epl': 'KXEPLGAME', 'laliga': 'KXLALIGAGAME', 'mls': 'KXMLSGAME', 'ucl': 'KXUCLGAME'}
MON = {m: i + 1 for i, m in enumerate('JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split())}
DAYS_AHEAD = 8
MAX_PAGES = 4


def get(path):
    for attempt in range(3):
        try:
            req = urllib.request.Request(BASE + path, headers={'User-Agent': 'easyprop-data/1.0', 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except Exception as e:  # back off on 429s and blips
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))


def num(v):
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def main():
    today = datetime.datetime.utcnow().date()
    games, errors = [], []
    for lg, series in SERIES.items():
        events, cursor = {}, ''
        try:
            for _ in range(MAX_PAGES):
                q = {'series_ticker': series, 'status': 'open', 'limit': 200}
                if cursor:
                    q['cursor'] = cursor
                j = get('/markets?' + urllib.parse.urlencode(q))
                for m in j.get('markets', []):
                    et = m.get('event_ticker', '')
                    d = re.match(r'^[A-Z0-9]+-(\d{2})([A-Z]{3})(\d{2})', et)
                    if not d or d.group(2) not in MON:
                        continue
                    date = datetime.date(2000 + int(d.group(1)), MON[d.group(2)], int(d.group(3)))
                    if not (-1 <= (date - today).days <= DAYS_AHEAD):
                        continue
                    name = (m.get('yes_sub_title') or '').strip()
                    if not name:
                        continue
                    g = events.setdefault(et, {'lg': lg, 'date': date.isoformat(), 'ev': et, 'teams': []})
                    g['teams'].append({'n': name, 'a': m.get('ticker', '').rsplit('-', 1)[-1],
                                       'bid': num(m.get('yes_bid_dollars')), 'ask': num(m.get('yes_ask_dollars')),
                                       'last': num(m.get('last_price_dollars')), 'vol': num(m.get('volume_fp'))})
                cursor = j.get('cursor') or ''
                if not cursor:
                    break
                time.sleep(0.5)
        except Exception as e:
            errors.append(f'{lg}: {e}')
        games.extend(events.values())
        time.sleep(0.5)
    if not games and errors:
        print('No data fetched:', errors, file=sys.stderr)
        sys.exit(1)   # keep the last good file rather than publishing an empty one
    out = {'updated': datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
           'source': 'Kalshi public market data (prediction-market prices, not sportsbook odds)',
           'errors': errors, 'games': games}
    with open('kalshi.json', 'w') as f:
        json.dump(out, f, separators=(',', ':'))
    print(len(games), 'games', 'errors:', errors)


if __name__ == '__main__':
    main()
