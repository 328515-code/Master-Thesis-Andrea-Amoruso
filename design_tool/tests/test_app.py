from pathlib import Path
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'streamlit_app.py'

def test_default_and_gas_change():
    at=AppTest.from_file(str(APP),default_timeout=30).run()
    assert not at.exception
    assert len(at.get('plotly_chart'))==4
    assert at.dataframe[0].value.shape[0]==4
    at.selectbox(key='gas').select('N2').run()
    assert not at.exception
    assert at.number_input(key='flow_g_s').value==15
    assert at.warning
    at.number_input(key='flow_g_s').set_value(200.0).run()
    assert not at.exception and not at.error

def test_mach_gate_and_zero():
    at=AppTest.from_file(str(APP),default_timeout=30).run()
    at.selectbox(key='gas').select('N2').run()
    at.number_input(key='flow_g_s').set_value(400.0).run()
    assert not at.exception and at.error
    assert at.dataframe[0].value.iloc[0]['Assessment'].startswith('Mach')
    at.number_input(key='flow_g_s').set_value(0.0).run()
    assert not at.exception and at.warning
    assert (at.dataframe[0].value['Force Fₓ [N]']=='0.000').all()
