#!/usr/bin/env python3
"""
Stock Screening Memo PDF Generator
Produces a concise buy-side screening memo: verdict, intake, valuation snapshot,
bull/bear, niche dominance + chain effects, independent fair value, and risks.

Style intentionally matches the dcf-valuation skill (navy/grey IB palette) so memos
from both skills look like they came from the same desk.

Usage:
    python generate_memo_pdf.py --output out.pdf --data memo_data.json
    python generate_memo_pdf.py --print-schema     # dumps the expected JSON schema
"""

import json
import argparse
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, ListFlowable, ListItem
)

# ── IB palette (shared with dcf-valuation) ────────────────────────────────
NAVY = colors.HexColor("#1B2A4A")
DARK_GREY = colors.HexColor("#2C3E50")
MED_GREY = colors.HexColor("#7F8C8D")
LIGHT_GREY = colors.HexColor("#ECF0F1")
GREEN = colors.HexColor("#27AE60")
RED = colors.HexColor("#C0392B")
AMBER = colors.HexColor("#F39C12")
WHITE = colors.white

# Verdict → color mapping (covers both holding and non-holding vocabularies)
VERDICT_COLOR = {
    # holding
    "buy more": GREEN, "hold": AMBER, "sell": RED,
    # not holding
    "buy": GREEN, "bet heavily on it": GREEN,
    "wait for a better price": AMBER, "pass": RED, "hard pass": RED,
}

VALUATION_COLOR = {
    "undervalued": GREEN, "fairly valued": AMBER, "overvalued": RED,
}


def build_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name='Title2', fontName='Helvetica-Bold', fontSize=20,
                         leading=24, textColor=NAVY, spaceAfter=2))
    s.add(ParagraphStyle(name='Sub', fontName='Helvetica', fontSize=10,
                         leading=13, textColor=MED_GREY, spaceAfter=10))
    s.add(ParagraphStyle(name='H', fontName='Helvetica-Bold', fontSize=12,
                         leading=16, textColor=NAVY, spaceBefore=14, spaceAfter=6))
    s.add(ParagraphStyle(name='Body', fontName='Helvetica', fontSize=9,
                         leading=13, textColor=DARK_GREY, spaceAfter=5, alignment=TA_LEFT))
    s.add(ParagraphStyle(name='BodyTight', fontName='Helvetica', fontSize=9,
                         leading=12.5, textColor=DARK_GREY, spaceAfter=2))
    s.add(ParagraphStyle(name='Cell', fontName='Helvetica', fontSize=8.5,
                         leading=11, textColor=DARK_GREY))
    s.add(ParagraphStyle(name='CellBold', fontName='Helvetica-Bold', fontSize=8.5,
                         leading=11, textColor=NAVY))
    s.add(ParagraphStyle(name='CellWhite', fontName='Helvetica-Bold', fontSize=8.5,
                         leading=11, textColor=WHITE))
    s.add(ParagraphStyle(name='VerdictBig', fontName='Helvetica-Bold', fontSize=16,
                         leading=20, textColor=WHITE, alignment=TA_CENTER))
    s.add(ParagraphStyle(name='Disc', fontName='Helvetica-Oblique', fontSize=7.5,
                         leading=10, textColor=MED_GREY, spaceAfter=2))
    return s


def hr(color=LIGHT_GREY, w=1, sb=4, sa=4):
    return HRFlowable(width="100%", thickness=w, color=color,
                      spaceBefore=sb, spaceAfter=sa)


