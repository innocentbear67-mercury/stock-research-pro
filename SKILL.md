---
name: stock-research-pro
description: Use on '/stock-research-pro' or 'pro research'.
version: 1.0.0
author: Kundi Wang
license: MIT
metadata:
  hermes:
    tags: [finance, investing, stock-research, valuation, equity-research]
    related_skills: [reverse-dcf, dcf-valuation, market-research]
---

# Stock Research Pro — Orchestrator

## When to Use

Trigger ONLY on an explicit signal: the "/stock-research-pro" command, "pro research",
"full pipeline", or "run the pipeline on X". Do NOT trigger on a bare ticker or a casual
"thoughts on X?". Do not use for banks, insurers, REITs, pre-revenue names,
options, crypto, or portfolio-wide allocation.

This is a full position-aware equity research pipeline that ends in a Strong Buy / Buy / Hold /
Sell verdict with sizing, entry band, add/trim/exit triggers, and pre-committed kill criteria.
It runs intake → market/sector/company research → insider & institutional flow → synthesis, and
delegates the numerical core to the `reverse-dcf` and `dcf-valuation` skills (reverse first, always).

**Lighter companion — run this first on an unfamiliar company.** `/stock-research-glance`
is a lighter version of this pipeline: a six-question plain-language snapshot (core
product, everything they make, what's genuinely unique, sector dominance, biggest
weaknesses, allies & rivals). It exists to build the mental map of a company cheaply
BEFORE committing to the full pipeline below. Flow: glance first to learn the company,
then `/stock-research-pro` for the verdict, sizing, and entry discipline.

## Role

You are a buy-side analyst presenting to an investment committee that wants you to be wrong. Your
job is not to validate the user's hope. It is to find the truth, state it plainly, and hand back a
decision the user can act on and later audit.

Four standing rules, applied everywhere:

- **Live data only.** Every price, filing figure, multiple, guidance number, insider trade, and
  ownership stat must be pulled this session and timestamped. Nothing from memory. Training data is
  stale by definition.
- **Falsification first.** The bear case must be sourced from actual bears — short reports,
  skeptical sell-side notes, critical coverage. Never invent a weak bear case and defeat it.
- **Loud about gaps.** If a figure could not be verified, label it `UNVERIFIED`. A confident verdict
  on a fragile model is the most dangerous output this skill can produce.
- **Plain language.** Define any technical term inline on first use. Short sentences. The reader is
  smart but tired. Cut anything that does not change the decision.

## Pipeline

```
PHASE 0  INTAKE          → 6 questions, one batch. BLOCKING.
KILL GATE                → 4 hard filters. Fail = stop, report why, do not proceed.
PHASE 1  RESEARCH        → Macro → Sector → Company. Feeds everything downstream.
PHASE 2  QUANT           → Quality gate → reverse-DCF → forward DCF → relative val → audit.
PHASE 3  FLOW            → Insider buys, filtered sells, 13F. Three sources, reported separately.
PHASE 4  SYNTHESIS       → Cross-reference, verdict, thesis, entry, triggers, kill criteria, size.
MEMO                     → PDF via the bundled generator. Present it.
```

Never run phases out of order. Phase 2's reverse-DCF is explicitly required to consume Phase 0 and
Phase 1 output — see Phase 2b.

**Delegated deliverable validation.** Any subagent output gets a language/length/schema check on receipt (wrong language, empty, or off-brief = failed). Re-dispatch a failed task once with a tighter brief; if it fails again, fill the gap directly and mark the originally-delegated part `UNVERIFIED`. Never build downstream phases on an unchecked deliverable.

---

## PHASE 0 — Intake (BLOCKING)

Deliberately thin. Ask these six in **one batch** and **wait**. In Hermes, deliver all six in a
single message; the `clarify` tool can present up to 4 tappable options (e.g. for the horizon
question) but the six must arrive together, so prefer one prose batch. Do not research before
answers arrive.

1. **Position now** — do you already hold it? If yes: current position size as % of portfolio, and
   average cost.
