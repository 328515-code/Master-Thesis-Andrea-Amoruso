"""Run with: python -m streamlit run streamlit_app.py"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import streamlit as st
import pandas as pd
from model import load_models, GEOMETRIES, AREA_M2, export_results
from charts import curve

st.set_page_config(page_title='EFV | Threshold design study',page_icon='◉',layout='wide')
st.markdown('**EFV DESIGN STUDY** · CFD-based engineering comparison')
st.title('From threshold flow to obturator load')
st.write('Compare four fixed-position obturators and identify the fluid load to carry into a spring force balance.')
try:
    models, provenance=load_models()
except (ValueError, AssertionError, OSError) as exc:
    st.error(f'The audited dataset could not be loaded: {exc}'); st.stop()

with st.sidebar:
    st.header('Design inputs')
    gas=st.selectbox('Working gas', ['H2','N2'],format_func=lambda x:'Hydrogen (H₂)' if x=='H2' else 'Nitrogen (N₂)',key='gas')
    flow=st.number_input('Threshold mass flow [g/s]',min_value=0.0,max_value=1000000.0,value=15.0,step=1.0,format='%.3f',key='flow_g_s')
    st.caption(f'Equivalent to {flow/1000:.6g} kg/s and {flow*3.6:.4g} kg/h.')
    st.divider()
    st.markdown('**Reference operating state**')
    st.write('437 bar absolute · 233 K')
    st.caption('The dataset applies to this state and the simulated fixed obturator position. Changing gas keeps your entered mass flow.')
    st.caption('The app runs from compact audited data; OpenFOAM and ParaView are not needed.')

m=flow/1000
base=models[gas,'A']
lo,hi=base.mass_range
c1,c2,c3=st.columns(3)
c1.metric('Threshold mass flow',f'{flow:,.3f} g/s')
c2.metric('Equivalent inlet velocity',f'{m/(base.rho*AREA_M2):.3f} m/s')
c3.metric('CFD coverage [g/s]',f'{lo*1000:.2f}–{hi*1000:.2f}')
st.caption('Coverage corresponds to inlet velocities 5–15 m/s. Mass flow uses the discretized inlet area, 4.658925 × 10⁻⁵ m².')
results=[models[gas,o].evaluate(m) for o in GEOMETRIES]
blocked=[r['obturator'] for r in results if r['status']=='CFD_REQUIRED_MACH']
if blocked:
    st.error('Further CFD required for obturator(s) '+', '.join(blocked)+': the estimated local Mach number reaches or exceeds 0.3. Force and pressure design outputs are withheld for these geometries.')
elif any(r['status']=='EXTRAPOLATION' for r in results):
    st.warning('This flow is outside the sampled CFD interval. Values are unvalidated extrapolations; obtain additional CFD before using them to set a spring load.')
else:
    st.info('The selected flow is within the sampled CFD interval. The fitted loads support preliminary comparison at the reference state and fixed obturator position.')
st.caption('Mach boundaries are projections from the largest observed full-volume velocity amplification for each geometry. They are screening estimates, not measured transition points or guarantees of incompressibility.')

st.subheader('Load comparison at your threshold')
labels={'WITHIN_SAMPLED_RANGE':'Within CFD range','EXTRAPOLATION':'Extrapolation','CFD_REQUIRED_MACH':'Mach ≥ 0.3: new CFD'}
table=[]
for r in results:
    table.append({'Obturator':r['obturator'],'Force Fₓ [N]':'—' if r['force_N'] is None else f'{r["force_N"]:.3f}',
        'Δp [kPa]':'—' if r['pressure_loss_kPa'] is None else f'{r["pressure_loss_kPa"]:.3f}',
        'Est. Mach':r['mach_estimate'],'Ma 0.3 [g/s]':r['mach_mass_limit_kg_s']*1000,'Assessment':labels[r['status']]})
st.dataframe(pd.DataFrame(table),hide_index=True,width='stretch',column_config={
    'Est. Mach':st.column_config.NumberColumn(format='%.4f'),
    'Ma 0.3 [g/s]':st.column_config.NumberColumn(format='%.2f')})
st.caption('Reported force is the positive CFD x-component, including pressure and viscous contributions. Pressure loss is a companion design trade-off, fitted independently with the same quadratic method.')

st.subheader('Force curves and Mach screening boundaries')
st.write('Blue shading marks the sampled flow interval. Solid curves show the fit within it; dashed curves are extrapolations. Red shading starts at the estimated Mach boundary. Use “CFD / selected flow” to inspect the original data closely.')
for pair in [('A','B'),('C','D')]:
    for col,obt in zip(st.columns(2),pair):
        with col:
            model=models[gas,obt];n,d=GEOMETRIES[obt]
            st.markdown(f'#### Obturator {obt} · {n} holes × {d:g} mm')
            st.plotly_chart(curve(model,m),key=f'curve_{obt}',width='stretch',config={'displaylogo':False})
            st.caption(f'Maximum fit mismatch at a CFD point: {model.force_fit_max_error_pct:.2f}%. Highest terminal force CV: {max(p["force_CV_pct"] for p in model.points):.2f}%. Error bars show temporal standard deviation, not confidence intervals.')

with st.expander('How to use the load for spring design',expanded=True):
    st.write('At the reference position, project the CFD force onto the verified closing direction. At incipient motion, this closing component balances spring preload plus friction and other opposing loads. A specified displacement and preload are needed to calculate spring stiffness; these simulations do not provide a force-versus-stroke law.')
    st.latex(r'F_{\mathrm{fluid,close}}(x_0,\dot m_{\mathrm{thr}})\approx F_0+kx_0+F_{\mathrm{friction}}+F_{\mathrm{other}}')
    st.caption('No automatic geometry ranking or spring stiffness is calculated. A large force may come with a large pressure penalty. Nitrogen A is close to the Mach screen at the highest simulated flow; low Mach alone does not establish constant density.')
with st.expander('Fitting method, data quality and provenance'):
    st.latex(r'\widehat F_x=k_F U_{\mathrm{in}}^2,\quad k_F=\frac{\sum_i U_i^2\overline F_{x,i}}{\sum_i U_i^4},\quad U_{\mathrm{in}}=\frac{\dot m}{\rho A_{\mathrm{in,mesh}}}')
    st.latex(r'\alpha=\max_i\frac{U_{\max,3D,i}}{U_{\mathrm{in},i}},\quad \widehat{Ma}=\frac{\alpha\dot m}{a_{\mathrm{ref}}\rho A_{\mathrm{in,mesh}}},\quad \dot m_{0.3}=\frac{0.3a_{\mathrm{ref}}\rho A_{\mathrm{in,mesh}}}{\alpha}')
    st.write('A separate equal-weight least-squares parabola through zero is fitted to the three force means of each gas/geometry. It smooths the data; it is not an exact interpolant. Temporal CV is shown as a diagnostic and is not used as a statistical weighting or prediction interval.')
    st.write(f'Reference density: {base.rho:g} kg/m³; sound speed: {base.sound_speed:.2f} m/s. The sound speeds are archived real-gas reference values, not local thermodynamic solutions.')
    st.write('Most integral means use iterations 2700–3000. Nitrogen A at 5 m/s uses 1072–1372; its latest complete velocity field is iteration 1000. The other velocity fields are iteration 3000. Full-volume maxima are used because central slices miss off-plane peaks.')
    st.caption('Source revision: '+provenance['source_commit'])
    st.dataframe(pd.DataFrame([p for o in GEOMETRIES for p in models[gas,o].points]),hide_index=True)
st.download_button('Download this comparison (CSV)',export_results(models,gas,m,provenance),file_name=f'EFV_{gas}_{flow:g}g_s.csv',mime='text/csv')
