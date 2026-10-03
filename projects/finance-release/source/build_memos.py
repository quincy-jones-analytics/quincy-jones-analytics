from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape
P=Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('DB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'));pdfmetrics.registerFontFamily('D',normal='D',bold='DB')
s={'title':ParagraphStyle('title',fontName='DB',fontSize=23,leading=27,textColor=HexColor('#17324d'),spaceAfter=14),'h':ParagraphStyle('h',fontName='DB',fontSize=12,leading=17,spaceBefore=13,spaceAfter=7,textColor=HexColor('#17324d')),'body':ParagraphStyle('body',fontName='D',fontSize=10,leading=15,spaceAfter=8),'small':ParagraphStyle('small',fontName='D',fontSize=8.5,leading=12,spaceAfter=6),'table':ParagraphStyle('table',fontName='D',fontSize=9,leading=13),'th':ParagraphStyle('th',fontName='DB',fontSize=9,leading=13,textColor=white)}
c=json.loads((P/'scenario_captures.json').read_text());fmt=lambda x:'(${:,.0f})'.format(-x) if x<0 else '${:,.0f}'.format(x)
def para(text,style='body'):return Paragraph(escape(str(text)),s[style])
def tab(rows,widths):
 t=Table([[para(x,'th' if i==0 else 'table') for x in row] for i,row in enumerate(rows)],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#17324d')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,0),1,HexColor('#17324d')),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f1f5f9')]) ]));return t
cases=json.loads((P/'case_narratives.json').read_text())
for slug,d in cases.items():
 story=[para('QUINCY JONES / FINANCE DECISION CASE','small'),para(d['title'],'title'),para(d['subtitle'],'body'),para('Synthetic portfolio analysis. Recommendations are proposed; no employer outcomes are claimed.','small'),para('Decision requested','h'),para(d['decision']),para('Financial case','h'),para(d['why']),tab(d['rows'],[116,128,128,128]),para('Tradeoffs and alternatives','h'),para(d['tradeoffs']),PageBreak(),para('Approval and execution','title'),para('Conditions before approval','h'),para(d['conditions']),tab([['Proposed owner','Timing','Required action']]+d['actions'],[130,105,265]),para('Post-decision review','h'),para('The following observations are a separate synthetic review exercise. They demonstrate follow-through without claiming realized results.'),tab(d['review'],[125,100,110,165]),PageBreak(),para('Model basis and review','title'),para('Calculation method','h'),para(d['methods']),para('Material limitations','h'),para(d['limits']),para('Scenario capture and refresh','h'),para('The comparison uses three sequential recalculations of one active Excel build, captured October 3, 2026. Change Assumptions D5 to select a case. Recalculate in Excel and refresh comparisons after changing inputs; PDF figures are a dated snapshot.'),para('Ownership represented','h'),para('Quincy Jones developed this independent portfolio analysis with AI assistance. The package includes the model, controls, alternatives and proposed decision workflow. Proposed corporate owners are roles inside the case, not positions held by Quincy.'),para('Forensic review','h'),para('Independent calculations, reconciliation checks and input-change tests were completed before publication. The downloadable audit explains scope and engine limitations. Artifact-tool input edits and exported caches were checked. A second LibreOffice engine reproduced 2,134 numeric base-case formula caches. Desktop Microsoft Excel was not available; compatibility testing is limited to the stated engines.'),para('Sources','h'),para(d['reference'],'small')]
 def footer(canvas,doc):
  canvas.setFont('D',8);canvas.setFillColor(HexColor('#536174'));canvas.drawString(40,25,'Quincy Jones - synthetic portfolio case - October 3, 2026');canvas.drawRightString(572,25,str(doc.page))
 SimpleDocTemplate(str(P/(slug+'_Decision_Memo.pdf')),pagesize=(612,792),leftMargin=40,rightMargin=40,topMargin=35,bottomMargin=45,title=d['title'],author='Quincy Jones').build(story,onFirstPage=footer,onLaterPages=footer)
(P/'case_narratives.json').write_text(json.dumps(cases,indent=2))
print('Created three complete decision memos')
