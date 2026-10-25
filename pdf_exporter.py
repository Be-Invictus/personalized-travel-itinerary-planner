"""
Offline PDF Travel Guide Generator using ReportLab.
Generates an elegant, printable travel itinerary with day-by-day clusters, budget tables,
and emergency contact checklists.
"""

import io
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

from models import Itinerary


class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' and footer branding to each page."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header rule & title
        self.drawString(54, letter[1] - 36, "Personalized Travel Itinerary Planner • Offline Guide")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 40, letter[0] - 54, letter[1] - 40)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_text)
        self.drawString(54, 32, "Generated with AI Route Optimizer • Keep this copy offline during transit")
        self.line(54, 44, letter[0] - 54, 44)
        self.restoreState()


def generate_itinerary_pdf(itinerary: Itinerary) -> bytes:
    """Generates a complete, publication-grade PDF itinerary and returns binary bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Deep slate
    c_accent = colors.HexColor("#2A9D8F")     # Sage teal
    c_warm = colors.HexColor("#E07A5F")       # Terracotta
    c_light_bg = colors.HexColor("#F8FAFC")   # Sand light
    c_border = colors.HexColor("#CBD5E1")     # Light border

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=c_accent,
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    bold_style = ParagraphStyle(
        'BoldCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    meta_tag_style = ParagraphStyle(
        'MetaTagCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0284C7")
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph(f"✈ {itinerary.trip_title}", title_style))
    story.append(Paragraph(
        f"<b>Destination:</b> {itinerary.destination}, {itinerary.country} &nbsp;|&nbsp; "
        f"<b>Dates:</b> {itinerary.start_date} to {itinerary.end_date} ({itinerary.duration_days} Days) &nbsp;|&nbsp; "
        f"<b>Party:</b> {itinerary.travel_party} &nbsp;|&nbsp; "
        f"<b>Pace:</b> {itinerary.pace}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=2, spaceAfter=12))

    # 2. Executive Summary & Budget Snapshot Table
    summary_data = [
        [
            Paragraph("<b>Target Budget Tier:</b>", body_style),
            Paragraph(f"{itinerary.budget_level}", body_style),
            Paragraph("<b>Local Currency:</b>", body_style),
            Paragraph(f"{itinerary.local_currency_code} ({itinerary.local_currency_symbol})", body_style),
        ],
        [
            Paragraph("<b>Total Est. Cost (USD):</b>", body_style),
            Paragraph(f"<b>${itinerary.total_cost_usd:,.2f}</b>", bold_style),
            Paragraph("<b>Total Est. Cost (INR):</b>", body_style),
            Paragraph(f"<b>₹{itinerary.total_cost_inr:,.2f}</b>", bold_style),
        ],
        [
            Paragraph("<b>Total in Local Currency:</b>", body_style),
            Paragraph(f"<b>{itinerary.local_currency_symbol}{itinerary.total_cost_local:,.2f}</b>", bold_style),
            Paragraph("<b>Exchange Rate (USD):</b>", body_style),
            Paragraph(f"1 USD = {itinerary.usd_exchange_rate} {itinerary.local_currency_code}", body_style),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # 3. Day-by-Day Clustered Schedule
    story.append(Paragraph("📅 Day-by-Day Geographic Clustered Itinerary", h2_style))

    for day in itinerary.days:
        day_flowables = []
        day_header_text = f"<b>DAY {day.day_number} &bull; {day.date_str} &bull; {day.theme}</b>"
        cluster_text = f"<b>Cluster Zone:</b> {day.neighborhood_cluster} | <i>{day.transit_summary}</i>"
        
        day_header_data = [[
            Paragraph(day_header_text, ParagraphStyle('DH', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#FFFFFF"))),
            Paragraph(f"Day Total: ${day.daily_cost_usd:,.0f} / ₹{day.daily_cost_inr:,.0f}", ParagraphStyle('DH2', parent=body_style, alignment=2, fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#FFFFFF")))
        ]]
        d_table = Table(day_header_data, colWidths=[5.4*inch, 1.8*inch])
        d_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_primary),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        day_flowables.append(d_table)

        # Cluster Sub-bar
        cluster_data = [[Paragraph(cluster_text, ParagraphStyle('CL', parent=body_style, fontSize=8, textColor=c_accent))]]
        c_sub_table = Table(cluster_data, colWidths=[7.2*inch])
        c_sub_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BBF7D0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        day_flowables.append(c_sub_table)

        # Slots Table
        slot_rows = [
            [
                Paragraph("<b>Time & Slot</b>", bold_style),
                Paragraph("<b>Activity & Neighborhood Cluster</b>", bold_style),
                Paragraph("<b>Transit Tip & Details</b>", bold_style),
                Paragraph("<b>Est. Cost</b>", bold_style)
            ]
        ]

        for slot in day.slots:
            slot_info = (
                f"<b>{slot.time_slot}</b><br/>"
                f"<font size=7 color='#64748B'>{slot.time_range}</font>"
            )
            act_info = (
                f"<b>{slot.title}</b><br/>"
                f"<font size=8 color='#0F172A'>{slot.description}</font><br/>"
                f"<font size=7 color='#0284C7'>Cluster: {slot.neighborhood} &bull; {', '.join(slot.tags[:2])}</font>"
            )
            transit_info = (
                f"<font size=7.5 color='#334155'><b>Route:</b> {slot.transit_tip}</font>"
            )
            cost_info = (
                f"<b>{itinerary.local_currency_symbol}{slot.cost_local:,.0f}</b><br/>"
                f"<font size=7 color='#64748B'>${slot.cost_usd:,.0f} / ₹{slot.cost_inr:,.0f}</font>"
            )

            slot_rows.append([
                Paragraph(slot_info, body_style),
                Paragraph(act_info, body_style),
                Paragraph(transit_info, body_style),
                Paragraph(cost_info, body_style)
            ])

        slots_table = Table(slot_rows, colWidths=[1.1*inch, 3.4*inch, 1.8*inch, 0.9*inch])
        slots_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#F1F5F9")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        day_flowables.append(slots_table)
        day_flowables.append(Spacer(1, 10))

        story.append(KeepTogether(day_flowables))

    # 4. Emergency Contact Checklist & Offline Safety
    story.append(Spacer(1, 10))
    story.append(Paragraph("🛡 Emergency Contact & Offline Health Checklist", h2_style))

    em = itinerary.emergency_info
    em_data = [
        [
            Paragraph("<b>Police Emergency:</b>", bold_style),
            Paragraph(em.police_number if em else "112", body_style),
            Paragraph("<b>Ambulance / Medical:</b>", bold_style),
            Paragraph(em.ambulance_number if em else "112", body_style),
        ],
        [
            Paragraph("<b>Recommended Hospital:</b>", bold_style),
            Paragraph(em.local_hospital if em else "City Central International Hospital", body_style),
            Paragraph("<b>Tourist Helpline:</b>", bold_style),
            Paragraph(em.tourist_helpline if em else "Available at Airport Information Desk", body_style),
        ],
        [
            Paragraph("<b>Consular / Embassy:</b>", bold_style),
            Paragraph(em.embassy_note if em else "Keep copy of passport and contact home consulate.", body_style),
            Paragraph("<b>Travel Insurance:</b>", bold_style),
            Paragraph("Carry policy card with 24/7 overseas emergency phone number.", body_style),
        ]
    ]
    em_table = Table(em_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    em_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF7ED")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FDBA74")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FED7AA")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(em_table)
    story.append(Spacer(1, 12))

    # 5. Packing & Cultural Etiquette
    story.append(Paragraph("🧳 Packing Essentials & Local Etiquette", h2_style))
    pack_tips = "<br/>".join([f"&bull; {item}" for item in itinerary.packing_checklist])
    cult_tips = "<br/>".join([f"&bull; {item}" for item in itinerary.cultural_tips])

    guide_data = [
        [
            Paragraph("<b>Recommended Packing List</b>", bold_style),
            Paragraph("<b>Local Cultural Customs & Etiquette</b>", bold_style)
        ],
        [
            Paragraph(pack_tips, body_style),
            Paragraph(cult_tips, body_style)
        ]
    ]
    guide_table = Table(guide_data, colWidths=[3.6*inch, 3.6*inch])
    guide_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(guide_table)

    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
