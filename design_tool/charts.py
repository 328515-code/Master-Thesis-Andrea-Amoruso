"""Interactive force curves with explicit CFD coverage and Mach screening."""
import plotly.graph_objects as go
from model import AREA_M2


def curve(model, mass_kg_s):
    lo, hi = model.mass_range
    critical = model.mach_mass_limit
    end = max(hi * 1.15, critical * 1.08, mass_kg_s * 1.1)
    fig = go.Figure()
    def add_curve(left, right, name, colour, dash):
        if right <= left:
            return
        xs = [left + (right-left)*i/100 for i in range(101)]
        ys = [model.force_k * (x/(model.rho*AREA_M2))**2 for x in xs]
        fig.add_trace(go.Scatter(x=[x*1000 for x in xs], y=ys, mode='lines', name=name,
            showlegend=name!='Extrapolation above CFD range',legendgroup='extrapolation' if 'Extrapolation' in name else name,
            line=dict(color=colour, dash=dash, width=2.5), hovertemplate='%{x:.3f} g/s<br>%{y:.3f} N<extra>'+name+'</extra>'))
    add_curve(0, lo, 'Extrapolation', '#b7791f', 'dash')
    add_curve(lo, min(hi, critical), 'Fit within CFD range', '#006b83', 'solid')
    add_curve(hi, critical, 'Extrapolation above CFD range', '#b7791f', 'dash')
    add_curve(critical, end, 'Projection: new CFD needed', '#9ca3af', 'dot')
    fig.add_vrect(x0=lo*1000, x1=hi*1000, fillcolor='#d8edf0', opacity=.35, line_width=0, layer='below')
    fig.add_vrect(x0=critical*1000, x1=end*1000, fillcolor='#fee2e2', opacity=.35, line_width=0, layer='below')
    ps=model.points
    fig.add_trace(go.Scatter(x=[p['velocity_m_s']*model.rho*AREA_M2*1000 for p in ps],
        y=[p['mean_axial_force_N'] for p in ps], mode='markers', name='CFD mean ± temporal SD',
        marker=dict(color='#0f172a',size=9), error_y=dict(type='data',array=[p['mean_axial_force_N']*p['force_CV_pct']/100 for p in ps],visible=True),
        hovertemplate='%{x:.3f} g/s<br>%{y:.3f} N<extra>CFD terminal mean; SD is not uncertainty</extra>'))
    r=model.evaluate(mass_kg_s)
    invalid=r['status']=='CFD_REQUIRED_MACH'
    title='Selected threshold: formal projection only' if invalid else 'Selected threshold'
    fig.add_trace(go.Scatter(x=[mass_kg_s*1000],y=[r['formal_force_projection_N']],mode='markers',name=title,
        marker=dict(color='#b91c1c' if invalid else '#e06a16',size=12,symbol='x' if invalid else 'diamond'),
        hovertemplate='%{x:.3f} g/s<br>%{y:.3f} N<extra>'+title+'</extra>'))
    fig.add_vline(x=mass_kg_s*1000,line=dict(color='#e06a16',dash='dot',width=1.5))
    fig.add_vline(x=critical*1000,line=dict(color='#b91c1c',dash='dash',width=2))
    fig.add_annotation(x=1,xref='paper',y=1.05,yref='paper',text=f'Estimated Ma = 0.3: {critical*1000:.2f} g/s',
        showarrow=False,xanchor='right',font=dict(color='#b91c1c',size=12))
    focus_end=min(end, max(hi*1.15, mass_kg_s*1.12, critical*1.08 if critical<hi*1.25 else 0))
    buttons=[]
    for label, right in [('Full screening range',end),('CFD / selected flow',focus_end)]:
        ymax=model.force_k*(right/(model.rho*AREA_M2))**2*1.15
        buttons.append(dict(label=label,method='relayout',args=[{'xaxis.range':[0,right*1000],'yaxis.range':[0,ymax]}]))
    fig.update_layout(template='plotly_white',height=430,margin=dict(l=45,r=15,t=90,b=100),
        xaxis=dict(title='Mass flow [g/s]',range=[0,end*1000]),yaxis=dict(title='Axial force Fₓ [N]',rangemode='tozero'),
        legend=dict(orientation='h',y=-.24,font=dict(size=10)),
        updatemenus=[dict(type='buttons',direction='right',x=0,xanchor='left',y=1.24,buttons=buttons)],
        font=dict(family='Arial',color='#16324f'),uirevision=f'{model.gas}-{model.obturator}-{mass_kg_s}')
    return fig
