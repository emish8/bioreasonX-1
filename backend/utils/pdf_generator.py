import io
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from backend.utils.config import logger

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total page count dynamically for Page X of Y footer."""
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#666666"))
        
        # Draw header rule and title (on pages after the first)
        if self._pageNumber > 1:
            self.drawString(54, 750, "BioReason-X Biomedical Intelligence Report")
            self.setStrokeColor(colors.HexColor("#cccccc"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Draw footer rule and page number
        self.setStrokeColor(colors.HexColor("#e0e0e0"))
        self.setLineWidth(0.5)
        self.line(54, 50, 558, 50)
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 35, page_text)
        self.drawString(54, 35, "CONFIDENTIAL - CLINICAL USE ONLY")
        self.restoreState()


def generate_biomedical_pdf(report_data: Dict[str, Any]) -> bytes:
    """Generates a professional clinical PDF report from consensus report data."""
    logger.info("Initializing PDF generation.")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom color palette
    primary_color = colors.HexColor("#1A365D")  # Deep Blue
    secondary_color = colors.HexColor("#2B6CB0")  # Slate Blue
    accent_color = colors.HexColor("#319795")  # Teal
    text_color = colors.HexColor("#2D3748")  # Charcoal
    border_color = colors.HexColor("#E2E8F0")

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=10
    )

    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=primary_color
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=body_style
    )

    story = []

    # Title & Header
    story.append(Paragraph("BioReason-X Analysis Report", title_style))
    story.append(Paragraph("Mutation → Mechanism → Therapy Intelligence Platform", subtitle_style))
    story.append(Spacer(1, 10))

    # Mutation Overview Table
    mutation_input = report_data.get("mutation_input", "Unknown Variant")
    consensus = report_data.get("consensus", {})
    confidence_score = consensus.get("confidence_score", "N/A")
    mutation_details = report_data.get("mutation_details", {})
    
    gene = mutation_details.get("gene", "N/A")
    mut_type = mutation_details.get("mutation_type", "N/A")
    clin_sig = mutation_details.get("clinical_significance", "N/A")

    overview_data = [
        [Paragraph("Target Mutation", meta_label_style), Paragraph(mutation_input, meta_val_style)],
        [Paragraph("Affected Gene", meta_label_style), Paragraph(gene, meta_val_style)],
        [Paragraph("Mutation Type", meta_label_style), Paragraph(mut_type, meta_val_style)],
        [Paragraph("Clinical Significance", meta_label_style), Paragraph(clin_sig, meta_val_style)],
        [Paragraph("Validation Confidence", meta_label_style), Paragraph(f"{confidence_score}%", meta_val_style)]
    ]

    t = Table(overview_data, colWidths=[2.0*inch, 5.0*inch])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F7FAFC")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Executive Summary Section
    story.append(Paragraph("Executive Summary", h1_style))
    summary_text = consensus.get("final_findings", "No final findings summary generated by the Consensus Agent.")
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))

    # Gene and Protein Impact Section
    story.append(Paragraph("Gene & Protein Disruption", h1_style))
    protein_impact = report_data.get("protein_impact", "No protein impact details compiled.")
    story.append(Paragraph(protein_impact, body_style))
    story.append(Spacer(1, 10))

    # Pathway Cascade Section
    story.append(Paragraph("Pathway Cascade Impact", h1_style))
    pathway_reasoning = report_data.get("pathway_reasoning", {})
    if isinstance(pathway_reasoning, dict):
        pathway_summary = pathway_reasoning.get("pathway_reasoning", "No pathway data provided.")
    else:
        pathway_summary = str(pathway_reasoning)
    story.append(Paragraph(pathway_summary, body_style))
    story.append(Spacer(1, 10))

    # Disease Association Section
    story.append(Paragraph("Disease Associations", h1_style))
    disease_associations = consensus.get("disease_associations", [])
    if disease_associations:
        if isinstance(disease_associations, list):
            for disease in disease_associations:
                story.append(Paragraph(f"• {disease}", bullet_style))
        else:
            story.append(Paragraph(str(disease_associations), body_style))
    else:
        story.append(Paragraph("No direct disease associations cataloged.", body_style))
    story.append(Spacer(1, 10))

    # Therapy Recommendations Table
    story.append(Paragraph("Therapy Recommendations", h1_style))
    therapies = report_data.get("therapies", [])
    
    if therapies:
        table_headers = [
            Paragraph("Therapy / Class", meta_label_style),
            Paragraph("Rationale", meta_label_style),
            Paragraph("Relevance", meta_label_style)
        ]
        therapy_table_data = [table_headers]
        
        for tx in therapies:
            drug = tx.get("drug", tx.get("therapy_name", "N/A"))
            rationale = tx.get("rationale", "N/A")
            level = tx.get("evidence_level", tx.get("relevance", "High"))
            
            therapy_table_data.append([
                Paragraph(drug, body_style),
                Paragraph(rationale, body_style),
                Paragraph(level, body_style)
            ])
            
        tx_table = Table(therapy_table_data, colWidths=[2.0*inch, 4.0*inch, 1.0*inch])
        tx_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(tx_table)
    else:
        story.append(Paragraph("No targeted therapies recommended.", body_style))
    story.append(Spacer(1, 15))

    # Literature Evidence Section
    story.append(Paragraph("Supporting Evidence & Publications", h1_style))
    evidence = report_data.get("literature_evidence", [])
    if evidence:
        for ev in evidence:
            title = ev.get("title", "Unknown Publication")
            abstract = ev.get("abstract", "")
            source = ev.get("source", "Literature Database")
            doc_id = ev.get("id", "N/A")
            
            title_p = Paragraph(f"<b>{doc_id}</b>: {title} ({source})", body_style)
            abs_p = Paragraph(f"<i>Abstract:</i> {abstract}", ParagraphStyle('Abs', parent=body_style, fontSize=9, textColor=colors.HexColor("#4A5568")))
            
            story.append(KeepTogether([title_p, abs_p, Spacer(1, 6)]))
    else:
        story.append(Paragraph("No indexed publications referenced.", body_style))
    story.append(Spacer(1, 10))

    # Final Clinical Recommendation Section
    story.append(Paragraph("Consensus Final Recommendation", h1_style))
    final_rec = consensus.get("final_recommendation", "No clinical recommendations finalized.")
    story.append(Paragraph(final_rec, body_style))
    
    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    logger.info("PDF generation completed.")
    return pdf_bytes
