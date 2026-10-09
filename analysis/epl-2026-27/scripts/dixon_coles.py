"""Time-weighted Dixon-Coles model for EPL 2026-27.

- Data: EPL results 2023-24 to date (football-data.co.uk via GitHub mirror) + openfootball 2026-27.
- Weights: exponential decay with half-life HALF_LIFE days.
- Promoted sides with no top-flight data in the window are shrunk to a promoted-team prior
  estimated from recent promoted sides' first seasons.
- Back-test: refit before each 2026-27 matchweek and score MW1-5 with both accuracy methods.
- Forecast: MW6 score matrices.
"""
import csv, json, math, sys
from datetime import date
import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson

S = sys.argv[1]
HALF_LIFE = 240.0
XI = math.log(2) / HALF_LIFE
MAXG = 10
NAME = {"Nott'm Forest": 'Nottingham Forest', 'Man United': 'Manchester United', 'Man City': 'Manchester City',
        'Hull': 'Hull City', 'Hull City AFC': 'Hull City', 'Sunderland AFC': 'Sunderland',
        'Brighton & Hove Albion': 'Brighton', 'Tottenham Hotspur': 'Tottenham', 'Tottenham': 'Tottenham',
        'Newcastle United': 'Newcastle', 'Leeds United': 'Leeds', 'Ipswich Town': 'Ipswich',
        'Coventry City': 'Coventry', 'Wolverhampton Wanderers': 'Wolves', 'West Ham United': 'West Ham',
        'Leicester City': 'Leicester', 'Luton Town': 'Luton', 'Sheffield United': 'Sheffield United',
        "Sheffield Utd": 'Sheffield United'}
nm = lambda t: NAME.get(t.strip(), t.strip())

matches = []
for r in csv.DictReader(open(f'{S}/bettingdata/refresh/results.csv')):
    if r['season'] in ('2023-24', '2024-25', '2025-26'):
        matches.append(dict(season=r['season'], d=date.fromisoformat(r['date'][:10]), h=nm(r['home_team']),
                            a=nm(r['away_team']), hg=int(r['fthg']), ag=int(r['ftag']), mw=None))
for r in csv.DictReader(open(f'{S}/results_2026-27.csv')):
    matches.append(dict(season='2026-27', d=date.fromisoformat(r['date']), h=nm(r['home']), a=nm(r['away']),
                        hg=int(r['hg']), ag=int(r['ag']), mw=int(r['matchweek'])))

def tau(x, y, lh, la, rho):
    if x == 0 and y == 0: return 1 - lh * la * rho
    if x == 0 and y == 1: return 1 + lh * rho
    if x == 1 and y == 0: return 1 + la * rho
    if x == 1 and y == 1: return 1 - rho
    return 1.0

def fit(train, ref_date, priors, lam=3.0):
    teams = sorted({m['h'] for m in train} | {m['a'] for m in train} | set(priors))
    idx = {t: i for i, t in enumerate(teams)}; n = len(teams)
    H = np.array([idx[m['h']] for m in train]); A = np.array([idx[m['a']] for m in train])
    hg = np.array([m['hg'] for m in train]); ag = np.array([m['ag'] for m in train])
    w = np.array([math.exp(-XI * (ref_date - m['d']).days) for m in train])
    pa = np.array([priors.get(t, (0.0, 0.0))[0] for t in teams])
    pd_ = np.array([priors.get(t, (0.0, 0.0))[1] for t in teams])
    pw = np.array([lam if t in priors else 0.05 for t in teams])  # weak ridge for established sides
    def nll(p):
        att, dfn = p[:n], p[n:2 * n]; home, rho, mu = p[2 * n], p[2 * n + 1], p[2 * n + 2]
        lh = np.exp(mu + att[H] + dfn[A] + home); la = np.exp(mu + att[A] + dfn[H])
        ll = hg * np.log(lh) - lh + ag * np.log(la) - la
        t = np.ones_like(lh)
        m00 = (hg == 0) & (ag == 0); m01 = (hg == 0) & (ag == 1); m10 = (hg == 1) & (ag == 0); m11 = (hg == 1) & (ag == 1)
        t[m00] = 1 - lh[m00] * la[m00] * rho; t[m01] = 1 + lh[m01] * rho; t[m10] = 1 + la[m10] * rho; t[m11] = 1 - rho
        ll = ll + np.log(np.clip(t, 1e-9, None))
        pen = np.sum(pw * ((att - pa) ** 2 + (dfn - pd_) ** 2)) + 100 * np.mean(att) ** 2
        return -np.sum(w * ll) + pen
    x0 = np.concatenate([np.zeros(n), np.zeros(n), [0.25, -0.05, 0.3]])
    res = minimize(nll, x0, method='L-BFGS-B',
                   bounds=[(-3, 3)] * (2 * n) + [(-1, 1), (-0.3, 0.3), (-2, 2)])
    p = res.x
    return dict(att={t: p[idx[t]] for t in teams}, dfn={t: p[n + idx[t]] for t in teams},
                home=p[2 * n], rho=p[2 * n + 1], base=p[2 * n + 2], converged=bool(res.success))