def verdict_banner(data, st):
    verdict = (data.get("verdict") or "—").strip()
    color = VERDICT_COLOR.get(verdict.lower(), MED_GREY)
    one_liner = data.get("verdict_one_liner", "")
    cells = [[Paragraph(verdict.upper(), st['VerdictBig'])]]
    if one_liner:
        cells.append([Paragraph(one_liner, ParagraphStyle(
            'ol', parent=st['CellWhite'], alignment=TA_CENTER, fontSize=9, leading=12))])
    t = Table(cells, colWidths=[6.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return t


def kv_table(rows, st, col0=2.0, col1=4.5, header=None):
    data_rows = []
    if header:
        data_rows.append([Paragraph(header[0], st['CellWhite']),
                          Paragraph(header[1], st['CellWhite'])])
    for k, v in rows:
        data_rows.append([Paragraph(str(k), st['CellBold']),
                          Paragraph(str(v), st['Cell'])])
    t = Table(data_rows, colWidths=[col0 * inch, col1 * inch])
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY) if header else ('BACKGROUND', (0, 0), (0, -1), LIGHT_GREY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DBDB")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]
    if header:
        style.append(('BACKGROUND', (0, 1), (0, -1), LIGHT_GREY))
    t.setStyle(TableStyle(style))
    return t


def bullets(items, st, style='Body'):
    if not items:
        return Paragraph("—", st['Body'])
    return ListFlowable(
        [ListItem(Paragraph(str(i), st[style]), leftIndent=10) for i in items],
        bulletType='bullet', start='•', leftIndent=12, bulletColor=NAVY,
    )


def bull_bear_table(bull, bear, st):
    head = [Paragraph("BULL CASE", st['CellWhite']), Paragraph("BEAR CASE", st['CellWhite'])]
    body_bull = bullets(bull, st, 'BodyTight')
    body_bear = bullets(bear, st, 'BodyTight')
    t = Table([head, [body_bull, body_bear]], colWidths=[3.25 * inch, 3.25 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), GREEN),
        ('BACKGROUND', (1, 0), (1, 0), RED),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DBDB")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def scenario_table(scenarios, st):
    """scenarios: list of {name, probability, value, note}"""
    if not scenarios:
        return None
    head = [Paragraph(h, st['CellWhite']) for h in ["Scenario", "Prob.", "Implied Value", "Note"]]
    rows = [head]
    for sc in scenarios:
        rows.append([
            Paragraph(str(sc.get("name", "")), st['CellBold']),
            Paragraph(str(sc.get("probability", "")), st['Cell']),
            Paragraph(str(sc.get("value", "")), st['Cell']),
            Paragraph(str(sc.get("note", "")), st['Cell']),
        ])
    t = Table(rows, colWidths=[1.2 * inch, 0.8 * inch, 1.5 * inch, 3.0 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DBDB")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
    ]))
    return t


def build(data, output):
    st = build_styles()
    doc = SimpleDocTemplate(output, pagesize=letter,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch)
    E = []

    # Header
    ticker = data.get("ticker", "—")
    name = data.get("company_name", "")
    E.append(Paragraph(f"{name} ({ticker})" if name else ticker, st['Title2']))
    date = data.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
    lens = data.get("lens", "—")
    horizon = data.get("time_horizon", "—")
    E.append(Paragraph(f"Screening Memo · {date} · Lens: {lens} · Horizon: {horizon}", st['Sub']))

    # Verdict banner
    E.append(verdict_banner(data, st))
    E.append(Spacer(1, 10))

    # Snapshot: price vs intrinsic value
    E.append(Paragraph("Valuation Snapshot", st['H']))
    snap = [
        ("Current price", data.get("current_price", "—")),
        ("Independent fair value", data.get("fair_value", "—")),
        ("Fair value range", data.get("fair_value_range", "—")),
        ("Margin of safety", data.get("margin_of_safety", "—")),
        ("Valuation call", data.get("valuation_call", "—")),
        ("Method(s) used", data.get("valuation_method", "—")),
        ("Consensus target (challenged)", data.get("consensus_target", "—")),
    ]
    E.append(kv_table(snap, st))

    # Intake assumptions
    E.append(Paragraph("Intake & Assumptions", st['H']))
    intake = [
        ("Lens", data.get("lens", "—")),
        ("Time horizon", data.get("time_horizon", "—")),
        ("Position size", data.get("position_size", "—")),
        ("Currently holding", data.get("holding", "—")),
        ("Cost basis", data.get("cost_basis", "—")),
    ]
    E.append(kv_table(intake, st))
    if data.get("assumption_flags"):
        E.append(Spacer(1, 4))
        E.append(Paragraph("Flagged assumptions (user did not confirm):", st['BodyTight']))
        E.append(bullets(data["assumption_flags"], st, 'BodyTight'))

    # Financial snapshot
    if data.get("financial_highlights"):
        E.append(Paragraph("Financial Snapshot", st['H']))
        E.append(kv_table([(k, v) for k, v in data["financial_highlights"]], st))

    # Bull vs Bear
    E.append(Paragraph("Bull vs Bear", st['H']))
    E.append(bull_bear_table(data.get("bull_case", []), data.get("bear_case", []), st))

    # Independent fair value + scenarios
    E.append(Paragraph("Independent Fair Value", st['H']))
    if data.get("fair_value_narrative"):
        E.append(Paragraph(data["fair_value_narrative"], st['Body']))
    sc = scenario_table(data.get("scenarios", []), st)
    if sc:
        E.append(Spacer(1, 4))
        E.append(sc)
    if data.get("probability_weighted_value"):
        E.append(Spacer(1, 4))
        E.append(Paragraph(f"<b>Probability-weighted value:</b> {data['probability_weighted_value']}", st['Body']))

    # Catalyst & convexity (growth lens only)
    if data.get("catalyst_panel"):
        cp = data["catalyst_panel"]
        E.append(Paragraph("Catalyst, Convexity & Reflexivity (Growth Lens)", st['H']))
        E.append(kv_table([
            ("Hard catalyst", cp.get("catalyst", "—")),
            ("Narrative alignment", cp.get("narrative", "—")),
            ("Convexity profile", cp.get("convexity", "—")),
        ], st))
        if cp.get("reflexivity"):
            E.append(Spacer(1, 4))
            refl = Table([[Paragraph("SPECULATIVE REFLEXIVITY (not value)", st['CellWhite'])],
                          [Paragraph(cp["reflexivity"], st['Cell'])]], colWidths=[6.5 * inch])
            refl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), AMBER),
                ('BACKGROUND', (0, 1), (-1, 1), LIGHT_GREY),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DBDB")),
                ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            E.append(refl)
        if cp.get("survivorship_note"):
            E.append(Paragraph("• " + cp["survivorship_note"], st['Disc']))

    # Niche dominance & chain effects
    E.append(Paragraph("Niche Dominance & Chain Effects", st['H']))
    nd = [
        ("Dominates its niche?", data.get("dominance_verdict", "—")),
        ("Market share / trend", data.get("market_share", "—")),
        ("Moat type(s)", data.get("moat_type", "—")),
        ("Moat direction", data.get("moat_direction", "—")),
    ]
    E.append(kv_table(nd, st))
    if data.get("chain_effects"):
        E.append(Spacer(1, 4))
        E.append(Paragraph("Chain effects (who catches a cold if it sneezes — and vice versa):", st['BodyTight']))
        E.append(bullets(data["chain_effects"], st, 'BodyTight'))

    # Verdict rationale
    E.append(Paragraph("Verdict Rationale", st['H']))
    if data.get("verdict_rationale"):
        E.append(Paragraph(data["verdict_rationale"], st['Body']))
    if data.get("what_would_change_my_mind"):
        E.append(Paragraph(f"<b>What would flip this verdict:</b> {data['what_would_change_my_mind']}", st['Body']))

    # Risks / model breakers
    E.append(Paragraph("Key Risks / Thesis Breakers", st['H']))
    E.append(bullets(data.get("risks", []), st, 'BodyTight'))

    # Caveats
    E.append(Spacer(1, 10))
    E.append(hr(MED_GREY, 0.5))
    caveats = data.get("caveats", [
        "Screening framework, not investment advice. Verdict is only as good as its stated, contestable assumptions.",
        "Public data only — no management access or proprietary datasets.",
        "Lens and horizon were user-chosen; a different lens can yield a different verdict from the same facts.",
        "Intrinsic value is sensitive to discount rate and terminal assumptions; the scenario range reflects this.",
    ])
    for c in caveats:
        E.append(Paragraph("• " + c, st['Disc']))

    doc.build(E)


