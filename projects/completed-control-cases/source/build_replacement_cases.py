from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import date,timedelta
import csv,json,random,sqlite3,hashlib,shutil,html,zipfile,os,re
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent if ROOT.name=='source' else ROOT/'outputs/completed_cases'
OUT.mkdir(exist_ok=True);SRC=OUT/'source';SRC.mkdir(exist_ok=True)
SITE=Path(os.environ.get('CASE_SITE_DIR',str(OUT/'web')));SITE.mkdir(parents=True,exist_ok=True)
R=random.Random(20261003)
def cents(x):return int(Decimal(str(x)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
def write_csv(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def usd(x):return '${:,.0f}'.format(x/100)
checks=[]
def check(name,ok):
 assert ok,name;checks.append(name)

# New generated population, not a reconstruction of the archived Tableau data.
pricing=[];names=['VectorNode','ThermaTrack','FlowGuard','EdgeMeter Pro','PulseSense X1','AeroLink']
listprices=[18000,25000,32000,42000,28000,36000];costs=[10600,14000,20000,24800,18900,20800]
for i in range(480):
 f=i%6;units=R.randint(12,120);bps=R.choice([500,800,1000,1200,1500,1800,2200,2500,2800,3200])
 gross=listprices[f]*units;discount=cents(Decimal(gross)*bps/10000);net=gross-discount;var=costs[f]*units;fulfill=600*units+4000
 pricing.append(dict(TransactionID=f'NEW-P-{i+1:04d}',InvoiceDate=(date(2026,1,1)+timedelta(days=R.randrange(181))).isoformat(),ProductFamily=names[f],CustomerSegment=R.choice(['OEM','Distributor','Service']),Units=units,ListUnitPriceCents=listprices[f],DiscountBps=bps,ListRevenueCents=gross,DiscountCents=discount,RevenueCents=net,VariableCostCents=var,FulfillmentCents=fulfill,ContributionCents=net-var-fulfill,DataStatus='New synthetic portfolio record'))
write_csv(SRC/'new_pricing_transactions.csv',pricing)
family=[]
for name in names:
 g=[x for x in pricing if x['ProductFamily']==name];rev=sum(x['RevenueCents'] for x in g);contr=sum(x['ContributionCents'] for x in g);gross=sum(x['ListRevenueCents'] for x in g)
 family.append(dict(family=name,transactions=len(g),units=sum(x['Units'] for x in g),revenue_cents=rev,contribution_cents=contr,margin=contr/rev,weighted_discount=sum(x['DiscountCents'] for x in g)/gross))
eligible=[x for x in pricing if x['DiscountBps']>1800];baseC=sum(x['ContributionCents'] for x in pricing)
scenarios=[]
for loss in [None,0,.02,.05,.10,.50]:
 rev=con=units=0
 for x in pricing:
  capped=loss is not None and x['DiscountBps']>1800;u=round(x['Units']*(1-loss)) if capped else x['Units'];bps=1800 if capped else x['DiscountBps'];gross=x['ListUnitPriceCents']*u
  nr=gross-cents(Decimal(gross)*bps/10000);vc=x['VariableCostCents']//x['Units']*u;fc=600*u+4000
  rev+=nr;con+=nr-vc-fc;units+=u
 scenarios.append(dict(name='Current terms' if loss is None else f'18% cap / {loss:.0%} eligible unit loss',loss=loss,revenue_cents=rev,contribution_cents=con,margin=con/rev,units=units,incremental_contribution_cents=con-baseC))
fixed=4000*len(eligible);den=sum(cents(Decimal(x['ListRevenueCents'])*Decimal('.82'))-x['VariableCostCents']-600*x['Units'] for x in eligible)
breakloss=1-(sum(x['ContributionCents'] for x in eligible)+fixed)/den
totalRev=sum(x['RevenueCents'] for x in pricing);totalContr=baseC;low=min(family,key=lambda x:x['margin'])
price_metrics=dict(population=480,revenue_cents=totalRev,contribution_cents=totalContr,margin=totalContr/totalRev,weighted_discount=sum(x['DiscountCents'] for x in pricing)/sum(x['ListRevenueCents'] for x in pricing),eligible_orders=len(eligible),eligible_volume_break_even_loss=breakloss,lowest_family=low['family'],families=family,scenarios=scenarios)
check('Pricing new population is 480 unique transaction IDs',len(pricing)==480 and len({x['TransactionID'] for x in pricing})==480)
for x in pricing:
 check(x['TransactionID']+' price and contribution reconcile',x['RevenueCents']==x['ListRevenueCents']-x['DiscountCents'] and x['ContributionCents']==x['RevenueCents']-x['VariableCostCents']-x['FulfillmentCents'])
check('Pricing family totals reconcile',sum(x['revenue_cents'] for x in family)==totalRev and sum(x['contribution_cents'] for x in family)==totalContr)
check('Pricing base scenario matches raw transactions',scenarios[0]['contribution_cents']==baseC and scenarios[0]['revenue_cents']==totalRev)
check('Cap cannot reduce net revenue with no volume loss',scenarios[1]['revenue_cents']>=totalRev)

# New 700-row invoice population. Vendor/invoice pairs intentionally include duplicates.
invoices=[]
for i in range(700):
 amount=R.randint(40,3000)*100;po='PO-'+str(10000+i);supplier='S-'+str(1+i%35).zfill(3);invoice='INV-'+str(i+1).zfill(5)
 missing=i%11==0;receipt=i%17==0
 invoices.append(dict(RecordID=f'NEW-I-{i+1:04d}',SupplierID=supplier,VendorInvoiceNumber=invoice,InvoiceDate=(date(2026,1,1)+timedelta(days=i%181)).isoformat(),AmountCents=amount,PaymentStatus='Paid' if i%3==0 else 'Unpaid',PurchaseOrderID='' if missing else po,ReceiptMatched=0 if receipt else 1,GoodsReceivedCents=amount if not receipt else max(0,amount-R.randint(1,20)*100),DataStatus='New synthetic portfolio record'))
duplicate_truth=[]
for pair in range(20):
 a=pair*5;b=600+pair; original=invoices[a];repeat=invoices[b]
 for key in ['SupplierID','VendorInvoiceNumber','InvoiceDate','AmountCents']:repeat[key]=original[key]
 # Ten confirmed duplicate repeats, five valid installments, five unresolved groups.
 confirmed=pair<10
 original['PaymentStatus']='Paid' if pair%2==0 else 'Unpaid';repeat['PaymentStatus']='Paid' if pair%2==0 else 'Unpaid'
 outcome='Confirmed' if confirmed else 'Valid installment' if pair<15 else 'Unresolved'
 duplicate_truth.extend([{'RecordID':original['RecordID'],'GroupID':f'DUP-{pair+1:02d}','Role':'Original','ConfirmedDuplicate':0,'ReviewOutcome':outcome,'Evidence':'Synthetic original posting verified' if outcome=='Confirmed' else 'Synthetic valid split installment' if outcome=='Valid installment' else 'Review evidence pending'}, {'RecordID':repeat['RecordID'],'GroupID':f'DUP-{pair+1:02d}','Role':'Repeated posting','ConfirmedDuplicate':int(confirmed),'ReviewOutcome':outcome,'Evidence':'Synthetic duplicate repeat confirmed' if confirmed else 'Synthetic valid split installment' if outcome=='Valid installment' else 'Review evidence pending'}])
for x in invoices[-2:]:x['ReceiptMatched']=None;x['GoodsReceivedCents']=None
write_csv(SRC/'new_supplier_invoices.csv',invoices);write_csv(SRC/'synthetic_review_evidence.csv',duplicate_truth)
by_key={}
for x in invoices:by_key.setdefault((x['SupplierID'],x['VendorInvoiceNumber'],x['AmountCents']),[]).append(x)
evidence={x['RecordID']:x for x in duplicate_truth};classified=[]
for x in invoices:
 group=by_key[(x['SupplierID'],x['VendorInvoiceNumber'],x['AmountCents'])];duplicate=len(group)>1;ev=evidence.get(x['RecordID'],{})
 confirmed=ev.get('ConfirmedDuplicate',0)==1;missing=not x['PurchaseOrderID'];mismatch=x['ReceiptMatched']==0;unknown_receipt=x['ReceiptMatched'] is None
 unresolved=duplicate and ev.get('ReviewOutcome')=='Unresolved'
 flagged=confirmed or unresolved or missing or mismatch or unknown_receipt
 # Mutually exclusive PRIMARY category for allocating invoice-level gross review value.
 category='Confirmed duplicate repeat' if confirmed else 'Duplicate candidate - unresolved' if unresolved else 'Missing PO' if missing else 'Receipt evidence missing' if unknown_receipt else 'Receipt mismatch' if mismatch else 'Clean'
 repeat_candidate=duplicate and x['RecordID']!=min(r['RecordID'] for r in group)
 classified.append(dict(**x,DuplicateCandidate=int(duplicate),DuplicateReviewOutcome=ev.get('ReviewOutcome','Not a duplicate candidate'),ConfirmedDuplicateRepeat=int(confirmed),CandidateRepeat=int(repeat_candidate),MissingPO=int(missing),ReceiptMismatch=int(mismatch),ReceiptEvidenceMissing=int(unknown_receipt),PrimaryReviewCategory=category,GrossReviewCents=x['AmountCents'] if flagged else 0,UnpaidReviewCents=x['AmountCents'] if flagged and x['PaymentStatus']=='Unpaid' else 0,PaidConfirmedPotentialRecoveryCents=x['AmountCents'] if confirmed and x['PaymentStatus']=='Paid' else 0,UnpaidConfirmedDuplicateAvoidanceCents=x['AmountCents'] if confirmed and x['PaymentStatus']=='Unpaid' else 0,RealizedRecoveryCents=0))
write_csv(OUT/'classified_supplier_invoices.csv',classified)
cats=[]
for category in ['Confirmed duplicate repeat','Duplicate candidate - unresolved','Missing PO','Receipt evidence missing','Receipt mismatch','Clean']:
 g=[x for x in classified if x['PrimaryReviewCategory']==category];cats.append(dict(category=category,records=len(g),gross_review_cents=sum(x['GrossReviewCents'] for x in g)))
invoice_metrics=dict(population=700,total_invoice_cents=sum(x['AmountCents'] for x in invoices),flagged_records=sum(x['GrossReviewCents']>0 for x in classified),gross_review_cents=sum(x['GrossReviewCents'] for x in classified),unpaid_review_cents=sum(x['UnpaidReviewCents'] for x in classified),paid_confirmed_potential_recovery_cents=sum(x['PaidConfirmedPotentialRecoveryCents'] for x in classified),unpaid_confirmed_duplicate_avoidance_cents=sum(x['UnpaidConfirmedDuplicateAvoidanceCents'] for x in classified),realized_recovery_cents=0,duplicate_groups=20,candidate_records=sum(x['DuplicateCandidate'] for x in classified),confirmed_repeat_records=sum(x['ConfirmedDuplicateRepeat'] for x in classified),unresolved_duplicate_groups=5,cleared_duplicate_records=20,missing_receipt_records=2,overlap_records=sum(int(x['DuplicateReviewOutcome']=='Unresolved')+x['ConfirmedDuplicateRepeat']+x['MissingPO']+x['ReceiptMismatch']+x['ReceiptEvidenceMissing']>1 for x in classified),naive_overlapping_flag_cents=sum(x['AmountCents']*(int(x['DuplicateReviewOutcome']=='Unresolved')+x['ConfirmedDuplicateRepeat']+x['MissingPO']+x['ReceiptMismatch']+x['ReceiptEvidenceMissing']) for x in classified),categories=cats)
check('Invoice population is 700 unique record IDs',len(invoices)==700 and len({x['RecordID'] for x in invoices})==700)
check('Duplicate groups count exactly 20',sum(len(g)>1 for g in by_key.values())==20)
check('Confirmed repeated postings count exactly 10',invoice_metrics['confirmed_repeat_records']==10)
check('Primary review categories reconcile to entire population',sum(x['records'] for x in cats)==700)
check('Primary review values are non-overlapping',sum(x['gross_review_cents'] for x in cats)==invoice_metrics['gross_review_cents'])
check('Overlap exists and naive sum overstates review value',invoice_metrics['overlap_records']>0 and invoice_metrics['naive_overlapping_flag_cents']>invoice_metrics['gross_review_cents'])
check('Null receipt evidence remains a review exception',sum(x['ReceiptEvidenceMissing'] for x in classified)==2 and all(x['GrossReviewCents']>0 for x in classified if x['ReceiptEvidenceMissing']))
check('Cleared candidates do not stay in unresolved duplicate category',all(x['PrimaryReviewCategory']!='Duplicate candidate - unresolved' for x in classified if x['DuplicateReviewOutcome'] in ['Valid installment','Confirmed']))
check('Severe volume-loss case reverses modeled gain',scenarios[-1]['incremental_contribution_cents']<0)
for x in classified:
 check(x['RecordID']+' paid/unpaid and duplicate evidence limits',x['RealizedRecoveryCents']==0 and (x['PaidConfirmedPotentialRecoveryCents']==0 or x['PaymentStatus']=='Paid' and x['ConfirmedDuplicateRepeat']==1) and (x['UnpaidConfirmedDuplicateAvoidanceCents']==0 or x['PaymentStatus']=='Unpaid' and x['ConfirmedDuplicateRepeat']==1))

# Independent SQL aggregation of raw record controls and duplication, including null receipt test.
con=sqlite3.connect(':memory:');con.execute('CREATE TABLE pricing(id TEXT PRIMARY KEY, family TEXT, gross INTEGER, discount INTEGER, net INTEGER, vc INTEGER, fulfillment INTEGER, contribution INTEGER)')
con.executemany('INSERT INTO pricing VALUES(?,?,?,?,?,?,?,?)',[(x['TransactionID'],x['ProductFamily'],x['ListRevenueCents'],x['DiscountCents'],x['RevenueCents'],x['VariableCostCents'],x['FulfillmentCents'],x['ContributionCents']) for x in pricing])
check('SQL pricing arithmetic has zero exceptions',con.execute('SELECT COUNT(*) FROM pricing WHERE net!=gross-discount OR contribution!=net-vc-fulfillment').fetchone()[0]==0)
check('SQL pricing sums match Python',con.execute('SELECT SUM(net),SUM(contribution) FROM pricing').fetchone()==(totalRev,totalContr))
con.execute('CREATE TABLE invoices(id TEXT PRIMARY KEY, supplier TEXT, number TEXT, amount INTEGER, paid TEXT, missing_po INTEGER, receipt INTEGER)');con.executemany('INSERT INTO invoices VALUES(?,?,?,?,?,?,?)',[(x['RecordID'],x['SupplierID'],x['VendorInvoiceNumber'],x['AmountCents'],x['PaymentStatus'],int(not x['PurchaseOrderID']),x['ReceiptMatched']) for x in invoices])
check('SQL invoice source control matches',con.execute('SELECT COUNT(*),SUM(amount) FROM invoices').fetchone()==(700,invoice_metrics['total_invoice_cents']))
sqlgroups=con.execute('SELECT supplier,number,amount,COUNT(*) FROM invoices GROUP BY supplier,number,amount HAVING COUNT(*)>1').fetchall();check('SQL duplicate candidate groups match Python',len(sqlgroups)==20 and sum(x[3] for x in sqlgroups)==40)
con.close()
(SRC/'audit_queries.sql').write_text('''-- Values are integer cents. Candidate matching is a review signal, not proof of a duplicate.
SELECT COUNT(*), SUM(net), SUM(contribution) FROM pricing;
SELECT family, SUM(net) AS revenue_cents, SUM(contribution) AS contribution_cents,
       CAST(SUM(contribution) AS REAL)/NULLIF(SUM(net),0) AS weighted_contribution_margin
FROM pricing GROUP BY family;
SELECT COUNT(*), SUM(amount) FROM invoices;
SELECT supplier, number, amount, COUNT(*) AS candidate_count
FROM invoices GROUP BY supplier, number, amount HAVING COUNT(*)>1;
-- Keep receipt-null rows unresolved in real source data. Never treat NULL as a clean match.
SELECT * FROM invoices WHERE receipt IS NULL;
''')
(OUT/'pricing_metrics.json').write_text(json.dumps(price_metrics,indent=2));(OUT/'invoice_metrics.json').write_text(json.dumps(invoice_metrics,indent=2));(OUT/'case_audit.json').write_text(json.dumps(dict(date='2026-10-03',passed=len(checks),failed=0,checks=checks,scope='New synthetic replacements; not recovered Tableau originals',native_tableau_tested=False,desktop_excel_tested=False),indent=2))

# Decision memos: one decision page and one method/accountability page.
regular='Helvetica';bold='Helvetica-Bold'
if (SRC/'DejaVuSans.ttf').exists():
 pdfmetrics.registerFont(TTFont('PortfolioSans',str(SRC/'DejaVuSans.ttf')));pdfmetrics.registerFont(TTFont('PortfolioSans-Bold',str(SRC/'DejaVuSans-Bold.ttf')));regular='PortfolioSans';bold='PortfolioSans-Bold'
styles=getSampleStyleSheet();styles['Normal'].fontName=regular;styles['Normal'].fontSize=10;styles['Normal'].leading=14;styles['Heading1'].fontName=bold;styles['Heading2'].fontName=bold;styles['Heading1'].textColor=colors.HexColor('#17324d');styles['Heading1'].fontSize=22;styles['Heading2'].textColor=colors.HexColor('#17324d');styles['Heading2'].fontSize=13
def para(s):return Paragraph(html.escape(s),styles['Normal'])
def table(data,widths):
 t=Table([[para(str(c)) for c in row] for row in data],colWidths=widths);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eef5')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f4f7fa')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));return t
