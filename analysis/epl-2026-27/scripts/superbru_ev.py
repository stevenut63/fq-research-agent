"""Expected Superbru points for the user's GW6 picks v our picks, using the blended score matrices.
Scoring (per epl-predictions skill): exact 3; correct result and closeness < 1.5 -> 1.5; correct result -> 1; else 0.
Closeness = |GD diff| + |total goals diff| / 2. Slam: 7 correct results +1, 8-9 +2, 10 +3."""
import json, sys
import numpy as np
S = sys.argv[1]
fin = json.load(open(f'{S}/gw6_final.json')); dc = json.load(open(f'{S}/dc_model.json'))
user = ['2-0', '2-2', '2-1', '2-1', '1-2', '2-1', '1-1', '0-1', '1-2', '0-2']
order = ['Arsenal', 'Aston Villa', 'Chelsea', 'Ipswich Town', 'Sunderland AFC', 'Manchester United', 'Crystal Palace', 'Hull City AFC', 'Liverpool', 'Coventry City']
byhome = {g['home']: (g, f) for g, f in zip(fin, dc['forecast'])}
res = lambda x, y: 'H' if x > y else 'A' if x < y else 'D'
def pts(px, py, ax, ay):
    if (px, py) == (ax, ay): return 3.0
    if res(px, py) != res(ax, ay): return 0.0
    ci = abs((ax - ay) - (px - py)) + abs((px + py) - (ax + ay)) / 2
    return 1.5 if ci < 1.5 else 1.0
def adj_matrix(g, f):
    M = np.array(g.get('M_model') or f['M']); M = M / M.sum()
    reg = {'H': np.tril(np.ones_like(M), -1), 'D': np.eye(len(M)), 'A': np.triu(np.ones_like(M), 1)}
    return sum(M * reg[k] / (M * reg[k]).sum() * p for k, p in zip('HDA', g['blend']))
def ev(A, pick):
    px, py = map(int, pick.split('-'))
    return sum(A[x, y] * pts(px, py, x, y) for x in range(6) for y in range(6))
def p_result(A, pick):
    px, py = map(int, pick.split('-')); r = res(px, py)
    return sum(A[x, y] for x in range(6) for y in range(6) if res(x, y) == r)
def slam_ev(ps):
    dist = np.zeros(11); dist[0] = 1
    for p in ps: dist = np.concatenate([dist[:1] * (1 - p), dist[1:] * (1 - p) + dist[:-1] * p])
    bonus = sum(dist[k] * (1 if k == 7 else 2 if k in (8, 9) else 3 if k == 10 else 0) for k in range(11))
    return bonus, float(dist[:].dot(np.arange(11))), float(dist[7:].sum())
rows = []; tot = {'user': [], 'ours': [], 'best': []}; pr = {'user': [], 'ours': [], 'best': []}
cands = [f'{x}-{y}' for x in range(5) for y in range(5)]
for h, up in zip(order, user):
    g, f = byhome[h]; A = adj_matrix(g, f)
    best = max(cands, key=lambda c: ev(A, c))
    for k, pick in (('user', up), ('ours', g['score']), ('best', best)):
        tot[k].append(ev(A, pick)); pr[k].append(p_result(A, pick))
    rows.append((h, g['away'], up, g['score'], best, ev(A, up), ev(A, g['score']), ev(A, best), p_result(A, up), p_result(A, g['score']), float(A[tuple(map(int, up.split('-')))]), float(A[tuple(map(int, g['score'].split('-')))])))
    print(f"{h[:14]:14} v {g['away'][:14]:14} you {up} (EV {ev(A, up):.2f}, P(res) {p_result(A, up):.0%}, P(exact) {A[tuple(map(int, up.split('-')))]:.1%})  ours {g['score']} (EV {ev(A, g['score']):.2f}, P(exact) {A[tuple(map(int, g['score'].split('-')))]:.1%})  EV-max {best} ({ev(A, best):.2f})")
for k in tot:
    b, ec, p7 = slam_ev(pr[k])
    print(f"{k:5}: EV points {sum(tot[k]):.2f} + slam {b:.2f} = {sum(tot[k]) + b:.2f}; expected correct results {ec:.2f}; P(7+ correct) {p7:.1%}")
json.dump(rows, open(f'{S}/superbru_ev.json', 'w'), indent=1)