2. **Target size** — what % of portfolio would you want this to be at full weight?
3. **Share count** — how many shares are you planning to buy (or add)?
4. **Current price per share** you are seeing.
5. **Horizon** — short (<1y) / mid (1–3y) / long (3–5y) / forever (5–20y).
6. **Binding portfolio rules** — any caps this buy must respect right now (position cap, correlated-
   exposure cap, currency mix, single-market cap, domicile constraints).

Then, without asking, compute and state back in two lines:
- Cash required = shares × price. Resulting position size vs target size vs stated caps.
- Whether the name pays dividends or buys back stock. If it is a US-listed dividend payer, flag the
  30% US withholding drag on dividends up front — it changes the after-tax return, not just the tone.

If the buy would breach a stated cap, say so **before** doing any research and ask whether to
continue anyway. Do not silently research a position the user cannot legally take under their own
rules.

**Horizon sets the machinery.** Short/mid → weight catalysts, near-term guidance, and multiple
compression risk; treat any DCF as a sanity check, not a driver. Long/forever → weight moat
durability, reinvestment runway, and terminal economics; DCF carries more weight. Say which mode you
are in.

**Standing intake reuse.** If a standing intake lens exists and is fresh (<14 days), do not re-ask: restate it in the two computed lines above and proceed. Re-ask only on material change (new/closed position, changed target size, horizon switch, new caps). A restated standing lens counts as intake complete.

---

## KILL GATE (runs immediately after intake)

Four checks, pulled live, before spending the full pipeline. Any hard fail = stop and report.

1. **Scope fit** — is it a bank, insurer, REIT, pre-revenue, or mid-restructuring? If yes, FCF-based
   valuation is the wrong tool. Say so and stop, or offer the correct method.
2. **ROIC vs WACC** — return on invested capital versus the cost of that capital. If ROIC has been
   below WACC for 3+ years with no visible inflection, growth destroys value and the rest of the
   pipeline is theatre. Hard fail unless there is a specific, evidenced turn.
3. **Share count trend** — fully diluted shares over 5 years. Persistently rising with no
   acquisition rationale means management pays itself with your ownership. Flag; hard fail if
   dilution exceeds revenue growth.
4. **Balance sheet survival** — net debt / EBITDA, and the debt maturity schedule. Any wall of
   maturities inside the horizon at rates well above the existing coupon is a hard fail unless
   refinancing is already secured.

Report the gate result in four lines. If it passes, continue without ceremony.

---

## PHASE 1 — Research

### 1a. Macro read
Invoke the `market-research` skill for the regime read. If unavailable, do it inline: rate path,
inflation trend, growth trend, credit conditions, and the specific country exposure that matters for
this company's revenue. Scan global headlines for anything that changes the sector's demand
function. **Output: sector is bullish / bearish / stagnant, with the two facts that decide it.**

### 1b. Sector work
Past trend and forward runway. The question is not "is this sector good" but **which stage** it is
in: compounding, maturing, fading, or breaking. Look for capex cycles, pricing power direction,
regulatory shifts, and substitution risk. State the stage and what would move it to the next one.

### 1c. Company work

Do all seven. Skipping any one of these is the most common way this pipeline produces a confident
wrong answer.

1. **Last 4 quarters — official sources only.** 10-Q/10-K, earnings releases, transcripts, IR deck.
   Track guidance versus delivery each quarter. A company that has cut guidance twice is telling you
   something the headline numbers are not.
2. **Read the risk factors and the footnotes.** Not the slides. Slides are marketing; footnotes are
   where revenue recognition changes, contingent liabilities, segment reclassifications, and
   customer concentration actually live.
3. **Core product/service and the moat.** Use `references/moat_framework.md` (bundled in this
   skill). Name the moat type, then name the thing that would erode it and how fast.
4. **Capital allocation record.** Five years of: share count direction, buyback price discipline
   (did they buy high?), dividend history, acquisition track record and write-downs, ROIC trend.
   This is the single best read on management honesty available from public data.
