# reportagent.py
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Spacer, SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

class ReportAgent:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, analysis, filename=None):
        """
        Generate PDF report including:
        - Technical indicators
        - Sentiment analysis
        - LLM summary
        - Charts
        """
        if filename is None:
            filename = f"{analysis['ticker']}_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        filepath = os.path.join(self.output_dir, filename)

        # Use SimpleDocTemplate for easier text wrapping
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        story = []
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        heading_style = styles['Heading2']

        # Title
        story.append(Paragraph(f"Investment Analysis Report: {analysis['ticker']}", heading_style))
        story.append(Spacer(1, 12))

        # Date Range
        story.append(Paragraph(f"Date Range: {analysis['start']} → {analysis['end']}", normal_style))
        story.append(Spacer(1, 12))

        # Technical Indicators
        story.append(Paragraph("Technical Indicators:", heading_style))
        for key, value in analysis.get("technical", {}).items():
            story.append(Paragraph(f"{key}: {value}", normal_style))
        story.append(Spacer(1, 12))

        # Sentiment
        story.append(Paragraph("News Sentiment:", heading_style))
        for key, value in analysis.get("sentiment", {}).items():
            story.append(Paragraph(f"{key}: {value}", normal_style))
        story.append(Spacer(1, 12))

        # Final Signal
        story.append(Paragraph("Final Recommendation:", heading_style))
        story.append(Paragraph(f"Signal: {analysis.get('final_signal', 'N/A')}", normal_style))
        story.append(Spacer(1, 12))

        # Summary
        story.append(Paragraph("Summary:", heading_style))
        story.append(Paragraph(analysis.get("summary", "N/A"), normal_style))
        story.append(Spacer(1, 24))

        # Charts
        for chart in analysis.get("charts", []):
            # chart can be a dict or string depending on your VisualizationAgent
            if isinstance(chart, dict):
                # If indicators chart dict
                for key, path in chart.items():
                    if os.path.exists(path):
                        try:
                            img = Image(path)
                            max_width = 6.5 * inch
                            aspect = img.imageHeight / img.imageWidth
                            img.drawWidth = max_width
                            img.drawHeight = max_width * aspect
                            story.append(img)
                            story.append(Spacer(1, 12))
                        except Exception as e:
                            print(f"Error adding chart {path}: {e}")
            else:
                # Single chart path
                if os.path.exists(chart):
                    try:
                        img = Image(chart)
                        max_width = 6.5 * inch
                        aspect = img.imageHeight / img.imageWidth
                        img.drawWidth = max_width
                        img.drawHeight = max_width * aspect
                        story.append(img)
                        story.append(Spacer(1, 12))
                    except Exception as e:
                        print(f"Error adding chart {chart}: {e}")

        # Build PDF
        doc.build(story)
        return filepath
