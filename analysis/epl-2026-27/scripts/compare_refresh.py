"""Compare the current GW6 blend with an earlier snapshot, and price the user's Sportsbet multi."""
import json, math, sys
S, before_path = sys.argv[1], sys.argv[2]
now = {g['home']: g for g in json.load(open(f'{S}/gw6_final.json'))}
before = {g['home']: g for g in json.load(open(before_path))}
print('Fixture changes (blend H/D/A, call, score):')
for h, g in now.items():
    b = before[h]
    fmt = lambda x: '/'.join(f'{100 * p:.0f}' for p in x['blend'])
    flag = '' if (g['call'], g['score']) == (b['call'], b['score']) else '  <-- CHANGED'
    print(f"  {h[:16]:16} v {g['away'][:16]:16} {fmt(b)} {b['call']} {b['score']}  ->  {fmt(g)} {g['call']} {g['score']}{flag}")
legs = [('Manchester United', 0, 'Man Utd to beat Spurs'), ('Chelsea', 0, 'Chelsea to beat Bournemouth'),
        ('Coventry City', 2, 'Newcastle to win at Coventry'), ('Sunderland AFC', 2, 'Brighton to win at Sunderland')]
print('Multi legs (morning -> now):')
pb = pn = 1.0
for h, k, label in legs:
    b, n = before[h]['blend'][k], now[h]['blend'][k]
    pb *= b; pn *= n
    print(f'  {label:30} {100 * b:.1f}% -> {100 * n:.1f}%')
print(f'  All four: {100 * pb:.1f}% -> {100 * pn:.1f}%; fair price {1 / pb:.2f} -> {1 / pn:.2f}; '
      f'expected return per $1 at 15.80: {pn * 15.8:.2f}')
