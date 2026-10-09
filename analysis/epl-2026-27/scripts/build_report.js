// Builds the EPL 2026-27 prediction accuracy and MW6 forecast report (.docx, Open Sans).
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, BorderStyle, LevelFormat, Footer, PageNumber, TableLayoutType,
} = require('docx');

const S = process.argv[2];
const OUT = process.argv[3];
const combined = JSON.parse(fs.readFileSync(path.join(S, 'combined.json')));
const gw6 = JSON.parse(fs.readFileSync(path.join(S, 'gw6_final.json')));
const dc = JSON.parse(fs.readFileSync(path.join(S, 'dc_model.json')));

const FONT = 'Open Sans';
const DARK = '333C46', NAVY = '093D58', BLUE = '2DA9E1', LIGHT = 'E2F5FE', GREY = '929496';
const GREEN = 'E3F6EC', RED = 'FBE4E1';
const CONTENT_W = 9638; // A4 with 2 cm margins

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 20, bold: o.bold, italics: o.italics, color: o.color || DARK });
const p = (text, o = {}) => new Paragraph({
  spacing: { after: o.after ?? 120, before: o.before ?? 0, line: 276 }, alignment: o.align,
  children: Array.isArray(text) ? text : [run(text, o)],
});
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 280, after: 120 }, children: [new TextRun({ text: t, font: FONT, size: 30, bold: true, color: NAVY })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 80 }, children: [new TextRun({ text: t, font: FONT, size: 24, bold: true, color: NAVY })] });
const bullet = (parts) => new Paragraph({ numbering: { reference: 'bul', level: 0 }, spacing: { after: 60, line: 276 },
  children: (Array.isArray(parts) ? parts : [parts]).map((x) => (typeof x === 'string' ? run(x) : x)) });
const b = (t) => run(t, { bold: true });

const border = { style: BorderStyle.SINGLE, size: 4, color: 'D0D3D6' };
const borders = { top: border, bottom: border, left: border, right: border };
function table(headers, rows, widths, o = {}) {
  const total = widths.reduce((a, c) => a + c, 0);
  const sz = o.size || 16;
  const mk = (txt, w, opts = {}) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: { top: 50, bottom: 50, left: 80, right: 80 },
    children: [new Paragraph({ alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({ text: String(txt), font: FONT, size: sz, bold: opts.bold, color: opts.color || DARK })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => mk(h, widths[i], { fill: NAVY, bold: true, color: 'FFFFFF', align: i ? AlignmentType.CENTER : AlignmentType.LEFT })) }),
      ...rows.map((r, ri) => new TableRow({ children: r.map((c, i) => {
        const cell = typeof c === 'object' && c !== null ? c : { t: c };
        return mk(cell.t, widths[i], { fill: cell.fill || (ri % 2 ? 'F6F8FA' : undefined), bold: cell.bold, align: i ? AlignmentType.CENTER : AlignmentType.LEFT });
      }) })),
    ],
  });
}
const pct = (x, d = 0) => `${(100 * x).toFixed(d)}%`;
const short = (t) => t.replace(' AFC', '').replace('Brighton & Hove Albion', 'Brighton').replace('Manchester United', 'Man Utd')
  .replace('Manchester City', 'Man City').replace('Tottenham Hotspur', 'Tottenham').replace('Nottingham Forest', "Nott'm Forest")
  .replace('Newcastle United', 'Newcastle').replace('Leeds United', 'Leeds').replace('Ipswich Town', 'Ipswich').replace('Coventry City', 'Coventry').replace('Hull City', 'Hull');
const RES = { H: 'Home', D: 'Draw', A: 'Away' };

// ---------- figures ----------
const oc = combined.opta_cov, mc = combined.market_cov, ma = combined.market_all, mn = combined.market_nocov;
const rows = combined.rows;
const estM1 = oc.m1 + mn.m1, estM2 = oc.m2 + mn.m2; // proxy: market picks on uncovered matches
const bt = dc.backtest;

const children = [];
children.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: 'Premier League 2026-27', font: FONT, size: 22, bold: true, color: BLUE })] }));
children.push(new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: 'How accurate is the Opta supercomputer, who predicts best, and our Matchweek 6 forecast', font: FONT, size: 36, bold: true, color: NAVY })] }));
children.push(p('Prepared 9 October 2026. Covers Matchweeks 1 to 5 (50 matches, 21 August to 20 September 2026) and forecasts for Matchweek 6 (10 to 12 October 2026).', { italics: true, color: GREY, size: 18, after: 240 }));

