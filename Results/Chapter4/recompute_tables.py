"""Recompute Chapter 4 table values without CFD volumes or third-party packages."""
import csv,json,math
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parent.parent
area=math.pi*(.0078/2)**2
saved=json.loads((here/'coefficient_data.json').read_text())
with (root/'analysis/final_high_pressure_responses.csv').open() as stream:
    for row in csv.DictReader(stream):
        q=.5*float(row['rho_kg_m3'])*float(row['velocity_m_s'])**2
        cp=float(row['mean_pressure_drop_kPa'])*1000/q
        cf=float(row['mean_axial_force_N'])/(q*area)
        archived=next(x for x in saved if all(x[k]==row[k] for k in ['gas','velocity_m_s','obturator']))
        assert math.isclose(cp,archived['pressure_coefficient'],rel_tol=1e-12)
        assert math.isclose(cf,archived['force_coefficient'],rel_tol=1e-12)
        print(row['gas'],row['velocity_m_s'],row['obturator'],f'P_loss={cp:.2f}',f'C_Fx={cf:.2f}')
a=json.loads((here/'sound_speed.json').read_text())['sound_speed_m_s']
for row in json.loads((here/'mach_velocity_data.json').read_text()):
    print(row['case'],f'M_channel_slice={row["channel_slice_peak_speed"]/a:.4f}',f'M_max_3D={row["max_cell_speed"]/a:.4f}')