def memo(name,title,decision,summary,data,actions,limits,method):
 story=[Paragraph('QUINCY JONES / INDEPENDENT FINANCE CASE',styles['Normal']),Spacer(1,12),Paragraph(title,styles['Heading1']),para('New synthetic portfolio analysis | October 3, 2026'),Spacer(1,12),Paragraph('Decision requested',styles['Heading2']),para(decision),Paragraph('Financial case',styles['Heading2']),para(summary),Spacer(1,12),table(data,[190,158,158]),Paragraph('Tradeoffs and conditions',styles['Heading2']),para(limits),PageBreak(),Paragraph('Execution and verification',styles['Heading1']),para('Proposed corporate owners are simulation roles, not positions held by Quincy. All actions begin as Proposed.'),Spacer(1,12),table([['Owner','When','Required action']]+actions,[138,85,283]),Paragraph('Calculation method',styles['Heading2']),para(method),Paragraph('Forensic review',styles['Heading2']),para(f'{len(checks):,} record, population, reconciliation and SQL/Python checks passed across the two cases. Source data, review evidence and full source code are provided. These checks establish consistency of generated records; they do not validate real customers, supplier claims or realized outcomes.'),Paragraph('Follow-up',styles['Heading2']),para('Compare actual source records and approved decisions to the modeled baseline at the next review. Record the evidence and responsible reviewer before changing an action status. No realized savings or recoveries are claimed.')]
 def footer(c,d):c.setFont(regular,8);c.setFillColor(colors.HexColor('#617186'));c.drawString(48,30,'Quincy Jones - new synthetic case - October 3, 2026');c.drawRightString(564,30,str(d.page))
 SimpleDocTemplate(str(OUT/name),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=42,bottomMargin=48).build(story,onFirstPage=footer,onLaterPages=footer)
