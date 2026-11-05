import csv
import io
import math
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from model import load_models, quadratic_coefficient, AREA_M2, export_results

@pytest.fixture
def models():
    return load_models()[0]

def test_known_parabola():
    points=[{'velocity_m_s':u,'f':2*u*u} for u in [5,10,15]]
    assert quadratic_coefficient(points,'f')==2

def test_audited_force_and_mass_units(models):
    m=models['H2','A']
    assert m.points[1]['mean_axial_force_N']==22.34357
    # Independent hand calculation of normal equation, using the audited means.
    expected=(25*5.616+100*22.34357+225*50.08882)/(625+10000+50625)
    r=m.evaluate(33.77*4.658925e-5*10)
    assert r['force_N']==pytest.approx(expected*100)
    assert r['inlet_velocity_m_s']==pytest.approx(10)
    assert r['mass_flow_kg_s']==pytest.approx(.0157331914725)
    assert r['status']=='WITHIN_SAMPLED_RANGE'

@pytest.mark.parametrize('gas',['H2','N2'])
@pytest.mark.parametrize('obt',list('ABCD'))
def test_mach_envelope_and_boundary(models,gas,obt):
    m=models[gas,obt]
    for p in m.mach_points:
        assert m.amplification*p['inlet_velocity']>=p['max_cell_speed']-1e-10
    r=m.evaluate(m.mach_mass_limit)
    assert r['mach_estimate']==pytest.approx(.3)
    assert r['force_N'] is None and r['pressure_loss_kPa'] is None
    assert r['status']=='CFD_REQUIRED_MACH'
    assert m.evaluate(m.mach_mass_limit*(1-1e-6))['force_N'] is not None

def test_nitrogen_a_envelope_is_not_measured_transition(models):
    m=models['N2','A']
    observed=m.mach_points[-1]['max_cell_speed']/m.sound_speed
    assert observed<.3
    assert m.evaluate(m.mass_range[1])['status']=='CFD_REQUIRED_MACH'

def test_coverage_and_zero(models):
    m=models['H2','B']
    assert m.evaluate(0)['force_N']==0
    assert m.evaluate(0)['status']=='EXTRAPOLATION'
    for endpoint in m.mass_range:
        assert m.evaluate(endpoint)['status']=='WITHIN_SAMPLED_RANGE'
    assert m.evaluate(m.mass_range[0]*.99)['status']=='EXTRAPOLATION'
    assert m.evaluate(m.mass_range[1]*1.01)['status']=='EXTRAPOLATION'

@pytest.mark.parametrize('value',[-1,float('nan'),float('inf'),1001])
def test_invalid_inputs(models,value):
    with pytest.raises(ValueError): models['H2','A'].evaluate(value)

def test_short_run_and_all_geometries(models):
    assert len(models)==8
    a=models['N2','A']
    assert a.points[0]['averaging_window']=='1072-1372'
    assert a.mach_points[0]['iteration']=='1000'
    assert models['N2','D'].mach_points[0]['max_cell_speed']==pytest.approx(20.921922376327263)

def test_export_withholds_mach_exceedance(models):
    _,p=load_models()
    records=list(csv.DictReader(io.StringIO(export_results(models,'N2',models['N2','A'].mass_range[1],p))))
    assert len(records)==4
    assert records[0]['force_N']=='' and records[0]['status']=='CFD_REQUIRED_MACH'
    assert float(records[0]['formal_force_projection_N'])>0
    assert records[0]['source_commit']==p['source_commit']

def test_data_tampering_fails(tmp_path):
    import shutil
    from model import DATA
    for p in DATA.iterdir(): shutil.copyfile(p,tmp_path/p.name)
    with (tmp_path/'final_high_pressure_responses.csv').open('a') as f: f.write('\n')
    with pytest.raises(ValueError,match='integrity'): load_models(tmp_path)
