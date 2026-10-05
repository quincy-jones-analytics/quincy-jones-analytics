// Executes the shipped dashboard JavaScript with a minimal DOM fixture.
// This checks arithmetic and initialization, NOT native rendering or browser layout.
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(root+'/dashboard.html','utf8');
const d=JSON.parse(fs.readFileSync(root+'/outputs/dashboard_data.json','utf8'));
const ids={};
for(const m of html.matchAll(/<input[^>]*id="([^"]+)"[^>]*value="([^"]*)"/g))ids[m[1]]={value:m[2]};
for(const m of html.matchAll(/id="([^"]+)"/g))ids[m[1]]??={value:'',innerHTML:'',textContent:''};
ids['model-data'].textContent=JSON.stringify(d);ids['f-lane'].value='All lanes';
for(const [i,v] of d.vendors.entries())for(const k of Object.keys(d.assumptions.vendor_weights))ids['v-'+i+'-'+k]={value:String(v[k])};
for(const [k,v] of Object.entries(d.assumptions.vendor_weights))ids['w-'+k]={value:String(v*100)};
for(const [id,x] of Object.entries(ids)){let v=x.value??'';Object.defineProperty(x,'value',{get:()=>String(v),set:n=>{v=String(n)}});x.closest=()=>({firstChild:{textContent:id}});x.addEventListener=()=>{};}
const context={document:{getElementById:id=>ids[id],querySelectorAll:()=>[]},Intl,console,Blob,URL,alert:()=>{}};
vm.createContext(context);
const script=html.match(/<\/script><script>([\s\S]*?)<\/script>/)[1];
vm.runInContext(script,context);
const evaluate=s=>vm.runInContext(s,context);let checks=0;
function close(x,y,msg){assert.ok(Math.abs(x-y)<1e-6,msg);checks++;}
const base=d.base_lanes.reduce((s,r)=>s+r.contribution_usd,0);
close(evaluate('exportsNow.fuel[0].contribution_usd'),base,'fuel base');
ids['f-shock'].value='10';evaluate('renderFuel()');close(evaluate('exportsNow.fuel[0].contribution_usd'),base-d.base_lanes.reduce((s,r)=>s+r.base_fuel_usd,0)*.1,'fuel shock');
ids['f-lane'].value='Detroit-Cleveland';evaluate('renderFuel()');const c=d.base_lanes.find(x=>x.lane==='Detroit-Cleveland');close(evaluate('exportsNow.fuel[0].contribution_usd'),c.contribution_usd-c.base_fuel_usd*.1,'lane');
ids['f-target'].value='100';evaluate('renderFuel()');assert.equal(evaluate('exportsNow.fuel'),null);checks++;
ids['f-target'].value='18';ids['f-shock'].value='0';ids['f-lane'].value='All lanes';evaluate('renderFuel()');
close(evaluate('exportsNow.ocean[1].margin_erosion_usd'),1000+120000*.2*10/365,'ocean cost');
ids['o-extra'].value='0';evaluate('renderOcean()');close(evaluate('exportsNow.ocean[1].margin_erosion_usd'),1000,'ocean delay isolation');
ids['o-extra'].value='-1';evaluate('renderOcean()');assert.equal(evaluate('exportsNow.ocean'),null);checks++;
ids['o-extra'].value='10';evaluate('renderOcean()');
close(evaluate('exportsNow.air[1].trip_cost_usd'),67400,'air default');
ids['a-saving'].value='0';evaluate('renderAir()');close(evaluate('exportsNow.air[1].trip_cost_usd'),75500,'air reversal');
ids['a-distance'].value='8800';evaluate('renderAir()');assert.equal(evaluate('exportsNow.air[1].cost_usd_per_tonne_mile'),null);checks++;
ids['a-distance'].value='6000';ids['a-demand'].value='120';evaluate('renderAir()');assert.equal(evaluate('exportsNow.air[0].cost_usd_per_tonne_mile'),null);checks++;
ids['a-demand'].value='80';ids['a-saving'].value='20';evaluate('renderAir()');
assert.equal(evaluate('exportsNow.vendor[3].risk_score'),null);checks++;
close(evaluate('exportsNow.vendor[3].risk_upper_bound'),73.5,'missing bound');
ids['v-3-cybersecurity'].value='0';evaluate('renderVendor()');close(evaluate('exportsNow.vendor[3].risk_score'),48.5,'zero known');
ids['v-3-cybersecurity'].value='';ids['w-ownership'].value='40';evaluate('renderVendor()');assert.equal(evaluate('exportsNow.vendor'),null);checks++;
ids['w-ownership'].value='15';evaluate('renderVendor()');
for(const group of ['fuel','ocean','air','vendor']){assert.ok(evaluate('exportsNow.'+group).length>0);checks++;}
for(const prefix of ['f','o','a','v']){assert.equal(ids[prefix+'-error'].textContent,'');checks++;}
const result={checks,passed:true,execution:'Node VM with minimal DOM fixture; native rendering not tested'};
fs.writeFileSync(root+'/outputs/dashboard_logic_validation.json',JSON.stringify(result,null,2));console.log(result);