pm=price_metrics;im=invoice_metrics
pd=f'Pilot an 18% discount cap on eligible orders, beginning with {low["family"]}, subject to customer-retention and quote validation. Full-portfolio scenarios below are not forecasts of the smaller pilot.'
ps=f'The 480 generated transactions produce {usd(totalRev)} revenue and {usd(totalContr)} contribution ({pm["margin"]:.1%}). The 18% cap with 5% eligible unit loss changes modeled contribution by {usd(scenarios[3]["incremental_contribution_cents"])} across all eligible orders. The continuous break-even eligible volume loss is {breakloss:.1%}; this is an assumption threshold, not measured customer elasticity.'
pl='Demand response is assumed. Fixed order fulfillment remains payable and units are rounded to whole units. No contract-right, tax, competitor-price or customer-retention evidence is available. Pilot approval requires real quote and customer data. Results cover January-June synthetic transactions, not an annualized earnings forecast.'
pactions=[['Commercial + Finance','Before pilot','Validate customer terms, cost definitions and retention assumption'],['Sales lead','Week 1','Choose eligible accounts and document approval exceptions'],['Pricing analyst','Weekly','Track realized price, retained units and contribution against baseline'],['Finance lead','After 30 days','Expand, revise or stop based on actual contribution and retention']]
pdata=[['Case','Revenue','Contribution']]+[[s['name'],usd(s['revenue_cents']),usd(s['contribution_cents'])] for s in scenarios]
memo('Pricing_Decision_Memo.pdf','Discount discipline and contribution',pd,ps,pdata,pactions,pl,'All money is integer cents. Net revenue equals list revenue less discounts; contribution deducts variable product and fulfillment costs. Weighted discount uses list revenue as denominator. Weighted contribution margin uses net revenue. The cap changes only eligible orders; retained unit volumes are explicit assumptions.')
idc='Route confirmed duplicate repeats to payment-status review; hold unresolved unpaid control exceptions until supporting evidence is obtained. Do not book the gross review queue as savings or recovery.'
iss=f'Across 700 generated invoice postings, {im["flagged_records"]} require review with gross non-overlapping value {usd(im["gross_review_cents"])}. Paid confirmed duplicate repeats have {usd(im["paid_confirmed_potential_recovery_cents"])} potential recovery, and unpaid confirmed repeats have {usd(im["unpaid_confirmed_duplicate_avoidance_cents"])} potential avoidance. Realized recovery is $0. These categories are not additive to the gross review queue.'
il='Matching identifiers creates a candidate, not proof. Synthetic evidence confirms ten repeated postings, clears five installment groups, and leaves five groups unresolved. Original confirmed postings are cleared from duplicate review. Missing POs and receipt evidence are not automatically losses. Supplier consent and collection success remain untested.'
iactions=[['AP reviewer','Day 1','Reconcile all 700 postings and identify repeat versus original'],['AP + Procurement','Days 1-3','Obtain PO/receipt evidence for unpaid exceptions'],['Controller','Before action','Approve duplicate decisions and accounting treatment'],['Supplier relations','After approval','Request credit for paid confirmed repeat; record response'],['Finance lead','Weekly','Reconcile credits/cash before recognizing realized recovery']]
idata=[['Queue','Records / basis','Value'],['Gross unique review',str(im['flagged_records']),usd(im['gross_review_cents'])],['Unpaid review','All unpaid flagged postings',usd(im['unpaid_review_cents'])],['Paid confirmed repeat','Subset; potential recovery',usd(im['paid_confirmed_potential_recovery_cents'])],['Unpaid confirmed repeat','Subset; potential avoidance',usd(im['unpaid_confirmed_duplicate_avoidance_cents'])],['Realized recovery','No real action performed','$0']]
memo('Invoice_Controls_Decision_Memo.pdf','Invoice exceptions and cash control',idc,iss,idata,iactions,il,'Record IDs identify each posting. Duplicate matching uses supplier, invoice number and exact cents; separate synthetic evidence determines review outcome. Missing receipt evidence remains unresolved. Each flagged posting is allocated once using a primary-category hierarchy. Recovery candidates include only paid confirmed repeats; unpaid confirmed repeats are separately identified. Gross review value is workload, not a loss estimate.')

