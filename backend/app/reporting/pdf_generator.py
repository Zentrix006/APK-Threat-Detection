"""
PDF Report Generator
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate PDF threat reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()

    def _add_custom_styles(self):
        """Add custom styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#D32F2F'),
            spaceAfter=30,
            alignment=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1565C0'),
            spaceAfter=12,
            spaceBefore=12
        ))

    def generate(self, report_data: Dict[str, Any], output_path: str) -> None:
        """Generate PDF report"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=0.75*inch
            )
            
            story = []
            
            # Title
            story.append(Paragraph(
                report_data.get("title", "Threat Intelligence Report"),
                self.styles['CustomTitle']
            ))
            story.append(Spacer(1, 0.3*inch))
            
            # Metadata
            meta_data = [
                ["Generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
                ["Risk Score", f"{report_data.get('risk_score', 0)}/100"],
                ["Risk Level", report_data.get('risk_level', 'Unknown').upper()],
            ]
            
            meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
            summary = report_data.get('ai_report', '')[:500]
            if summary:
                story.append(Paragraph(summary, self.styles['BodyText']))
                story.append(Spacer(1, 0.2*inch))
            
            # Key Indicators
            story.append(Paragraph("Key Indicators", self.styles['CustomHeading']))
            indicators = report_data.get('indicators', {})
            
            indicator_data = [
                ["Indicator", "Count"],
                ["Permissions", str(indicators.get('permissions', 0))],
                ["URLs Detected", str(indicators.get('urls', 0))],
                ["IPs Detected", str(indicators.get('ips', 0))],
                ["C2 Communications", str(indicators.get('c2_communications', 0))],
                ["Suspicious APIs", str(indicators.get('suspicious_apis', 0))],
            ]
            
            indicator_table = Table(indicator_data, colWidths=[3*inch, 2*inch])
            indicator_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
            ]))
            story.append(indicator_table)
            story.append(Spacer(1, 0.3*inch))
            
            # MITRE ATT&CK Mapping
            story.append(Paragraph("MITRE ATT&CK Mapping", self.styles['CustomHeading']))
            mitre_mappings = report_data.get('mitre_mappings', [])[:5]
            
            if mitre_mappings:
                mitre_data = [["Tactic", "Technique"]]
                for mapping in mitre_mappings:
                    mitre_data.append([
                        mapping.get('tactic', ''),
                        mapping.get('technique', '')
                    ])
                
                mitre_table = Table(mitre_data, colWidths=[2.5*inch, 3.5*inch])
                mitre_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F57C00')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
                ]))
                story.append(mitre_table)
                story.append(Spacer(1, 0.3*inch))
            
            # Recommendations
            story.append(Paragraph("Recommended Actions", self.styles['CustomHeading']))
            recommendations = report_data.get('recommendations', [])
            
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['BodyText']))
            
            story.append(Spacer(1, 0.5*inch))
            
            # Footer
            story.append(Paragraph(
                "<i>This report is automatically generated and should be reviewed by security professionals.</i>",
                self.styles['Normal']
            ))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise
