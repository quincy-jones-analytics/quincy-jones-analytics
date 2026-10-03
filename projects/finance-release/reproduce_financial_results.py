"""Independent calculation checks. Reads XLSX files; never writes workbooks."""
import csv,json,math,hashlib,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent
checks=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def close(name,a,b,tol=.02):check(name,abs(float(a)-float(b))<=tol)
def read_xlsx(path):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        rel={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for sh in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns):
            target=rel[sh.attrib['{'+ns['r']+'}id']];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            cells={}
            for c in ET.fromstring(z.read(target)).findall('.//m:sheetData/m:row/m:c',ns):
                t=c.attrib.get('t');v=c.find('m:v',ns);f=c.find('m:f',ns)
                if t=='inlineStr':value=''.join(c.find('m:is',ns).itertext())
                elif v is None:value=None
                elif t=='s':value=strings[int(v.text)]
                elif t in ['str','e']:value=v.text
                else:
                    try:value=float(v.text)
                    except:value=v.text
                cells[c.attrib['r']]={'value':value,'formula':f.text if f is not None else None,'type':t}
            result[sh.attrib['name']]=cells
    return result
captured=json.loads((ROOT/'scenario_captures.json').read_text())
models={name:read_xlsx(ROOT/(name+'.xlsx')) for name in captured}
for name,sheets in models.items():
    for sheet,cells in sheets.items():
        check(name+': '+sheet+' cached errors absent',not any(c['type']=='e' for c in cells.values()))
        check(name+': '+sheet+' formula caches present',not any(c['formula'] and c['value'] is None for c in cells.values()))
        if sheet!='Audit':check(name+': '+sheet+' does not depend on Audit',not any(c['formula'] and 'Audit' in c['formula'] for c in cells.values()))
    for cell,rec in sheets['Audit'].items():
        if cell.startswith('D') and rec['formula']:close(name+': reconciliation '+cell,rec['value'],0)
def val(name,sheet,cell):return models[name][sheet][cell]['value']

