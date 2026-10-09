# EPL 2026-27: prediction accuracy and Matchweek 6 forecast

Prepared 9 October 2026. The report is `EPL_2026-27_Prediction_Accuracy_and_MW6_Forecast.docx`.

## Contents

- `work/results_2026-27.csv`: results for Matchweeks 1 to 5 (source: openfootball/football.json).
- `work/opta_mw/mw*.csv`: Opta pre-match probabilities rebuilt for each matchweek, with source URL and verification status for each match (VERIFIED, DERIVED, NOT_FOUND).
- `work/gw6/agent_*.json`: research inputs for Matchweek 6 (Opta, odds, team news, analyst probabilities).
- `work/*.json`: scored outputs (Opta, market comparison, Dixon-Coles back-test and forecast, final Matchweek 6 blend).
- `scripts/`: the scoring, model, blending and report-building scripts.

## Re-running

The scripts take the working folder as their first argument. They also need the football-data.co.uk odds files under `work/bettingdata/refresh/`. These are not committed because of their size (about 6 MB). They come from the GitHub mirror `AnishKhetani/premier-league-data`, commit `4930a1f`, at `data/processed/results_with_odds.csv` and `results.csv`.

```
python3 scripts/score_opta.py work && python3 scripts/combine.py work
python3 scripts/dixon_coles.py work && python3 scripts/blend_gw6.py work
node scripts/build_report.js work EPL_2026-27_Prediction_Accuracy_and_MW6_Forecast.docx
```