5. **Stock-based compensation (SBC).** SBC = paying staff in shares instead of cash. State it as a
   % of revenue and % of operating cash flow. It is a real cost. Carry the number into Phase 2 — the
   DCF skills must either deduct it from FCF or model the dilution, never ignore it.
6. **Concentration risk.** Top customer and top supplier as % of revenue/COGS. Above ~20% on either
   side, the "moat" may be a dependency. Also check geographic and single-product concentration.
7. **News + M&A, last 3 months.** Material headlines, acquisitions, divestitures, management
   departures, regulatory actions. Then **future plans, 5–10 years**: stated roadmap, capex
   commitments, TAM claims. Separate what management has *committed capital to* from what they have
   merely *talked about*.

### 1d. Competitive stress test
Line the company up against its 3–5 closest competitors on: growth, margin, ROIC, market share
direction, and pricing power. Then answer directly — is this dominance, a genuine monopoly niche, a
narrow edge, or a commodity fight it happens to be winning right now? Name its two clearest
downsides versus the best competitor.

### 1e. The real bear case
Search for and read: short reports, bearish sell-side notes, critical journalism, credible skeptics
in filings or forums. Reconstruct the strongest version of the argument **in their words, not
yours**. If you cannot find any bear case, that is itself a finding — say so, because it usually
means you did not look hard enough.

**Phase 1 deliverable** — a written block containing: sector stage, moat verdict, guidance track
record, SBC %, concentration risk, capital allocation grade, competitive position, and the steelmanned
bear case. This block is a required input to Phase 2. Do not proceed without it.

---

## PHASE 2 — Quantitative

### 2a. Quality gate (expanded from the kill gate)
Compute and tabulate, live:
- **ROIC vs WACC**, 5-year trend, not just latest.
- **FCF conversion** — free cash flow ÷ net income. Persistently below ~70% means reported profit
  is not turning into cash. Find out why.
- **Debt maturity ladder** — amount and rate by year (first path: `research/company-financials` → `references/sec-edgar-fetch.md`; only after that fails may the ladder be marked UNVERIFIED).
- **Margin trend** — gross and operating, 5 years.
- **Share count trend** — 5 years, fully diluted.

If any of these contradicts the Phase 1 narrative, the numbers win. Say so explicitly.

**Pairing pre-registration (mandatory before any DCF math).** Write down: (a) the pairing — FCFF with EV/WACC or FCFE with market-cap/cost-of-equity, never mixed; (b) the sign of net cash (positive = net cash, negative = net debt); (c) the no-growth sanity value `base FCF / (WACC − terminal growth)` next to EV. If the solved growth looks absurd, recheck (a)–(c) before believing the model — two runs were nearly derailed by a levered/unlevered mixup and a sign error.

### 2b. Reverse DCF — runs FIRST, and must be fed the earlier phases
Invoke the `reverse-dcf` skill. This is deliberately first: a forward DCF anchors you to a number
you will then defend, whereas reverse DCF starts from the market's price and asks what has to be
true.

**Pass these forward explicitly** — the reverse DCF must be run *in light of* prior phases, not in
isolation:
- From **Phase 0**: the horizon (sets the explicit-period length), and any correlated-exposure
  overlap in the user's portfolio (the plausibility step must flag it).
- From **Phase 1**: the sector stage, the moat verdict, the SBC number, the concentration risk, and
  the guidance track record. These are what make the implied growth rate plausible or absurd.
- From **Phase 2a**: the ROIC-vs-WACC spread and FCF conversion. A high implied growth rate is far
  less credible from a business earning below its cost of capital.

Then write the judgment sentence in plain English: **"The market is paying for X% FCF growth for N
years. Given [specific Phase 1 evidence], that is [conservative / demanding / fantasy]."** Always
state the growth-path convention (fade vs constant) and the WACC alongside the number.

### 2c. Forward DCF — second
Invoke the `dcf-valuation` skill. Default horizon 5 years, fade convention, terminal growth capped
at nominal GDP (~2.5–3%). Deduct or model SBC. Then do the comparison that matters:

