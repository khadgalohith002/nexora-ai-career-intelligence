from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


def generate_analysis_pdf(analysis_data, output_path="resume_analysis_report.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("<b>NEXORA Analysis Report</b>", styles["Title"])
    subtitle = Paragraph("<b>AI-Powered Career Intelligence Platform</b>", styles["Heading2"])
    story.append(title)
    story.append(subtitle)
    story.append(Spacer(1, 12))

    for heading, content in analysis_data.items():
        story.append(Paragraph(f"<b>{heading}</b>", styles["Heading2"]))
        story.append(Paragraph(str(content), styles["BodyText"]))
        story.append(Spacer(1, 10))

    doc.build(story)
    return output_path
