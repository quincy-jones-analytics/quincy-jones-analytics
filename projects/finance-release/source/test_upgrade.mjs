import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const root=process.env.QUINCY_FINANCE_DIR || process.cwd();
const checks=[];function test(ok,name){if(!ok)throw Error(name);checks.push(name);}
for(const name of ['Operating_Plan','Fleet_Investment','Cash_Working_Capital']){
 const w=await SpreadsheetFile.importXlsx(await FileBlob.load(root+'/'+name+'.xlsx'));const a=w.worksheets.getItem('Assumptions'),s=w.worksheets.getItem('Summary');const get=(sh,cell)=>w.worksheets.getItem(sh).getRange(cell).values[0][0];const set=(cell,x)=>{a.getRange(cell).values=[[x]];w.recalculate();};w.recalculate();
 const guardRows=name==='Operating_Plan'?Array.from({length:18},(_,i)=>41+i):name==='Fleet_Investment'?Array.from({length:14},(_,i)=>44+i):[35,36,37,38,39,40,42];
 for(const r of guardRows){const saved=get('Assumptions','G'+r);set('G'+r,null);test(typeof get('Assumptions','I'+r)!=='number',name+': blank driver G'+r+' exposes unavailable');set('G'+r,-1);test(typeof get('Assumptions','I'+r)!=='number',name+': negative driver G'+r+' rejected');set('G'+r,saved);}
 if(name==='Operating_Plan'){set('G43',.8);test(typeof get('Assumptions','I43')!=='number','Operating: collection fractions cannot exceed one');set('G43',.25);set('G49',0);test(typeof get('Assumptions','I49')!=='number','Operating: zero asset life rejected');set('G49',60);}
 if(name==='Cash_Working_Capital'){set('G38',200001);test(typeof get('Assumptions','I38')!=='number','Cash: opening debt cannot exceed commitment');set('G38',0);set('G40',2.5);test(typeof get('Assumptions','I40')!=='number','Cash: fractional week lag rejected');set('G40',2);}
 let base=get('Summary','D7');set('D5',2);test(get('Summary','D7')!==base,name+': case changes active build');set('D5',1);
 if(name==='Operating_Plan'){
  const src=JSON.stringify(w.worksheets.getItem('Source').getRange('C7:I24').values);let cash=get('Summary','D10');set('G43',.35);test(get('Summary','D10')!==cash,'Operating: collection rate changes cash');test(src===JSON.stringify(w.worksheets.getItem('Source').getRange('C7:I24').values),'Operating: history preserved');
  for(const c of ['D','E','F','G','H','I'])test(Math.abs(get('Statements',c+'55'))<.02,'Operating: BS reconciles after collection edit '+c);
  set('G50',0);test(get('Debt','D9')===0 && get('Debt','I11')===0,'Operating: zero debt has zero interest and repayments');set('G50',5000);test(get('Debt','D10')===5000 && get('Debt','E10')===0,'Operating: principal cannot exceed debt');
  set('D10',null);test(typeof get('Summary','D7')==='number','Operating: missing inactive case input does not block base');set('D5',2);test(typeof get('Summary','D7')!=='number','Operating: selected missing driver is unavailable');
 }else if(name==='Fleet_Investment'){
  const grid=a.getRange('H33:J35').values;
  for(let i=0;i<3;i++)for(let j=0;j<3;j++){set('D8',[.06,.08,.10][j]);set('D23',[18000,22000,26000][i]);test(Math.abs(get('Summary','F8')-grid[i][j])<.02,`Fleet: native data table equals active model ${i},${j}`);}
  set('D8',.08);set('D23',22000);set('G44',0);test(get('Summary','D8')>1447379,'Fleet: zero tax removes tax benefits');set('G50',0);test(get('Financing','D8')===0,'Fleet: zero financing fraction remains zero');set('G22',10000);test(get('Summary','D13')!=='Replace','Fleet: budget limit constrains selection');set('D18',65000);test(get('After Tax','E22')===0,'Fleet: mileage allowance boundary');set('D18',65001);test(Math.abs(get('After Tax','E22')-1.2)<1e-8,'Fleet: marginal mileage charge');
 }else{
  set('D5',2);set('G35',0);test(get('Summary','D13')>100000,'Cash: unavailable facility exposes residual gap');test(get('Summary','D8')===0,'Cash: no facility no draws');set('G35',200000);set('D5',3);test(get('Weekly','Q16')===90000 && get('Summary','D11')===0,'Cash: capex deferred to week 14 is paid');set('D19',27);set('D5',1);set('D18',27);test(get('Summary','D11')===90000,'Cash: capex beyond horizon is carried forward');set('G9',0);test(get('Summary','D14')<0,'Cash: zero opening cash remains genuine zero');
  const ids=w.worksheets.getItem('Invoices').getRange('C7:C32').values.flat().concat(w.worksheets.getItem('New Invoices').getRange('C7:C32').values.flat());test(new Set(ids).size===52,'Cash: distinct invoice populations');
 }
}
await fs.writeFile(root+'/recalculation_tests.json',JSON.stringify({passed:checks.length,failed:0,checks},null,2));console.log(checks.length+' input and native sensitivity checks passed');