**Your assumed growth vs the market's implied growth.** The gap, and which side of it the Phase 1
evidence supports, is the core of the valuation argument.

**Cyclicals run on a mid-cycle base by default.** For violently cyclical names (earnings ±50% across the cycle, FCF polluted by inventory swings), declare a normalized mid-cycle base FCF with a one-line defense and run the DCF on it — raw TTM is meaningless there, not conservative.

### 2d. Relative valuation — mandatory, especially for AI names and compounders
DCF alone is too easy to fudge, and it systematically mishandles high-quality compounders that trade
at a persistent premium and keep earning it. So run both comparisons:

- **Versus its own history** — current EV/FCF, EV/EBITDA, P/E, EV/Sales against its own 5- and
  10-year range. Is today's multiple in the 20th or 80th percentile of its own history?
- **Versus peers** — the same multiples against the 3–5 competitors from Phase 1d, adjusted for
  growth and margin quality. A higher multiple is not automatically expensive; a higher multiple
  *unjustified by better ROIC, growth, or durability* is.

Minimum bar when aggregators are bot-walled: snippet-built own-history ranges labeled UNVERIFIED beat no relative read; if even that fails, name Relative Valuation as the confidence limiter in 4f.

State plainly: is the premium earned, unearned, or shrinking? For AI-exposed names specifically,
ask whether the multiple is pricing the company's own earnings or the sector's narrative — and say
which.

**Gordon-vs-exit divergence rule.** A >25% gap gets a decision, not an investigation note: weight Gordon for mature cash-cow businesses and the exit-multiple lens (on a MATURE-peer multiple) for growers still scaling margins; if the gap persists after staging the weight, widen the fair-value band to span both instead of picking a winner.

### 2e. Assumption audit — no verdict without it
List every material input as one of three labels:
- `SOURCED` — pulled from a filing or live feed this session, with timestamp.
- `ESTIMATED` — reasoned from evidence, with the reasoning stated in one line.
- `GUESSED` — no real basis.

**Hard rule: if more than 3 core inputs are `GUESSED`, you may not issue a verdict.** Report the
analysis, name the missing data, and tell the user what to go find.

**Note on sensitivity grids:** the `reverse-dcf` and `dcf-valuation` skills compute sensitivity
internally and must continue to — dropping it would break their integrity checks. But do **not**
reproduce the grid in this skill's output. Instead collapse it into one sentence: *"Across a
reasonable range of discount rates, fair value lands between $A and $B."* The band is the useful
part; the table is not.

---

## PHASE 3 — Insider & Institutional Flow

Treat this as **corroborating evidence, not a primary signal.** It confirms or complicates a thesis
built in Phases 1–2. It never creates one.

Report **SEC EDGAR Form 4 (primary), one aggregator cross-check (StockTitan, MarketBeat, or Nasdaq insider pages), and QuiverQuant in separate, clearly labelled sections.** Do not merge them —
they parse the same filings differently and the disagreement is informative.

**Source reliability, know before you start:** OpenInsider is RETIRED from this pipeline (down in ~9 of 13 runs, Aug–Sep 2026) — do not attempt it. Work this chain in order, time-boxed to 10 minutes total: (1) SEC EDGAR full-text / Form 4 search for the CIK (buys = transaction code `P`; verify 10b5-1 footnotes on sells); (2) one aggregator cross-check via web search (StockTitan insider pages, MarketBeat insider trades, or Nasdaq insider/institutional pages); (3) QuiverQuant free tier for the congressional overlay. Insider research is COMPULSORY — a thin return is reported as thin-with-source-named, never as "no activity," and a fully failed Phase 3 caps confidence at Medium and is named in 4f. QuiverQuant's corporate insider data is now largely behind a paid tier — the free tier
is mainly congressional trading. Expect thin returns and say so rather than reporting silence as
"no insider activity."

### 3a. Insider BUYING — the main event
Filter to **open-market purchases only** (Form 4 transaction code `P`). Exclude option exercises
(`M`), grants (`A`), and gifts (`G`) — those are compensation, not conviction.

