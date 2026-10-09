"""Join Opta-scored rows with market closing odds; compute like-for-like comparisons."""
import csv, json, sys
S = sys.argv[1]
opta = json.load(open(f'{S}/opta_scored.json'))
MAP = {"Nott'm Forest": 'Nottingham Forest', 'Man United': 'Manchester United', 'Man City': 'Manchester City',
       'Hull': 'Hull City AFC', 'Sunderland': 'Sunderland AFC', 'Brighton': 'Brighton & Hove Albion',
       'Tottenham': 'Tottenham Hotspur', 'Newcastle': 'Newcastle United', 'Leeds': 'Leeds United',
       'Ipswich': 'Ipswich Town', 'Coventry': 'Coventry City', 'Wolves': 'Wolverhampton Wanderers'}
nm = lambda t: MAP.get(t, t)
mk = {}
for r in csv.DictReader(open(f'{S}/bettingdata/refresh/results_with_odds.csv')):
    if r['season'] != '2026-27': continue
    o = [float(r[f'market_avg_1x2_{k}_close']) for k in ('home', 'draw', 'away')]
    imp = [1 / x for x in o]; s = sum(imp)
    mk[(nm(r['home_team']), nm(r['away_team']))] = [100 * x / s for x in imp]

def picks(ph, pd, pa):
    m1 = max({'H': ph, 'D': pd, 'A': pa}.items(), key=lambda kv: kv[1])[0]
    m2 = ('H' if ph >= pa else 'A') if max(ph, pa) >= 40 else 'D'
    return m1, m2

def brier(ph, pd, pa, ftr):
    t = ph + pd + pa; p = {'H': ph / t, 'D': pd / t, 'A': pa / t}
    return sum((p[k] - (k == ftr)) ** 2 for k in 'HDA')

rows = []
for r in opta['rows']:
    m = mk.get((r['home'], r['away']))
    if m is None: print('NO MARKET', r['home'], r['away'], file=sys.stderr)
    r['mh'], r['md'], r['ma'] = m
    r['mk_m1'], r['mk_m2'] = picks(*m)
    r['mk_brier'] = brier(*m, r['ftr'])
    rows.append(r)

def tally(sub, prefix):
    n = len(sub)
    if prefix == 'opta':
        a = sum(r['m1'] == r['ftr'] for r in sub); b = sum(r['m2'] == r['ftr'] for r in sub)
        br = sum(r['brier'] for r in sub) / n
    else:
        a = sum(r['mk_m1'] == r['ftr'] for r in sub); b = sum(r['mk_m2'] == r['ftr'] for r in sub)
        br = sum(r['mk_brier'] for r in sub) / n
    return dict(n=n, m1=a, m1_pct=100 * a / n, m2=b, m2_pct=100 * b / n, brier=br)

cov = [r for r in rows if r['ph'] is not None]
nocov = [r for r in rows if r['ph'] is None]
out = dict(opta_cov=tally(cov, 'opta'), market_cov=tally(cov, 'mk'),
           market_all=tally(rows, 'mk'), market_nocov=tally(nocov, 'mk') if nocov else None,
           agree_m1=sum(r['m1'] == r['mk_m1'] for r in cov),
           home_only=sum(r['ftr'] == 'H' for r in rows), n_all=len(rows), rows=rows)
json.dump(out, open(f'{S}/combined.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))
for r in cov:
    if r['m1'] != r['mk_m1'] or r['m2'] != r['mk_m2']:
        print('DISAGREE', r['home'], r['away'], r['ftr'], 'opta', r['m1'], r['m2'], 'mkt', r['mk_m1'], r['mk_m2'])