// ---------- 1. Summary ----------
children.push(h1('1. Summary'));
children.push(bullet([b('Opta, verified sample: '), run(`On the 28 matches where Opta's pre-match probabilities could be confirmed, the supercomputer called ${oc.m1}/28 (${pct(oc.m1 / 28)}) correctly using its highest probability (Method 1) and ${oc.m2}/28 (${pct(oc.m2 / 28)}) using the 40% rule (Method 2).`)]));
children.push(bullet([b('Opta, full season estimate: '), run(`The 28 matches found are biased towards easier games. The betting market called ${pct(mc.m1_pct / 100)} of them correctly but only ${pct(mn.m1_pct / 100)} of the 22 that could not be found. Because Opta and the market made the same pick in 26 of the 28 verified matches, the best estimate for all 50 matches is about ${estM1}/50 (${pct(estM1 / 50)}) on Method 1 and ${estM2}/50 (${pct(estM2 / 50)}) on Method 2.`)]));
children.push(bullet([b('Method 2 beats Method 1 this season '), run('because 16 of 50 matches (32%) have been drawn, well above the usual 23 to 25%. In none of the 28 verified matches was a draw Opta\'s single most likely outcome, so Method 1 could not score on draws; the 40% rule picked up two 0-0 draws Opta otherwise got wrong.')]));
children.push(bullet([b('Who is most accurate? '), run(`No predictor is demonstrably better than the betting market. The market's closing odds called ${ma.m1}/50 (${pct(ma.m1 / 50)}) and ${ma.m2}/50 (${pct(ma.m2 / 50)}) on the 40% rule. The best published third-party record is Squawka's AI predictor (self-reported 47.5% on 40 matches). Our own Dixon-Coles model, back-tested without look-ahead, scored ${bt.m1}/50 (${pct(bt.m1 / 50)}) with ${bt.exact} exact scores. With 50 matches the margin of error is about plus or minus 14 points, so none of these gaps is statistically meaningful.`)]));
children.push(bullet([b('Matchweek 6: '), run('Our blended forecast calls 4 home wins, 3 draws and 3 away wins. The most confident pick is Arsenal 1-0 Leeds (66% home win). Seven of the ten picks are low confidence, which reflects how evenly matched most fixtures are.')]));

// ---------- 2. Data and method ----------
children.push(h1('2. Data and method'));
children.push(h2('Sources'));
children.push(bullet([b('Results: '), run('openfootball (GitHub), cross-checked against a GitHub mirror of football-data.co.uk. All 50 scores agree.')]));
children.push(bullet([b('Opta probabilities: '), run('The Analyst (theanalyst.com) publishes Opta win, draw and loss percentages before each match. Its weekly predictions page is overwritten every matchweek, so earlier weeks had to be rebuilt from The Analyst\'s per-fixture pages and outlets that quote them (Al Jazeera, legit.ng, Yahoo Sports, club fan sites). Only figures explicitly attributed to Opta and dated to the 2026-27 fixture were accepted.')]));
children.push(bullet([b('Betting market: '), run('average closing odds across bookmakers (football-data.co.uk via GitHub mirror), with the bookmaker margin removed.')]));
children.push(bullet([b('Other predictors: '), run('three research agents searched for published 2026-27 records from human pundits, machine and AI models, and prediction competitions.')]));
children.push(h2('Scoring rules'));
children.push(bullet([b('Method 1 (highest probability): '), run('the predicted outcome is whichever of home win, draw or away win has the highest probability.')]));
children.push(bullet([b('Method 2 (40% threshold): '), run('a team is predicted to win only if its win probability is 40% or more; if neither team reaches 40%, the prediction is a draw.')]));
children.push(bullet([b('Brier score '), run('(reported where possible) measures the quality of the probabilities themselves, not just the pick; 0 is perfect and lower is better.')]));
children.push(h2('Limitations'));
children.push(bullet('This environment\'s network policy blocked direct access to theanalyst.com, premierleague.com, the Wayback Machine and most news sites. All Opta figures were obtained through search-engine summaries of those pages rather than the pages themselves, so transcription errors are possible.'));
children.push(bullet(`Opta figures were confirmed for 28 of 50 matches (${combined.rows.filter((r) => r.status === 'VERIFIED').length} with all three figures published; the rest have the draw derived as 100 minus the two win figures). The other 22 could not be found and were not estimated.`));
children.push(bullet('One figure (Bournemouth v Liverpool, 31.6 / 24.2 / 44.2) comes from a single translated source and the same three numbers were also attributed to an unrelated match elsewhere. Excluding it changes the verified results to 14/27 (52%) on Method 1 and 16/27 (59%) on Method 2.'));

