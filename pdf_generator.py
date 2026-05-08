from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_formula_pdf(data: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = ParagraphStyle(
        "FormulaBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        spaceAfter=6,
    )

    story = [Paragraph("FormulaForge AI", title_style), Spacer(1, 10)]
    story.append(Paragraph(f"Subject: {data.get('subject', 'Unknown Subject')}", styles["Heading3"]))
    story.append(Spacer(1, 12))

    for topic in data.get("topics", []):
        story.append(Paragraph(topic.get("topic_name", "Untitled Topic"), heading_style))
        story.append(Spacer(1, 8))
        for formula in topic.get("formulas", []):
            rows = [
                ["Formula", formula.get("formula", "")],
                ["Meaning", formula.get("meaning", "")],
                [
                    "Variables",
                    "<br/>".join(
                        f"{item.get('symbol', '')} -> {item.get('meaning', '')}"
                        for item in formula.get("variables", [])
                    )
                    or "-",
                ],
                ["Use", formula.get("use", "")],
            ]
            table = Table(rows, colWidths=[80, 420])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E5E7EB")),
                        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("LEADING", (0, 0), (-1, -1), 13),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 12))

    important = data.get("important_formulas", [])
    if important:
        story.append(Paragraph("Most Frequently Used Formulae", heading_style))
        story.append(Spacer(1, 8))
        for item in important:
            story.append(Paragraph(f"<b>{item.get('formula', '')}</b>", body_style))
            story.append(Paragraph(f"Meaning: {item.get('meaning', '')}", body_style))
            story.append(Paragraph(f"Use: {item.get('use', '')}", body_style))
            story.append(Spacer(1, 8))

    document.build(story)
    return buffer.getvalue()


def build_formula_txt(data: dict[str, Any]) -> str:
    lines = [f"FormulaForge AI\nSubject: {data.get('subject', 'Unknown Subject')}\n"]
    for topic in data.get("topics", []):
        lines.append(f"\n## {topic.get('topic_name', 'Untitled Topic')}")
        for formula in topic.get("formulas", []):
            lines.append(f"Formula: {formula.get('formula', '')}")
            lines.append(f"Meaning: {formula.get('meaning', '')}")
            variables = formula.get("variables", [])
            if variables:
                lines.append("Variables:")
                for item in variables:
                    lines.append(f"- {item.get('symbol', '')} -> {item.get('meaning', '')}")
            lines.append(f"Use: {formula.get('use', '')}")
            lines.append("")

    important = data.get("important_formulas", [])
    if important:
        lines.append("## Most Frequently Used Formulae")
        for item in important:
            lines.append(f"- {item.get('formula', '')}: {item.get('meaning', '')} | Use: {item.get('use', '')}")

    return "\n".join(lines).strip() + "\n"