# Operating forecast: reconstruct segment economics from the raw H1 sheet.
raw=[]
for row in range(7,25):raw.append({c:val('Operating_Plan','Source',c+str(row)) for c in 'CDEFGHI'})
with (ROOT/'operating_h1_source.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['Excel_month_serial','segment','units','price','variable_cost','fixed_cost','opex']);w.writerows([[x[c] for c in 'CDEFGHI'] for x in raw])
growth=[(.012,.018,.025,.020),(-.012,0,.035,.025),(.027,.025,.020,.018)]
original_fixed=[89000,76000,42000];seasons=[1.01,1.04,1.01,1.08,1.13,1.17]
independent={};details=[]
for idx,(ug,pg,cg,og) in enumerate(growth):
    h1rev=sum(x['E']*x['F'] for x in raw);h1eb=sum(x['E']*(x['F']-x['G'])-x['H']-x['I'] for x in raw)
    rev=h1rev;eb=h1eb;cash=500000;prior_wc=sum(x['E']*x['F'] for x in raw[-3:])*35/30-sum(x['E']*x['G'] for x in raw[-3:])*20/30;cashs=[]
    for k,season in enumerate(seasons,1):
        monthrev=monthvc=monthfixed=monthopex=0
        for j,x in enumerate(raw[-3:]):
            units=math.floor(x['E']*(1+ug)**k*season+.5);price=x['F']*(1+pg)**k;cost=x['G']*(1+cg)**k
            monthrev+=units*price;monthvc+=units*cost
            monthfixed+=original_fixed[j]*(1+.001*(6+k))*(1+cg*.35)**k
            monthopex+=x['I']/(1+.002*6)*(1+.002*(6+k))*(1+og)**k
        ebitda=monthrev-monthvc-monthfixed-monthopex;ebit=ebitda-20000;tax=max(ebit,0)*.25
        wc=monthrev*35/30-monthvc*20/30;cash+=ebit-tax+20000-(wc-prior_wc)-25000;prior_wc=wc;cashs.append(cash);rev+=monthrev;eb+=ebitda
        details.append({'model':'Operating_Plan','case':idx+1,'period':6+k,'revenue':monthrev,'ebitda':ebitda,'ending_cash':cash})
    observed=captured['Operating_Plan'][idx]
    for key,expected in [('revenue',rev),('ebitda',eb),('endingCash',cash),('minCash',min(cashs))]:close('Operating case '+str(idx+1)+' '+key,observed[key],expected)
    close('Operating margin '+str(idx+1),observed['margin'],eb/rev,.000001)
    if not idx:
        # July exact quantity / price / cost bridge is verified separately from its Excel check.
        reference=sum(math.floor(x['E']*1.01+.5)*(x['F']-x['G'])-x['H']-x['I'] for x in raw[-3:])
        close('Operating July reference plan',val('Operating_Plan','Variance','D12'),reference)
    independent.setdefault('Operating_Plan',[]).append({'name':observed['name'],'revenue':rev,'ebitda':eb,'ending_cash':cash})

# Fleet: pretax, five end-year cash flows; disposal receipt only when old fleet sold.
for idx,(rate,fuel,miles,maintenance) in enumerate([(.08,4,70000,22000),(.10,5,70000,26000),(.08,4,45000,22000)]):
    old=[0];new=[-660000];lease=[70000]
    for year in range(1,6):
        inflation=1.03**(year-1);oldcost=6*(maintenance+miles/6*fuel+12*1800)*inflation;newcost=6*(9000+miles/7.2*fuel+4*1800)*inflation;leasecost=6*(33000+miles/7.2*fuel+4*1800)*inflation
        old.append(-oldcost+(42000 if year==5 else 0));new.append(-newcost+(252000 if year==5 else 0));lease.append(-leasecost+(50000 if year==5 else 0))
    pv=lambda cf:sum(x/(1+rate)**i for i,x in enumerate(cf))
    vals={'keepPV':-pv(old),'replacePV':-pv(new),'leasePV':-pv(lease),'replaceNPV':pv(new)-pv(old),'upfront':660000}
    for key,expected in vals.items():close('Fleet case '+str(idx+1)+' '+key,captured['Fleet_Investment'][idx][key],expected)
    costs=[vals['keepPV'],vals['replacePV'],vals['leasePV']];recommend=['Keep','Replace','Lease'][costs.index(min(costs))]
    check('Fleet case '+str(idx+1)+' ranking',captured['Fleet_Investment'][idx]['recommendation']==recommend)
    independent.setdefault('Fleet_Investment',[]).append({'name':captured['Fleet_Investment'][idx]['name'],**vals,'recommendation':recommend})
    for year in range(6):details.append({'model':'Fleet_Investment','case':idx+1,'period':year,'keep_cf':old[year],'replace_cf':new[year],'lease_cf':lease[year]})

# Cash: every invoice collected once or carried beyond week 13.
invoice_rows=[]
for i in range(26):
    week=i//2+1;invoice_rows.append({'invoice':'INV-'+str(1001+i),'base_week':week,'amount':44000+(i%4)*3000,'eligible':int(week in [4,5])})
with (ROOT/'cash_invoice_source.csv').open('w') as f:
    wr=csv.DictWriter(f,fieldnames=list(invoice_rows[0]));wr.writeheader();wr.writerows(invoice_rows)
for idx,(delay,acceleration,capexweek) in enumerate([(0,0,6),(2,0,6),(2,2,14)]):
    cash=180000;balances=[];future=0;receipts=[0]*13
    for inv in invoice_rows:
        wk=max(1,inv['base_week']+delay-inv['eligible']*acceleration)
        if wk<=13:receipts[wk-1]+=inv['amount']
        else:future+=inv['amount']
    for wk in range(1,14):
        cash+=receipts[wk-1]+20000-112000-(90000 if wk==capexweek else 0);balances.append(cash)
        details.append({'model':'Cash_Working_Capital','case':idx+1,'period':wk,'collections':receipts[wk-1],'ending_cash':cash})
    vals={'minCash':min(balances),'fundingGap':max(0,100000-min(balances)),'endingCash':cash,'futureReceipts':future,'deferredCapex':90000 if capexweek>13 else 0,'overdue':194000}
    for key,expected in vals.items():close('Cash case '+str(idx+1)+' '+key,captured['Cash_Working_Capital'][idx][key],expected)
    close('Cash case '+str(idx+1)+' invoice completeness',sum(receipts)+future,sum(i['amount'] for i in invoice_rows))
    independent.setdefault('Cash_Working_Capital',[]).append({'name':captured['Cash_Working_Capital'][idx]['name'],**vals})

(ROOT/'independent_results.json').write_text(json.dumps(independent,indent=2))
(ROOT/'independent_audit.json').write_text(json.dumps({'status':'passed','checks':checks,'count':len(checks)},indent=2))
keys=sorted({k for x in details for k in x})
with (ROOT/'reproduced_period_results.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(details)
manifest=[]
for name in captured:
    p=ROOT/(name+'.xlsx');manifest.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sheets':list(models[name])})
(ROOT/'new_model_manifest.json').write_text(json.dumps(manifest,indent=2));print('Independent audit passed:',len(checks),'checks across 3 models and 9 recalculated cases.')