// ---------- 3. Opta accuracy ----------
children.push(h1('3. Opta supercomputer accuracy'));
children.push(h2('Headline results'));
children.push(table(
  ['Measure', 'Matches', 'Method 1: highest %', 'Method 2: 40% rule', 'Brier'],
  [
    ['Opta, verified matches', '28', `${oc.m1} (${pct(oc.m1 / 28)})`, `${oc.m2} (${pct(oc.m2 / 28)})`, oc.brier.toFixed(3)],
    ['Betting market, same 28 matches', '28', `${mc.m1} (${pct(mc.m1 / 28)})`, `${mc.m2} (${pct(mc.m2 / 28)})`, mc.brier.toFixed(3)],
    ['Betting market, 22 matches without Opta data', '22', `${mn.m1} (${pct(mn.m1 / 22)})`, `${mn.m2} (${pct(mn.m2 / 22)})`, mn.brier.toFixed(3)],
    [{ t: 'Opta, estimated for all 50 matches', bold: true }, '50', { t: `c. ${estM1} (${pct(estM1 / 50)})`, bold: true }, { t: `c. ${estM2} (${pct(estM2 / 50)})`, bold: true }, 'n/a'],
    ['Betting market, all 50 matches', '50', `${ma.m1} (${pct(ma.m1 / 50)})`, `${ma.m2} (${pct(ma.m2 / 50)})`, ma.brier.toFixed(3)],
    ['Baseline: always pick the home team', '50', '18 (36%)', 'n/a', 'n/a'],
  ], [3638, 900, 1800, 1800, 1500]));
children.push(p('', { after: 60 }));
children.push(p('How to read this: on a like-for-like basis Opta and the betting market are effectively level. Opta edges the market on Method 2 (17 v 16 correct) and on Brier score (0.584 v 0.586), but the market edges Opta on Method 1 (16 v 15). The two agree on the pick in 26 of 28 matches. The full-season estimate assumes Opta would have made the same picks as the market on the 22 missing matches, which is consistent with that 93% agreement rate; treat it as plus or minus two correct calls.'));
children.push(h2('Where Opta and the market differed'));
children.push(bullet([b('Nottingham Forest 0-0 Tottenham: '), run('Opta 39.5 / 27.2 / 33.4. Method 1 picked Forest; Method 2 called a draw (correct).')]));
children.push(bullet([b('Hull 0-0 Aston Villa: '), run('Opta 34.8 / 25.9 / 39.3. Method 1 picked Villa; Method 2 called a draw (correct). The market had Villa above 40%, so it was wrong on both methods.')]));
children.push(bullet([b('Brentford 3-0 Chelsea: '), run('Opta 35.4 / 24.3 / 40.3 made Chelsea favourites (wrong). The market had Brentford narrowly ahead.')]));
children.push(h2('By matchweek (verified matches only)'));
const byMw = [1, 2, 3, 4, 5].map((w) => {
  const s = rows.filter((r) => r.mw === w && r.ph !== null);
  const m1 = s.filter((r) => r.m1 === r.ftr).length, m2 = s.filter((r) => r.m2 === r.ftr).length;
  const dr = rows.filter((r) => r.mw === w && r.ftr === 'D').length;
  return [`Matchweek ${w}`, `${s.length} of 10`, `${m1} (${pct(m1 / s.length)})`, `${m2} (${pct(m2 / s.length)})`, `${dr} of 10`];
});
children.push(table(['Matchweek', 'Opta found', 'Method 1', 'Method 2', 'Draws (all matches)'], byMw, [2238, 1700, 1900, 1900, 1900]));

