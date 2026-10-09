"""Blend market, Opta, Dixon-Coles model and analyst-agent probabilities for MW6; pick correct scores."""
import json, glob, sys
import numpy as np
S = sys.argv[1]
W = dict(market=0.35, opta=0.25, model=0.20, analyst=0.20)
dc = json.load(open(f'{S}/dc_model.json'))
agents = [x for f in sorted(glob.glob(f'{S}/gw6/agent_*.json')) for x in json.load(open(f))]
try:
    ADJ = json.load(open(f'{S}/gw6/adjustments.json'))
except FileNotFoundError:
    ADJ = {}
from scipy.stats import poisson
def dc_matrix(lh, la, rho, n=6):
    M = np.zeros((n, n))
    for x in range(n):
        for y in range(n):
            t = {(0, 0): 1 - lh * la * rho, (0, 1): 1 + lh * rho, (1, 0): 1 + la * rho, (1, 1): 1 - rho}.get((x, y), 1.0)
            M[x, y] = poisson.pmf(x, lh) * poisson.pmf(y, la) * t
    return M / M.sum()
def apply_adjustment(fc):
    a = ADJ.get(f"{fc['home']} v {fc['away']}")
    if not a: return fc, None
    lh, la = fc['xg_h'] * a.get('home_xg_mult', 1), fc['xg_a'] * a.get('away_xg_mult', 1)
    M = dc_matrix(lh, la, dc['rho'])
    ph, pd, pa = float(np.tril(M, -1).sum()), float(np.trace(M)), float(np.triu(M, 1).sum())
    return dict(fc, xg_h=lh, xg_a=la, ph=ph, pd=pd, pa=pa, M=M.tolist()), a['reason']
def norm3(d, pct=False, odds=False):
    v = [float(d[k]) for k in 'hda']
    if odds: v = [1 / x for x in v]
    s = sum(v); return [x / s for x in v]
out = []
for fc, ag in zip(dc['forecast'], agents):
    fc, adj_reason = apply_adjustment(fc)
    src = dict(market=norm3(ag['odds'], odds=True), opta=norm3(ag['opta']),
               model=[fc['ph'], fc['pd'], fc['pa']], analyst=norm3(ag['my_probs']))
    b = np.sum([W[k] * np.array(v) for k, v in src.items()], axis=0)
    b = b / b.sum()
    ph, pd, pa = b
    call = ('H' if ph >= pa else 'A') if max(ph, pa) >= 0.40 else 'D'
    M = np.array(fc['M'])
    reg = {'H': np.tril(np.ones_like(M), -1), 'D': np.eye(len(M)), 'A': np.triu(np.ones_like(M), 1)}
    adj = sum(M * reg[k] / (M * reg[k]).sum() * p for k, p in zip('HDA', b))
    masked = adj * reg[call]
    x, y = np.unravel_index(np.argmax(masked), M.shape)
    flat = sorted(((float(adj[i, j]), f'{i}-{j}') for i in range(6) for j in range(6)), reverse=True)
    alts = [s for p, s in flat if s != f'{x}-{y}'][:2]
    conf = 'High' if max(b) >= 0.60 else 'Medium' if max(b) >= 0.45 else 'Low'
    out.append(dict(home=ag['home'], away=ag['away'], kickoff=ag['kickoff'], src=src, blend=b.tolist(), call=call,
                    score=f'{x}-{y}', p_score=float(adj[x, y]), alts=alts, conf=conf,
                    btts=fc['btts'], o25=fc['o25'], xg=(fc['xg_h'], fc['xg_a']), analyst_score=ag['primary_score'], M_model=fc['M'], adjustment=adj_reason))
    print(f"{ag['home'][:16]:16} v {ag['away'][:16]:16} mkt {[round(100*x) for x in src['market']]} opta {[round(100*x) for x in src['opta']]} "
          f"model {[round(100*x) for x in src['model']]} analyst {[round(100*x) for x in src['analyst']]} => blend {[round(100*x) for x in b]} "
          f"call {call} score {x}-{y} ({adj[x,y]:.1%}) alts {alts} [{ag['primary_score']}] {conf}")
json.dump(out, open(f'{S}/gw6_final.json', 'w'), indent=1)
print('draws called:', sum(o['call'] == 'D' for o in out))