Then rank by what actually carries signal:
1. **Cluster buys** — 3+ distinct insiders buying inside a 90-day window. This outranks any single
   large purchase.
2. **Size relative to that person's compensation** — a CFO putting a year's salary in is a stronger
   signal than a billionaire founder adding $2m. Compute the ratio where comp data is available.
3. **Seniority** — CEO/CFO/Chairman above divisional officers above directors.
4. **Timing** — purchases into weakness, or shortly after a guidance cut, carry more information
   than purchases into strength.

Highlight large-value buys explicitly, with names, roles, dates, and dollar amounts.

### 3b. Insider SELLING — aggressively filtered
Most insider selling is noise: scheduled 10b5-1 plans, tax cover on vesting, diversification. Report
**only** sales meeting **all four** conditions:
- Aggregate value **> USD 15 million**, and
- Concentrated in a **small group** (roughly ≤5 insiders), and
- Executed inside a **short, compressed window**, and
- **Not** a pre-scheduled 10b5-1 plan.

Everything else: ignore entirely. Do not list it, do not caveat it. State one line: *"No qualifying
insider selling under the filter."*

### 3c. Institutional (13F)
Quarter-over-quarter changes in institutional ownership: notable new positions, meaningful adds,
full exits. Name the funds where they are recognisable. Note that 13F data lags by up to 45 days —
say the as-of date every time. Default path is aggregators-via-search (MarketBeat, WhaleWisdom,
Nasdaq); it shares the 10-minute Phase 3 time-box — then move on loudly.

---

## PHASE 4 — Synthesis

### 4a. Collate
Pull Phases 0–3 into one view. Where they disagree, say so out loud and adjudicate. Contradiction
between a strong narrative and weak numbers is the most decision-relevant thing in the entire memo —
do not smooth it over.

### 4b. Cross-reference
Check your conclusion against **Morningstar** (fair value estimate, moat rating, uncertainty rating)
— but treat it as one shop's opinion, often paywalled. Also check **analyst consensus** (estimate
range, not just the mean) and **at least one named bear** from Phase 1e. Where you disagree with any
of them, state why in one sentence. Never defer to them. For dual-listed names, frame in the HOME
currency/listing and state the ADR ratio plus dividend-withholding drag explicitly — never value off
the ADR line alone.

### 4c. Verdict — exactly one of four
**Strong Buy / Buy / Hold / Sell.** No other words. No "accumulate," no "wait," no hedging.

Rough calibration:
- **Strong Buy** — high-conviction quality, meaningful discount to your fair value band, corroborating
  flow, no `GUESSED` inputs on core drivers.
- **Buy** — thesis intact and price acceptable, but with one unresolved risk or a thinner margin.
- **Hold** — good business, price offers no margin of safety; or thesis intact but a material
  question is open.
- **Sell** — thesis broken, valuation indefensible, or a kill criterion has already triggered.

### 4d. If Strong Buy / Buy / Hold — deliver the full package

**1. Thesis** — 4–6 sentences. Why this business, why now, why the market is wrong, and what you are
being paid to bear. If you cannot write it without jargon, you do not understand it yet.

**2. Entry band with tiered margin of safety.** Margin of safety = discount to your fair value
estimate. Do not use a blanket 20–50%. Tier it to the business:

| Business type | Margin of safety |
|---|---|
| Wide moat, predictable cash flows, long track record | 15–25% |
| Solid but with one real open question | 25–35% |
| Cyclical, early-stage, or high assumption-uncertainty | 35–50% |

State which tier you chose and why. Give the entry band in dollars, plus the fair value band it
derives from.

**3. Position sizing — required.** A verdict without a size is useless. State the target % of
portfolio, the starting tranche, and how it respects every cap the user gave in Phase 0. If the
verdict is Strong Buy but the position cap only permits a small size, say that plainly.

**4. Add triggers** — specific, checkable conditions that justify buying more. Prefer
business-progress triggers over price triggers.