// ---------- 4. Other predictors ----------
children.push(h1('4. How other predictors compare'));
children.push(p('Ranked by result accuracy. Evidence strength matters more than the ranking: most third-party figures are self-reported, cover only part of the season, or both.'));
children.push(table(
  ['Predictor', 'Type', 'Matches', 'Correct result', 'Evidence'],
  [
    ['Our Dixon-Coles model (back-test)', 'Statistical model', '50', `${pct(bt.m1 / 50)} (both methods); ${bt.exact} exact`, 'Verified (our calculation)'],
    ['Opta supercomputer, Method 2 (est.)', 'Simulation model', '50', `c. ${pct(estM2 / 50)}`, 'Estimated from 28 verified'],
    ['Betting market, 40% rule', 'Market', '50', pct(ma.m2 / 50), 'Verified'],
    ['Squawka AI Predictor', 'Team-strength model', '40', '47.5% (10% exact)', 'Self-reported'],
    ['Betting market favourite', 'Market', '50', pct(ma.m1 / 50), 'Verified'],
    ['ScoreSocial "Jim\'s v3"', 'Algorithm', '20', '45%', 'Self-reported, partial'],
    ['Chris Sutton (BBC Sport)', 'Human pundit', '18', '44% (2 exact)', 'Partial reconstruction'],
    ['Opta supercomputer, Method 1 (est.)', 'Simulation model', '50', `c. ${pct(estM1 / 50)}`, 'Estimated from 28 verified'],
    ['Jones Knows (Sky Sports)', 'Human pundit', '5', '40%', 'Very small sample'],
    ['Always pick home team', 'Baseline', '50', '36%', 'Verified'],
    ['Footballmeister "Coach AI"', 'AI model', '50', '34%', 'Self-reported'],
  ], [2900, 1700, 900, 2238, 1900]));
children.push(p('', { after: 60 }));
children.push(h2('Verdict'));
children.push(p('On the evidence available, the most accurate verifiable predictor this season is the betting market (46% favourite, 48% on the 40% rule), with Opta effectively tied once the coverage bias is allowed for. Squawka\'s AI predictor has the best published third-party record, but it is self-reported and only covers matches up to Matchweek 4. Our own model has the highest back-tested hit rate (50%) and the best Brier score (0.613 against the market\'s 0.636), but the margin is two or three matches and we built it, so it should be treated as competitive rather than superior.'));
children.push(p('Among human pundits, nobody publishes an auditable season tally. Chris Sutton has the most verifiable data (4 of 10 correct in Matchweek 5, confirmed by BBC). A third-party points table (betandskill.com) puts Jones Knows ahead of Sutton, but its figures are inconsistent across pages and could not be verified.'));
children.push(p('Large public competitions (Sky Bet Super 6, Superbru) publish points leaderboards that cannot be converted to accuracy rates, and the Premier League no longer runs a weekly match predictor.'));

// ---------- 5. MW6 forecast ----------
children.push(h1('5. Matchweek 6 forecast'));
children.push(p('Each fixture combines four independent inputs: the betting market (35% weight), Opta (25%), our Dixon-Coles model (20%) and an analyst agent\'s judgement based on team news, form and underlying numbers (20%). The result is called with the 40% rule, which has worked better than "highest probability" in this draw-heavy season. The correct score is the most likely scoreline within that result, taken from the model\'s score matrix after rescaling it to the blended probabilities.'));
children.push(table(
  ['Fixture', 'Home / Draw / Away', 'Call', 'Score', 'Alternatives', 'Conf.'],
  gw6.map((g) => [`${short(g.home)} v ${short(g.away)}`, g.blend.map((x) => Math.round(100 * x)).join(' / '), RES[g.call],
    { t: g.score, bold: true }, g.alts.join(', '), g.conf]),
  [2838, 1700, 900, 900, 1800, 1500]));
children.push(p('', { after: 60 }));
children.push(p(`Draws called: 3 of 10. Model expected goals and source-by-source probabilities are in the appendix.`, { italics: true, color: GREY, size: 18 }));
children.push(h2('Fixture notes'));
const notes = {
  'Arsenal': 'All four sources agree Arsenal are clear favourites (60 to 69%). Leeds are unbeaten and have conceded three in five, which favours a tight 1-0 over a rout. Saliba\'s fitness is disputed.',
  'Sunderland AFC': 'Brighton narrowly clear 40% (42%) despite a long injury list (Mitoma, Minteh, Wieffer, Ferguson out). 1-1 is almost as likely as 1-2; this is the best candidate to switch to a draw.',
  'Chelsea': 'Chelsea are favoured but winless in three and conceding 2.4 a game, with Palmer and Joao Pedro doubts. Every Chelsea league match has had three or more goals.',
  'Ipswich Town': 'Opta favours Ipswich (45%), the market and our model favour Fulham. The blend is a near three-way split, so the 40% rule calls a draw.',
  'Aston Villa': 'Opta has Villa at 48%, the market has Brentford marginally ahead. The blend gives Villa 39.8%, fractionally below the threshold, so this is a draw call on a knife-edge; 2-1 Villa is the alternative.',
  'Manchester United': 'Tottenham have scored two goals in five games and are without Porro; United are strong favourites in every source (50 to 57%). 2-1 edges 2-0 in the model.',
  'Hull City AFC': 'Everton are unbeaten and Opta\'s strongest away pick of the round (45.7%). Hull\'s results flatter their underlying numbers. Low-scoring: 0-1 or 0-0.',
  'Crystal Palace': 'The most even fixture of the round (35 / 30 / 35). Both sides are missing first-choice strikers and six of the last eight meetings were drawn.',
  'Liverpool': 'Opta (40.7%), the market and our model all lean City. Liverpool are without Isak, Gakpo and Ekitike; City are without Foden. City sit at 40.2%, only just over the threshold, so this is a marginal away call.',
  'Coventry City': 'Coventry have scored once in five games and are without both first-choice strikers. Newcastle\'s underlying numbers are poor, so a narrow 0-1 rather than a heavy defeat.',
};
gw6.forEach((g) => children.push(bullet([b(`${short(g.home)} ${g.score} ${short(g.away)}: `), run(notes[g.home] || '')])));

