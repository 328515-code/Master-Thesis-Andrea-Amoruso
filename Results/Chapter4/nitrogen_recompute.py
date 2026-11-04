"""Check the archived nitrogen diagnostics; no CFD files are modified."""
import json, math
from pathlib import Path
here=Path(__file__).resolve().parent
rows=json.loads((here/'nitrogen_mach_velocity_data.json').read_text())
a=json.loads((here/'nitrogen_sound_speed.json').read_text())['sound_speed_m_s']
ranges=json.loads((here/'nitrogen_colour_ranges.json').read_text())
assert len(rows)==12
for r in rows:
    assert r['processors']==52 and r['cell_count']>0
    assert math.isclose(r['channel_slice_peak_speed'],max(s['channel_peak'] for s in r['slices'].values()))
    assert r['channel_slice_peak_speed']<=r['max_cell_speed']
    for s in r['slices'].values():
        assert .035<=s['channel_peak_position'][0]<=.046
    print(r['case'],r['time'],f"channel Mach={r['channel_slice_peak_speed']/a:.4f}",f"domain Mach={r['max_cell_speed']/a:.4f}")
for field in ranges:
    actual=[min(s['ranges'][field][0] for r in rows for s in r['slices'].values()),max(s['ranges'][field][1] for r in rows for s in r['slices'].values())]
    assert actual==ranges[field]
print('All twelve nitrogen cases verified.')