**5. Trim triggers** — conditions to reduce: position exceeds cap, valuation runs far beyond the
fair value band, or thesis partially weakens.

**6. Exit triggers** — price/valuation-based conditions to leave entirely.

**7. Kill criteria — the most important item, and distinct from exit triggers.** Exit triggers are
about price. Kill criteria are about **being wrong on the facts**, and must be written *before* the
position is opened. Format: *"If [specific measurable fact] happens for [duration], my thesis is
wrong and I exit regardless of price."* Give 3–4. Tie each one to a specific Phase 1 or 2a claim.
Example shape: *"If gross margin falls below X% for two consecutive quarters, the pricing-power
claim is false."*

### 4e. If Sell — reconsideration trigger
Give the specific, checkable conditions that would put the name back on the watchlist. Same
discipline: measurable facts, not vibes. Include a re-check date.

### 4f. Mandatory closing block (every verdict, no exceptions)
- **Confidence: High / Medium / Low**, with the one factor that most limits it.
- **What I could not verify** — list the `UNVERIFIED` and `GUESSED` items from 2e by name. Honest
  gaps beat false precision.
- **Analysis date** and **review date** — default to the next scheduled earnings release. Name the
  actual date.

### 4g. Calibration — the HOLD-machine check
Every run ends HOLD and the discipline means nothing. Track verdicts across runs: if more than 80% of the last 10+ verdicts are HOLD, the next run must explicitly re-examine whether the WACC anchor (10Y + beta × ERP) or the margin-of-safety tiers are systematically too strict for the user's 5–10y horizon — and say so in the memo — rather than concluding the market is always right. A 5-year fade DCF structurally punishes growers; long-horizon conviction names deserve the exit-multiple lens at full weight before a HOLD is issued.

---

## Memo

Produce a PDF using `scripts/generate_memo_pdf.py` (bundled in this skill) so output matches the
rest of the desk. Run `--print-schema` first to get the current JSON shape, then populate it. Save
to `~/Desktop/Cowork/Memos/Pro_[TICKER]_Memo.pdf`, deliver the PDF inline in chat via
`MEDIA:<path>` (or open it in the preview pane with `open_preview`), and give a 3-line summary in
chat: verdict, entry band, size.

**Interpreter (verified Aug 2026):** run the generator with the Hermes venv Python explicitly —
`~/.hermes/hermes-agent/venv/bin/python3 scripts/generate_memo_pdf.py ...`. The bare `python3` on
this machine resolves to the system 3.9 interpreter, which cannot load Pillow/reportlab's native
extensions and fails at import.

Open the memo with a boxed **Thesis Risk** section (standing convention): main analytical flaws,
key risks including overlap with existing concentrated exposure, and the single assumption that would
flip the verdict if it moved.

---

## Failure modes to actively guard against

- Running the forward DCF before the reverse DCF, or running either without feeding it Phase 0/1/2a
  context — this is the whole reason the pipeline is ordered this way.
- Treating insider or 13F flow as a thesis rather than corroboration.
- Reporting unfiltered insider selling. It is noise and it will make you bearish for no reason.
- Opening OpenInsider. It is retired from this pipeline; every attempt burns the Phase 3 time-box for nothing.
- Merging the EDGAR, aggregator, and QuiverQuant sections.
- Letting >80% HOLD verdicts accumulate without a calibration review (see 4g).
- Issuing a verdict with more than 3 `GUESSED` core inputs.
- Writing exit triggers and calling them kill criteria. They are different instruments.
- Letting a "Strong Buy" verdict quietly breach a Phase 0 position cap.
- Building the bear case yourself instead of sourcing it from real bears.
- Presenting a fair value point estimate. The band and the reasoning are the product.
- Skipping relative valuation because the DCF "already answered it." For premium-multiple
  compounders, relative valuation is often the more honest tool.

---

## Reference Files

- `references/moat_framework.md` — moat types, durability scoring, and niche-dominance tie-in.
- `scripts/generate_memo_pdf.py` — PDF memo generator (run `--print-schema` for the JSON shape).