// ---------- 6. Next steps ----------
children.push(h1('6. Recommendations'));
children.push(bullet('To close the Opta gap properly, allow theanalyst.com and web.archive.org in the environment\'s network settings; archived snapshots of each week\'s predictions page would give exact figures for all 50 matches.'));
children.push(bullet('From Matchweek 6 onwards, capture Opta\'s figures each week before the page is overwritten. This turns the comparison into a clean, prospective test.'));
children.push(bullet('Judge predictors on Brier score as well as hit rate. Hit rates over a few dozen matches are dominated by luck; probability quality separates good models more quickly.'));

// ---------- Appendix ----------
children.push(h1('Appendix A. Match-level data, Matchweeks 1 to 5'));
children.push(p('Opta and market figures are home / draw / away percentages. Y or N shows whether Method 1 / Method 2 was correct (green: Method 2 correct; red: Method 2 wrong). A dash means no verified Opta figure was found.', { size: 18, color: GREY }));
const tick = (ok) => (ok ? 'Y' : 'N');
const appRows = rows.slice().sort((a, b2) => a.mw - b2.mw).map((r) => {
  const has = r.ph !== null;
  const fill = has ? (r.m2 === r.ftr ? GREEN : RED) : undefined;
  return [
    `MW${r.mw} ${short(r.home)} v ${short(r.away)}`, r.score,
    has ? `${r.ph.toFixed(1)} / ${r.pd.toFixed(1)} / ${r.pa.toFixed(1)}` : '-',
    has ? { t: `${tick(r.m1 === r.ftr)} / ${tick(r.m2 === r.ftr)}`, fill } : '-',
    `${Math.round(r.mh)} / ${Math.round(r.md)} / ${Math.round(r.ma)}`,
    `${tick(r.mk_m1 === r.ftr)} / ${tick(r.mk_m2 === r.ftr)}`,
  ];
});
children.push(table(['Match', 'Score', 'Opta H / D / A', 'Opta M1 / M2', 'Market H / D / A', 'Mkt M1 / M2'], appRows, [3038, 700, 1800, 1100, 1800, 1200], { size: 14 }));

children.push(h1('Appendix B. Matchweek 6 inputs by source'));
children.push(table(['Fixture', 'Market', 'Opta', 'Model', 'Analyst', 'Model xG'],
  gw6.map((g) => [`${short(g.home)} v ${short(g.away)}`,
    ...['market', 'opta', 'model', 'analyst'].map((k) => g.src[k].map((x) => Math.round(100 * x)).join(' / ')),
    `${g.xg[0].toFixed(2)} - ${g.xg[1].toFixed(2)}`]),
  [2638, 1400, 1400, 1400, 1400, 1400], { size: 14 }));
children.push(p('', { after: 60 }));
children.push(p(`Model details: time-weighted Dixon-Coles (half-life ${dc.half_life} days) fitted to Premier League results from 2023-24 to Matchweek 5 of 2026-27. Promoted sides without recent top-flight data (Coventry, Hull, Ipswich) start from the average rating of recent promoted teams. Estimated home advantage is ${pct(Math.exp(dc.home) - 1)} more goals for the home side.`, { size: 18, color: GREY }));

const doc = new Document({
  creator: 'Fifth Quadrant', title: 'EPL 2026-27 prediction accuracy and MW6 forecast',
  styles: { default: { document: { run: { font: FONT, size: 20, color: DARK } } } },
  numbering: { config: [{ reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ font: FONT, size: 16, color: GREY, children: ['EPL 2026-27 prediction accuracy  |  Page ', PageNumber.CURRENT] })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log('written', OUT); });