def h(s):return html.escape(str(s))
def htmltable(rows):return '<div class="tablewrap"><table><thead><tr>'+''.join('<th>'+h(v)+'</th>' for v in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+h(v)+'</td>' for v in r)+'</tr>' for r in rows[1:])+'</tbody></table></div>'
def page(slug,title,decision,summary,data,actions,limits,method,pdf,chart,extra=''):
 dest=SITE/slug;dest.mkdir(exist_ok=True);shutil.copy2(OUT/pdf,dest/pdf)
 body=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)} | Quincy Jones</title><meta name="description" content="New synthetic finance case with full records and reproducible audit"><link rel="stylesheet" href="/finance-cases.css"></head><body><nav><div class="wrap"><b>QUINCY JONES / FINANCE CASES</b><a href="/#new-control-cases">Portfolio</a></div></nav><main class="wrap"><div class="eyebrow">Source records • decision • execution</div><h1>{h(title)}</h1><p class="flag"><b>New synthetic replacement case.</b> Built from newly generated records, with AI assistance. This is not a reconstruction of the archived Tableau dashboard. Proposed owners and modeled outcomes are illustrative.</p><section class="panel"><h2>Decision requested</h2><p>{h(decision)}</p><p>{h(summary)}</p><a class="btn" href="/{slug}/{pdf}" download>Decision memo · PDF</a></section><section class="panel"><h2>Financial evidence</h2>{chart}{htmltable(data)}{extra}</section><section class="panel"><h2>Ownership and execution</h2><p>All actions are Proposed. Roles describe a simulated corporate workflow.</p>{htmltable([['Proposed owner','Timing','Required action']]+actions)}</section><section class="panel"><h2>Method and limits</h2><p>{h(method)}</p><p>{h(limits)}</p><p>{len(checks):,} source, population, arithmetic and SQL/Python checks passed across both cases. Native Tableau rendering and publication are not claimed.</p><a href="/{slug}/README.md">Source dictionary and reproduction</a> · <a href="/{slug}/case_audit.json">Audit evidence</a> · <a href="/completed-cases/Completed_Pricing_and_Invoice_Cases.zip" download>Full sources and both cases</a></section></main></body></html>'''
 (SITE/(slug+'.html')).write_text(body)
 for name in ['case_audit.json']:shutil.copy2(OUT/name,dest/name)
 return dest
def bars(rows,label,value):
 maxv=max(x[value] for x in rows);return '<figure aria-label="'+h(label)+'"><div style="display:grid;gap:12px">'+''.join(f'<div><b>{h(x[label])}</b> <span>{usd(x[value])}</span><div style="height:16px;width:{x[value]/maxv*100:.2f}%;background:#087a7e;border-radius:3px"></div></div>' for x in rows)+'</div><figcaption class="fine">Dollar comparison from the generated source records. Bars use a zero baseline.</figcaption></figure>'
pDest=page('pricing-control-case','Discount discipline and contribution',pd,ps,pdata,pactions,pl,'Revenue-weighted contribution margin = SUM(ContributionCents)/SUM(RevenueCents). Weighted discount = SUM(DiscountCents)/SUM(ListRevenueCents). Averages of family margins are not used. Capped discount scenarios model retained eligible units and include direct and fulfillment costs.','Pricing_Decision_Memo.pdf',bars(family,'family','contribution_cents'),htmltable([['Family','Revenue','Contribution margin','Weighted discount']]+[[x['family'],usd(x['revenue_cents']),f'{x["margin"]:.1%}',f'{x["weighted_discount"]:.1%}'] for x in family])+'<p><a href="/pricing-control-case/new_pricing_transactions.csv" download>All 480 new transaction records</a></p>')
iDest=page('invoice-control-case','Invoice exceptions and cash control',idc,iss,idata,iactions,il,'Each posting receives one primary review category. All flags remain visible for investigation. Evidence confirms ten repeats, clears five installment groups and leaves five groups unresolved. Cleared candidates leave the duplicate queue; other control flags remain actionable. Gross review value measures workload, not recoverable loss.','Invoice_Controls_Decision_Memo.pdf',bars(im['categories'],'category','gross_review_cents'),htmltable([['Primary category','Posting count','Gross review value']]+[[x['category'],x['records'],usd(x['gross_review_cents'])] for x in im['categories']])+'<p><a href="/invoice-control-case/new_supplier_invoices.csv" download>All 700 new invoice postings</a> · <a href="/invoice-control-case/classified_supplier_invoices.csv" download>Posting-level classifications</a> · <a href="/invoice-control-case/synthetic_review_evidence.csv" download>Synthetic review evidence</a></p>')
shutil.copy2(SRC/'new_pricing_transactions.csv',pDest/'new_pricing_transactions.csv');shutil.copy2(SRC/'new_supplier_invoices.csv',iDest/'new_supplier_invoices.csv');shutil.copy2(SRC/'synthetic_review_evidence.csv',iDest/'synthetic_review_evidence.csv');shutil.copy2(OUT/'classified_supplier_invoices.csv',iDest/'classified_supplier_invoices.csv')
for dest in [pDest,iDest]:
 (dest/'README.md').write_text('''# New synthetic finance cases

