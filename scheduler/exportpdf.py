"""Ekspor jadwal seluruh kelas ke PDF."""
import io
from collections import defaultdict
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer

DAY_NAMES = {1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat'}

def build(classes, rows, periods, school, year, semester):
    """Buat PDF seluruh kelas; satu halaman untuk setiap kelas."""
    by_class = defaultdict(dict)
    for row in rows:
        by_class[row['class_id']][(row['day'], row['period'])] = row

    out = io.BytesIO()
    doc = SimpleDocTemplate(
        out, pagesize=landscape(A3), rightMargin=10*mm, leftMargin=10*mm,
        topMargin=9*mm, bottomMargin=9*mm,
        title=f'Jadwal Pelajaran {school}', author=school
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ScheduleTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=16, leading=19, alignment=TA_CENTER, spaceAfter=2*mm)
    sub_style = ParagraphStyle('ScheduleSub', parent=styles['Normal'], fontSize=9, leading=11, alignment=TA_CENTER, spaceAfter=1*mm)
    head_style = ParagraphStyle('ScheduleHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=9, alignment=TA_CENTER, textColor=colors.white)
    cell_style = ParagraphStyle('ScheduleCell', parent=styles['Normal'], fontSize=7, leading=8, alignment=TA_CENTER)
    story = []
    for index, cls in enumerate(classes):
        story.append(Paragraph('JADWAL PELAJARAN', title_style))
        story.append(Paragraph(f'{school} · Tahun Ajaran {year} · Semester {semester}', sub_style))
        story.append(Paragraph(f'<b>Kelas: {cls["name"]}</b>', sub_style))
        data = [[Paragraph('Hari', head_style)] + [Paragraph(f'Jam {p["period"]}<br/>{p["st"]}-{p["en"]}', head_style) for p in periods]]
        for day in range(1, 6):
            line = [Paragraph(f'<b>{DAY_NAMES[day]}</b>', cell_style)]
            for p in periods:
                item = by_class[cls['id']].get((day, p['period']))
                if item:
                    content = f'<b>{item["subject"]}</b><br/>{item["teacher"]}'
                    if item.get('room'):
                        content += f'<br/><font size="6">Ruang: {item["room"]}</font>'
                    line.append(Paragraph(content, cell_style))
                else:
                    line.append(Paragraph('—', cell_style))
            data.append(line)
        usable = landscape(A3)[0] - 20*mm
        first_col = 23*mm
        other_col = (usable - first_col) / max(len(periods), 1)
        table = Table(data, colWidths=[first_col] + [other_col] * len(periods), rowHeights=[14*mm] + [25*mm]*5, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
            ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#e2e8f0')),
            ('GRID', (0,0), (-1,-1), .5, colors.HexColor('#94a3b8')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 2), ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.extend([Spacer(1, 5*mm), table])
        if index < len(classes)-1:
            story.append(PageBreak())
    if not classes:
        story.append(Paragraph('Belum ada data kelas untuk dicetak.', styles['Normal']))
    doc.build(story)
    out.seek(0)
    return out
