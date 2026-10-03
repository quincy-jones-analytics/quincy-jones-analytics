from pathlib import Path
import csv,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
P=Path(__file__).resolve().parents[1];import json;rows=json.loads((P/'independent_period_results.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#c6d0dd','text.color':'#17324d','axes.labelcolor':'#17324d','xtick.color':'#435870','ytick.color':'#435870','svg.fonttype':'none'})
for model in ['Operating_Plan','Fleet_Investment','Cash_Working_Capital']:
 for case in [1,2,3]:
  a=[x for x in rows if x['model']==model and int(x['case'])==case];fig,ax=plt.subplots(figsize=(10,3.5));x=[int(float(r['period'])) for r in a]
  if model=='Fleet_Investment':
   for col,label,color in [('keep_cf','Keep','#17324d'),('replace_cf','Replace','#087a7e'),('lease_cf','Lease','#b7651e')]:ax.plot(x,[float(r[col]) for r in a],marker='o',label=label,color=color)
   ax.set(xlabel='Year (0 = initial cash flow)',ylabel='Net cash flow · USD',title='After-tax unlevered cash flows')
  elif model=='Operating_Plan':
   ax.plot(x,[float(r['cash']) for r in a],marker='o',color='#087a7e',label='Ending cash');ax.axhline(250000,color='#b7651e',ls='--',label='$250k floor');ax.set_xticks(x,['Jul','Aug','Sep','Oct','Nov','Dec']);ax.set(ylabel='Cash · USD',title='Operating plan: July–December liquidity')
  else:
   ax.plot(x,[float(r['cash']) for r in a],marker='o',color='#087a7e',label='Ending cash');ax.axhline(100000,color='#b7651e',ls='--',label='$100k floor');ax.set(xlabel='Week (1 begins October 5, 2026)',ylabel='Cash · USD',title='26-week cash after hypothetical financing');ax.set_xticks(x[::3])
  ax.axhline(0,color='#96a7bd',linewidth=.7);ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:('${:,.0f}k'.format(v/1000))));ax.grid(axis='y',color='#e8edf4');ax.legend(frameon=False,ncol=3,loc='best');fig.tight_layout();fig.savefig(P/(model+'-case-'+str(case)+'.svg'));plt.close(fig)
print('Rendered nine financial scenario charts from independently reproduced period results')