SCHEMA = {
    "ticker": "NVDA",
    "company_name": "NVIDIA Corporation",
    "analysis_date": "2026-05-20",
    "lens": "Value | Growth/venture-style",
    "time_horizon": "3-5yr",
    "position_size": "e.g. 8% of portfolio / 200 shares",
    "holding": "Yes | No",
    "cost_basis": "e.g. $95 avg (omit if not holding)",
    "assumption_flags": ["Only if user declined to answer an intake question"],

    "current_price": "$X (cite source + date in chat)",
    "fair_value": "$Y (your independent base-case point estimate)",
    "fair_value_range": "$low - $high",
    "margin_of_safety": "+/- Z% vs current price",
    "valuation_call": "Undervalued | Fairly valued | Overvalued",
    "valuation_method": "e.g. DCF (via dcf-valuation) cross-checked with EV/EBITDA",
    "consensus_target": "$consensus (state your agreement/disagreement)",

    "financial_highlights": [["Revenue (FY/TTM)", "$X, +Y% YoY"], ["Operating margin", "X%"],
                             ["FCF / FCF yield", "$X / Y%"], ["Net debt (cash)", "$X"],
                             ["ROIC / ROE", "X%"], ["Fwd P/E · EV/EBITDA", "X · Y"]],

    "bull_case": ["Strongest bull point 1", "..."],
    "bear_case": ["Strongest bear point 1 (specific, falsifiable)", "..."],

    "fair_value_narrative": "Short paragraph: how you derived YOUR value and where you diverge from consensus/market.",
    "scenarios": [
        {"name": "Bull", "probability": "25%", "value": "$H", "note": "what has to be true"},
        {"name": "Base", "probability": "55%", "value": "$M", "note": "..."},
        {"name": "Bear", "probability": "20%", "value": "$L", "note": "..."}
    ],
    "probability_weighted_value": "$W",

    "catalyst_panel": {
        "_comment": "GROWTH LENS ONLY — omit entirely for value lens",
        "catalyst": "Strong/Soft/None — name the discrete dated event",
        "narrative": "Hot/Neutral/Cold — the macro theme it plugs into",
        "convexity": "High/Moderate/Low — name the small-base or distress-reprice mechanism; rough upside x + probability",
        "reflexivity": "Low/Elevated/Combustible — SI%/float, options, turnover. Speculation not value. Caution flag, not buy signal.",
        "survivorship_note": "Built only from winners that went vertical; matching signals != likely to 10x."
    },

    "dominance_verdict": "Yes/No/Partial — with the reason",
    "market_share": "e.g. ~80% of discrete GPU; share rising",
    "moat_type": "e.g. switching costs (CUDA) + learning curve",
    "moat_direction": "Widening | Stable | Eroding",
    "chain_effects": ["If it cuts capacity, foundry X and customer Y feel it...",
                      "Upstream shock Z propagates in via..."],

    "verdict": "Buy more|Hold|Sell  (holding)  OR  Hard Pass|Pass|Wait for a better price|Buy|Bet heavily on it (not holding)",
    "verdict_one_liner": "One line shown under the verdict banner.",
    "verdict_rationale": "Ties verdict to intrinsic value vs price, horizon, position size, and cost basis.",
    "what_would_change_my_mind": "The single fact/event that would flip the verdict.",

    "risks": ["Specific thesis-breaker 1", "..."],
    "caveats": ["Optional — defaults are sensible if omitted"]
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output")
    ap.add_argument("--data")
    ap.add_argument("--print-schema", action="store_true")
    args = ap.parse_args()

    if args.print_schema:
        print(json.dumps(SCHEMA, indent=2))
        return

    with open(args.data) as f:
        data = json.load(f)
    build(data, args.output)
    print(f"Memo written to {args.output}")


if __name__ == "__main__":
    main()
