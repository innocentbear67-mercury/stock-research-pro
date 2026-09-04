# Stock Research Pro

A position-aware equity research pipeline skill for [Hermes Agent](https://hermes-agent.nousresearch.com/docs) (by Nous Research).

Triggers on `/stock-research-pro` or "pro research". Ends in a single, un-hedged verdict — Strong Buy / Buy / Hold / Sell — with sizing, a tiered entry band, add/trim/exit triggers, and pre-committed kill criteria.

## What it does

```
PHASE 0  INTAKE          → 6 questions, one batch. BLOCKING.
KILL GATE                → 4 hard filters. Fail = stop, report why, do not proceed.
PHASE 1  RESEARCH        → Macro → Sector → Company (7 checks) → Competitive stress → Steelmanned bear case
PHASE 2  QUANT           → Quality gate → reverse-DCF first → forward DCF → relative val → assumption audit
PHASE 3  FLOW            → Insider buys, aggressively filtered sells, 13F. Corroboration, not thesis.
PHASE 4  SYNTHESIS       → Verdict, thesis, entry band, triggers, kill criteria, sizing, calibration check
MEMO                     → PDF via the bundled generator
```

Design principles baked into the pipeline:

- **Live data only.** Every figure pulled this session and timestamped.
- **Falsification first.** The bear case must come from actual bears — never invented and defeated.
- **Loud about gaps.** Unverifiable figures are labeled `UNVERIFIED`. More than 3 guessed core inputs = no verdict allowed.
- **Reverse DCF before forward DCF.** Ask what the market is paying for before anchoring on your own number.
- **Insider flow is corroboration, not thesis.** Selling is filtered aggressively — most of it is noise.
- **Kill criteria ≠ exit triggers.** One is about being wrong on the facts; the other is about price.

## Install

Copy into your Hermes skills directory:

```bash
git clone https://github.com/innocentbear67-mercury/stock-research-pro.git
mkdir -p ~/.hermes/skills/stock-research-pro
cp -r stock-research-pro/{SKILL.md,references,scripts} ~/.hermes/skills/stock-research-pro/
```

Requires: a Hermes Agent install, plus `reportlab` for the PDF memo generator (any Python ≥3.9 with reportlab works).

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The orchestrator — full pipeline spec |
| `references/moat_framework.md` | Moat typing, durability scoring, common errors |
| `scripts/generate_memo_pdf.py` | PDF memo generator (run `--print-schema` for the JSON shape) |

## Disclaimer

Analytical framework only — not investment advice. Verdicts are only as good as their stated, contestable assumptions.

## License

MIT