Generated October 3, 2026 with fixed seed 20261003. These are new populations, not recovered records from the archived Tableau projects. Download the full package for source code and audit queries.

Pricing: TransactionID is unique; Units is a whole-unit count. All monetary fields end in Cents and use integer USD cents; divide by 100 for dollar display. DiscountBps is basis points (1800 means 18%). RevenueCents = ListRevenueCents - DiscountCents. ContributionCents = RevenueCents - VariableCostCents - FulfillmentCents. Fulfillment uses $6 per unit plus $40 per order. Weighted contribution uses revenue, and weighted discount uses list revenue. Dates cover January-June 2026. The discount-cap simulation retains explicit eligible-unit volumes, rounded to whole units; it does not measure actual customer elasticity.

Invoices: RecordID is unique, while vendor invoice numbers intentionally repeat. PaymentStatus is Paid or Unpaid. Missing PurchaseOrderID is a review flag. ReceiptMatched is 1 for matched, 0 for unmatched and blank for missing evidence; two missing-evidence records stay in review. Monetary values are USD cents. The separate synthetic evidence identifies confirmed original/repeated postings, valid installments and unresolved groups. Classifications preserve every flag but allocate gross review value once to a primary category. Potential recovery/avoidance are subsets and must not be added to gross review. Realized recovery remains zero.