def matrix(model, h, a):
    lh = math.exp(model['att'][h] + model['dfn'][a] + model['home'] + model['base'])
    la = math.exp(model['att'][a] + model['dfn'][h] + model['base'])
    M = np.zeros((MAXG + 1, MAXG + 1))
    for x in range(MAXG + 1):
        for y in range(MAXG + 1):
            M[x, y] = poisson.pmf(x, lh) * poisson.pmf(y, la) * tau(x, y, lh, la, model['rho'])
    M /= M.sum()
    return M, lh, la

def outcome(M):
    return float(np.tril(M, -1).sum()), float(np.trace(M)), float(np.triu(M, 1).sum())

# --- Promoted-team prior: fit on all pre-2026-27 data and average promoted sides' first-season ratings ---
promoted_first = {'2023-24': ['Burnley', 'Luton', 'Sheffield United'], '2024-25': ['Ipswich', 'Leicester', 'Southampton'],
                  '2025-26': ['Leeds', 'Burnley', 'Sunderland']}
pa_list, pd_list = [], []
for season, sides in promoted_first.items():
    sub = [m for m in matches if m['season'] == season]
    end = max(m['d'] for m in sub)
    mdl = fit(sub, end, {}, lam=0)
    for t in sides:
        pa_list.append(mdl['att'][t]); pd_list.append(mdl['dfn'][t])
PRIOR = (float(np.mean(pa_list)), float(np.mean(pd_list)))
print('Promoted prior (att, def):', [round(x, 3) for x in PRIOR], file=sys.stderr)

def priors_for(train_ids):
    # Coventry and Hull have no top-flight data in the window; Ipswich's 2024-25 data is decayed, so give it the prior too
    return {t: PRIOR for t in ('Coventry', 'Hull City', 'Ipswich')}

# --- Back-test on 2026-27 MW1-5 ---
bt = []
for mw in range(1, 6):
    test = [m for m in matches if m['mw'] == mw]
    train = [m for m in matches if m['mw'] is None or m['mw'] < mw]
    ref = min(m['d'] for m in test)
    mdl = fit(train, ref, priors_for(train))
    for m in test:
        M, lh, la = matrix(mdl, m['h'], m['a'])
        ph, pdw, pa = outcome(M)
        ftr = 'H' if m['hg'] > m['ag'] else 'A' if m['hg'] < m['ag'] else 'D'
        m1 = max({'H': ph, 'D': pdw, 'A': pa}.items(), key=lambda kv: kv[1])[0]
        m2 = ('H' if ph >= pa else 'A') if max(ph, pa) >= 0.40 else 'D'
        x, y = np.unravel_index(np.argmax(M), M.shape)
        bt.append(dict(mw=mw, h=m['h'], a=m['a'], score=f"{m['hg']}-{m['ag']}", ftr=ftr, ph=ph, pd=pdw, pa=pa,
                       m1=m1, m2=m2, top=f'{x}-{y}', exact=(x == m['hg'] and y == m['ag']),
                       brier=sum((p - (k == ftr)) ** 2 for k, p in zip('HDA', (ph, pdw, pa)))))
n = len(bt)
summ = dict(n=n, m1=sum(b['m1'] == b['ftr'] for b in bt), m2=sum(b['m2'] == b['ftr'] for b in bt),
            exact=sum(b['exact'] for b in bt), brier=sum(b['brier'] for b in bt) / n)
print('Back-test', summ, file=sys.stderr)

# --- MW6 forecast ---
fixtures = [('Arsenal', 'Leeds'), ('Sunderland', 'Brighton'), ('Chelsea', 'Bournemouth'), ('Ipswich', 'Fulham'),
            ('Aston Villa', 'Brentford'), ('Manchester United', 'Tottenham'), ('Hull City', 'Everton'),
            ('Crystal Palace', 'Nottingham Forest'), ('Liverpool', 'Manchester City'), ('Coventry', 'Newcastle')]
mdl = fit(matches, date(2026, 10, 10), priors_for(matches))
fc = []
for h, a in fixtures:
    M, lh, la = matrix(mdl, h, a)
    ph, pdw, pa = outcome(M)
    flat = sorted(((float(M[x, y]), f'{x}-{y}') for x in range(6) for y in range(6)), reverse=True)[:5]
    fc.append(dict(home=h, away=a, xg_h=lh, xg_a=la, ph=ph, pd=pdw, pa=pa, top5=flat,
                   btts=float(1 - M[0, :].sum() - M[:, 0].sum() + M[0, 0]),
                   o25=float(sum(M[x, y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x + y >= 3)),
                   M=M[:6, :6].round(4).tolist()))
    print(f"{h:18} v {a:18} xG {lh:.2f}-{la:.2f}  H {ph:.0%} D {pdw:.0%} A {pa:.0%}  top: " +
          ', '.join(f'{s} {p:.1%}' for p, s in flat[:3]), file=sys.stderr)
json.dump(dict(prior=PRIOR, half_life=HALF_LIFE, home=mdl['home'], rho=mdl['rho'], backtest=summ, bt=bt, forecast=fc,
               ratings={t: (mdl['att'][t], mdl['dfn'][t]) for t in sorted({f[0] for f in fixtures} | {f[1] for f in fixtures})}),
          open(f'{S}/dc_model.json', 'w'), indent=1, default=float)
