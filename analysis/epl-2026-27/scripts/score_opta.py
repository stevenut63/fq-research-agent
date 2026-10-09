"""Score Opta pre-match probabilities against 2026-27 EPL results.

Method 1: predicted outcome = highest of home/draw/away probability.
Method 2: a team is "predicted" only if its win probability >= 40%;
          if neither side reaches 40%, the prediction is a draw.
"""
import csv, glob, json, sys

SCRATCH = sys.argv[1]
results = {(r['home'], r['away']): r for r in csv.DictReader(open(f'{SCRATCH}/results_2026-27.csv'))}

ALIASES = {'Hull City': 'Hull City AFC', 'Sunderland': 'Sunderland AFC', 'Brighton': 'Brighton & Hove Albion',
           'Spurs': 'Tottenham Hotspur', 'Man City': 'Manchester City', 'Man Utd': 'Manchester United',
           'Newcastle': 'Newcastle United', 'Leeds': 'Leeds United', 'Forest': 'Nottingham Forest'}
def norm(t): t = t.strip(); return ALIASES.get(t, t)

rows = []
for f in sorted(glob.glob(f'{SCRATCH}/opta_mw/mw*.csv')):
    for r in csv.DictReader(open(f)):
        h, a = norm(r['home']), norm(r['away'])
        res = results.get((h, a))
        if res is None:
            print('UNMATCHED', f, h, a, file=sys.stderr); continue
        try:
            ph, pd, pa = float(r['p_home']), float(r['p_draw']), float(r['p_away'])
        except ValueError:
            ph = pd = pa = None
        rows.append(dict(mw=int(res['matchweek']), home=h, away=a, score=f"{res['hg']}-{res['ag']}",
                         ftr=res['ftr'], ph=ph, pd=pd, pa=pa, status=r['status'], src=r['source_url']))

scored = [r for r in rows if r['ph'] is not None]
for r in scored:
    probs = {'H': r['ph'], 'D': r['pd'], 'A': r['pa']}
    r['m1'] = max(probs, key=probs.get)
    if r['ph'] >= 40 or r['pa'] >= 40:
        r['m2'] = 'H' if r['ph'] >= r['pa'] else 'A'
    else:
        r['m2'] = 'D'
    r['m1_ok'] = r['m1'] == r['ftr']
    r['m2_ok'] = r['m2'] == r['ftr']
    # Brier score (multi-class, 0 best, 2 worst) and probability assigned to actual outcome
    tot = r['ph'] + r['pd'] + r['pa']
    p = {k: v / tot for k, v in probs.items()}
    r['brier'] = sum((p[k] - (1 if k == r['ftr'] else 0)) ** 2 for k in 'HDA')
    r['p_actual'] = p[r['ftr']]

def summary(sub, label):
    n = len(sub)
    if not n: return {'label': label, 'n': 0}
    m1 = sum(r['m1_ok'] for r in sub); m2 = sum(r['m2_ok'] for r in sub)
    m2_team = [r for r in sub if r['m2'] != 'D']; m2_draw = [r for r in sub if r['m2'] == 'D']
    return dict(label=label, n=n, m1=m1, m1_pct=100 * m1 / n, m2=m2, m2_pct=100 * m2 / n,
                m2_team_calls=len(m2_team), m2_team_ok=sum(r['m2_ok'] for r in m2_team),
                m2_draw_calls=len(m2_draw), m2_draw_ok=sum(r['m2_ok'] for r in m2_draw),
                brier=sum(r['brier'] for r in sub) / n,
                exp_m1=sum(max(r['ph'], r['pd'], r['pa']) for r in sub) / n)

out = {'all': summary(scored, 'All scored matches'),
       'verified': summary([r for r in scored if r['status'] in ('VERIFIED', 'DERIVED')], 'Verified/derived only'),
       'by_mw': [summary([r for r in scored if r['mw'] == w], f'MW{w}') for w in range(1, 6)],
       'coverage': {s: sum(1 for r in rows if r['status'] == s) for s in ('VERIFIED', 'DERIVED', 'PARTIAL', 'NOT_FOUND')},
       'rows': rows}
json.dump(out, open(f'{SCRATCH}/opta_scored.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))
for r in scored:
    print(f"MW{r['mw']} {r['home']:24} {r['score']:5} {r['away']:24} H{r['ph']:5.1f} D{r['pd']:5.1f} A{r['pa']:5.1f} "
          f"res={r['ftr']} m1={r['m1']}{'✓' if r['m1_ok'] else '✗'} m2={r['m2']}{'✓' if r['m2_ok'] else '✗'} {r['status']}")