Reproduce: run `python source/build_replacement_cases.py` from the extracted package. Python uses its standard library plus reportlab. The deterministic data generation and SQL checks are contained in that one script. Outputs are generated in the package folder, with standalone HTML under web. AI assisted construction and review; no corporate outcomes or native Tableau testing are claimed.
''')
shutil.copy2(pDest/'README.md',OUT/'README.md')
if Path(__file__).resolve()!=(SRC/'build_replacement_cases.py').resolve():shutil.copy2(Path(__file__),SRC/'build_replacement_cases.py')
index=SITE/'index.html';s=index.read_text() if index.exists() else '<html><head><title>New synthetic finance cases</title></head><body><main></main></body></html>';section='''<section id="new-control-cases" class="projects"><div class="wrap"><div class="section-head"><div><div class="eyebrow">New synthetic cases · complete source records</div><h2>Pricing discipline and invoice control.</h2></div><p>Two new reproducible cases replace the missing-source demonstrations in the featured work. Original Tableau dashboards remain archived.</p></div><div class="cards"><article class="card"><span class="tag">480 new synthetic transactions</span><h3>Discount discipline and contribution</h3><p>Weighted economics, retention sensitivity, a proposed pilot and a decision memo.</p><a href="/pricing-control-case">Open pricing case →</a></article><article class="card"><span class="tag">700 new synthetic invoice postings</span><h3>Invoice exceptions and cash control</h3><p>Separate duplicate candidates, confirmed repeats, review workload and potential recovery.</p><a href="/invoice-control-case">Open invoice case →</a></article></div></div></section>'''
if 'id="new-control-cases"' in s:s=re.sub(r'<section id="new-control-cases".*?</section>',section,s,count=1,flags=re.S)
elif '<section id="public-work"' in s:s=s.replace('<section id="public-work"',section+'<section id="public-work"',1)
else:s=s.replace('</main>',section+'</main>',1)
index.write_text(s)
if (SRC/'finance-cases.css').exists():shutil.copy2(SRC/'finance-cases.css',SITE/'finance-cases.css')
files=[p for p in OUT.rglob('*') if p.is_file() and p.suffix in ['.csv','.json','.md','.py','.pdf','.css','.ttf','.txt'] and 'pdf_review' not in p.parts and 'web' not in p.parts and p.name not in ['build_results.json','SHA256SUMS.txt']]
(OUT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(OUT).as_posix()+'\n' for p in sorted(files)))
with zipfile.ZipFile(OUT/'Completed_Pricing_and_Invoice_Cases.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[OUT/'SHA256SUMS.txt']:z.write(p,p.relative_to(OUT).as_posix())
(SITE/'completed-cases').mkdir(exist_ok=True);shutil.copy2(OUT/'Completed_Pricing_and_Invoice_Cases.zip',SITE/'completed-cases/Completed_Pricing_and_Invoice_Cases.zip')
print(json.dumps({'pricing':pm,'invoice':im,'checks':len(checks)},indent=2))
