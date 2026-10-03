"""Independent math and structural review. Reads XLSX; does not author workbooks."""
import csv,json,math,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,ok):
    assert bool(ok),name
    checks.append(name)
def close(name,a,b,tol=.02):check(name,abs(float(a)-float(b))<=tol)
def read_xlsx(path):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
        rel={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for sh in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns):
            target=rel[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
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
cap=json.loads((ROOT/'scenario_captures.json').read_text()); models={n:read_xlsx(ROOT/(n+'.xlsx')) for n in cap}
def val(n,s,c):return models[n][s][c]['value']
for name,ss in models.items():
    for sn,cs in ss.items():
        check(name+' '+sn+' no cached errors',not any(c['type']=='e' for c in cs.values()))
        check(name+' '+sn+' formula caches present',not any(c['formula'] and c['value'] is None for c in cs.values()))
        if sn!='Audit':check(name+' '+sn+' terminal audit not used as input',not any(c['formula'] and 'Audit' in c['formula'] for c in cs.values()))
    for cell,c in ss['Audit'].items():
        if cell.startswith('D') and c['formula']:close(name+' '+cell+' terminal reconciliation',c['value'],0)
raw=[{c:val('Operating_Plan','Source',c+str(r)) for c in 'CDEFGHI'} for r in range(7,25)]
detail=[]
for idx,(ug,pg,cg,og) in enumerate([(.012,.018,.025,.020),(-.012,0,.035,.025),(.027,.025,.020,.018)]):
    revs=[];vcs=[];ebs=[]
    for k,season in enumerate([1.01,1.04,1.01,1.08,1.13,1.17],1):
        rev=vc=fixed=opex=0
        for j,x in enumerate(raw[-3:]):
            units=math.floor(x['E']*(1+ug)**k*season+.5)
            rev+=units*x['F']*(1+pg)**k;vc+=units*x['G']*(1+cg)**k
            fixed+=[89000,76000,42000][j]*(1+.001*(6+k))*(1+cg*.35)**k
            opex+=x['I']/(1+.002*6)*(1+.002*(6+k))*(1+og)**k
        revs.append(rev);vcs.append(vc);ebs.append(rev-vc-fixed-opex)
    cash=500000;ar=1020000;ap=300000;debt=600000;nol=0;gross=1200000;ad=480000;re=840000;bal=[]
    for k in range(6):
        receipts=revs[k]*.25+(revs[k-1]*.65 if k>0 else 0)+(revs[k-2]*.1 if k>1 else 0)+([550000,470000,0,0,0,0][k])
        supplier=vcs[k]*.5+(vcs[k-1]*.5 if k else 300000)
        new_ar=ar+revs[k]-receipts;new_ap=ap+vcs[k]-supplier
        dep=20000+k*25000/60;interest=debt*.08/12;principal=min(debt,10000)
        pretax=ebs[k]-dep-interest;used=min(nol,max(0,pretax));tax=max(0,pretax-used)*.25;nol=nol-used+max(0,-pretax);ni=pretax-tax
        cfo=ni+dep-(new_ar-ar)+(new_ap-ap);cash+=cfo-25000-principal;debt-=principal;gross+=25000;ad+=dep;re+=ni;ar,ap=new_ar,new_ap;bal.append(cash)
        close(f'Operating case {idx+1} BS month {k+7}',cash+ar+gross-ad,ap+debt+500000+re)
        detail.append(dict(model='Operating_Plan',case=idx+1,period=k+7,revenue=revs[k],ebitda=ebs[k],cash=cash,ar=ar,ap=ap,debt=debt,net_income=ni))
        if idx==0:
            c=chr(68+k)
            for r,e in [(14,dep),(16,interest),(21,tax),(23,ni),(35,cash),(39,ar),(42,gross-ad),(46,debt),(52,re),(55,0)]:close(f'Operating base {c}{r}',val('Operating_Plan','Statements',c+str(r)),e)
    h1rev=sum(x['E']*x['F'] for x in raw);h1eb=sum(x['E']*(x['F']-x['G'])-x['H']-x['I'] for x in raw)
    expected=dict(revenue=h1rev+sum(revs),ebitda=h1eb+sum(ebs),endingCash=cash,minCash=min(bal),endingDebt=debt,netIncomeDecember=ni)
    for key,e in expected.items():close(f'Operating case {idx+1} {key}',cap['Operating_Plan'][idx][key],e)
for idx,(rate,fuel,miles,maint) in enumerate([(.08,4,70000,22000),(.10,5,70000,26000),(.08,4,45000,22000)]):
    old=[0];new=[-685500];lease=[44500]
    for y in range(1,6):
        inf=1.03**(y-1);oc=6*(maint+miles/6*fuel+12*1800)*inf;nc=6*(9000+miles/7.2*fuel+4*1800)*inf;lc=6*(33000+miles/7.2*fuel+4*1800)*inf+max(0,miles-65000)*.2*6
        old.append(-oc*.75+18000*.25+(42000*.75 if y==5 else 0));new.append(-nc*.75+156000*.25+(252000*.75 if y==5 else 0));lease.append(-lc*.75+(50000 if y==5 else 0))
    pv=lambda cf:sum(x/(1+rate)**i for i,x in enumerate(cf))
    expected=dict(keepPV=-pv(old),replacePV=-pv(new),leasePV=-pv(lease),replaceNPV=pv(new)-pv(old),upfront=685500)
    for key,e in expected.items():close(f'Fleet case {idx+1} {key}',cap['Fleet_Investment'][idx][key],e)
    check(f'Fleet case {idx+1} lowest cost selection',cap['Fleet_Investment'][idx]['recommendation']==['Keep','Replace','Lease'][[-pv(old),-pv(new),-pv(lease)].index(min(-pv(old),-pv(new),-pv(lease)))])
    for y in range(6):detail.append(dict(model='Fleet_Investment',case=idx+1,period=y,keep_cf=old[y],replace_cf=new[y],lease_cf=lease[y]))
close('Fleet debt extinguished',val('Fleet_Investment','Financing','I10'),0)
close('Fleet lease obligation extinguished',val('Fleet_Investment','Financing','I20'),0)
for idx,(delay,accel,capweek) in enumerate([(0,0,6),(2,0,6),(2,2,14)]):
    opening=[0]*26;future=0
    for i in range(26):
        week=i//2+1;active=max(1,week+delay-(accel if week in [4,5] else 0));amount=44000+(i%4)*3000
        if active<=26:opening[active-1]+=amount
        else:future+=amount
    fresh=[0]*26
    for issue in range(1,27):
        collect=issue+2+delay
        if collect<=26:fresh[collect-1]+=92000
        else:future+=92000
    cash=unfunded=180000;debt=0;funded_bal=[];unfunded_bal=[];debts=[];costs=0;gaps=[]
    for wk in range(1,27):
        op=opening[wk-1]+fresh[wk-1]+20000-112000-(90000 if wk==capweek else 0)
        interest=debt*.09/52;fee=max(0,200000-debt)*.005/52;pre=cash+op-interest-fee
        draw=min(max(0,200000-debt),max(0,100000-pre));repay=min(debt,max(0,pre-100000));debt+=draw-repay;cash=pre+draw-repay;costs+=interest+fee;unfunded+=op
        funded_bal.append(cash);unfunded_bal.append(unfunded);debts.append(debt);gaps.append(max(0,100000-cash))
        close(f'Cash case {idx+1} commitment week {wk}',min(200000,debt),debt)
        detail.append(dict(model='Cash_Working_Capital',case=idx+1,period=wk,opening_receipts=opening[wk-1],new_receipts=fresh[wk-1],cash=cash,debt=debt,interest=interest,fee=fee))
    expected=dict(minCash=min(funded_bal),fundingGap=max(debts),endingCash=cash,futureReceipts=future,deferredCapex=0,residualGap=max(gaps),unfundedMinimum=min(unfunded_bal),endingDebt=debt,fundingCosts=costs)
    for key,e in expected.items():close(f'Cash case {idx+1} {key}',cap['Cash_Working_Capital'][idx][key],e)
    close(f'Cash case {idx+1} invoice population',sum(opening)+sum(fresh)+future,sum(44000+(i%4)*3000 for i in range(26))+26*92000)
    close(f'Cash case {idx+1} all cash reconciliation',cash+costs-debt,unfunded)
(ROOT/'independent_period_results.json').write_text(json.dumps(detail,indent=2))
(ROOT/'independent_audit.json').write_text(json.dumps(dict(passed=len(checks),failed=0,checks=checks),indent=2))
print(f'{len(checks)} independent checks passed')
