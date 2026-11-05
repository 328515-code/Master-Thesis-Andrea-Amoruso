"""Regenerate Chapter 5 illustrations and numeric audit from the application model."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from model import load_models, AREA_M2

models,provenance=load_models()
out=Path(__file__).resolve().parent.parent/'Results'/'Chapter5'
out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':13,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#16324f','text.color':'#16324f','figure.facecolor':'white'})
fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained')
for ax,obt in zip(axes.flat,'ABCD'):
    m=models['H2',obt];lo,hi=m.mass_range;xs=np.linspace(lo,hi,180)
    ax.plot(xs*1000,m.force_k*(xs/(m.rho*AREA_M2))**2,color='#006b83',label='Quadratic fit')
    ps=m.points
    ax.errorbar([p['velocity_m_s']*m.rho*AREA_M2*1000 for p in ps],[p['mean_axial_force_N'] for p in ps],yerr=[p['mean_axial_force_N']*p['force_CV_pct']/100 for p in ps],fmt='o',color='#172b4d',capsize=3,label='CFD mean ± temporal SD')
    r=m.evaluate(.015);ax.scatter([15],[r['force_N']],color='#e06a16',marker='D',s=45,zorder=4,label='Selected: 15 g/s')
    ax.axvline(15,color='#e06a16',ls=':',lw=1)
    ax.set(title=f"Obturator {obt} | selected force {r['force_N']:.3f} N",xlabel='Mass flow [g/s]',ylabel='Axial force [N]')
    ax.grid(alpha=.18);ax.legend(fontsize=10,loc='upper left')
fig.savefig(out/'hydrogen_design_example.png',dpi=220);plt.close(fig)
m=models['N2','A'];lo,hi=m.mass_range;crit=m.mach_mass_limit;end=.43
fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
for left,right,color,style,label in [(0,lo,'#b7791f','--','Extrapolation'),(lo,min(hi,crit),'#006b83','-','Fit within sampled interval'),(crit,end,'#777777',':','Formal projection; new CFD required')]:
    xs=np.linspace(left,right,150);ax.plot(xs*1000,m.force_k*(xs/(m.rho*AREA_M2))**2,color=color,ls=style,label=label)
ax.axvspan(lo*1000,hi*1000,color='#d8edf0',alpha=.5)
ax.axvspan(crit*1000,end*1000,color='#fee2e2',alpha=.5)
ax.axvline(crit*1000,color='#b91c1c',ls='--',label=f'Estimated Ma = 0.3: {crit*1000:.2f} g/s')
ax.scatter([p['velocity_m_s']*m.rho*AREA_M2*1000 for p in m.points],[p['mean_axial_force_N'] for p in m.points],color='#172b4d',label='CFD means',zorder=4)
ax.scatter([400],[m.evaluate(.4)['formal_force_projection_N']],color='#b91c1c',marker='x',s=75,label='Selected 400 g/s: formal projection only',zorder=5)
ax.set(xlabel='Mass flow [g/s]',ylabel='Axial force [N]',xlim=(0,end*1000),ylim=(0,None))
ax.grid(alpha=.18);ax.legend(loc='upper left',fontsize=11)
fig.savefig(out/'nitrogen_mach_screen_example.png',dpi=220);plt.close(fig)
summary=[]
for (gas,obt),m in models.items():
    summary.append(dict(gas=gas,obturator=obt,force_k_N_s2_m2=m.force_k,
        pressure_k_kPa_s2_m2=m.pressure_k,max_fit_error_pct=m.force_fit_max_error_pct,
        amplification=m.amplification,mach_limit_g_s=m.mach_mass_limit*1000,
        min_mass_g_s=m.mass_range[0]*1000,max_mass_g_s=m.mass_range[1]*1000,
        max_observed_mach=max(p['max_cell_speed'] for p in m.mach_points)/m.sound_speed))
(out/'model_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
