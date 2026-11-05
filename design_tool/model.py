"""Audited fixed-position CFD response model; all calculations use SI units."""
from dataclasses import dataclass
from pathlib import Path
import csv
import hashlib
import json
import math
import re

DATA = Path(__file__).resolve().parent / 'data'
AREA_M2 = 4.658925e-5  # discretized inlet patch used for actual flow reporting
MACH_LIMIT = 0.3
GEOMETRIES = {'A': (3, 1.5), 'B': (3, 3.0), 'C': (6, 1.5), 'D': (6, 3.0)}


@dataclass(frozen=True)
class Response:
    gas: str
    obturator: str
    rho: float
    nu: float
    sound_speed: float
    points: tuple
    mach_points: tuple
    force_k: float
    pressure_k: float
    amplification: float

    @property
    def mass_range(self):
        return tuple(self.rho * AREA_M2 * v for v in (5, 15))

    @property
    def mach_mass_limit(self):
        return MACH_LIMIT * self.sound_speed * self.rho * AREA_M2 / self.amplification

    @property
    def force_fit_max_error_pct(self):
        return max(abs(self.force_k * r['velocity_m_s'] ** 2 / r['mean_axial_force_N'] - 1) * 100 for r in self.points)

    def evaluate(self, mass_kg_s):
        if not math.isfinite(mass_kg_s) or not 0 <= mass_kg_s <= 1000:
            raise ValueError('Mass flow must be finite and between 0 and 1000 kg/s (display limit).')
        u = mass_kg_s / (self.rho * AREA_M2)
        mach = self.amplification * u / self.sound_speed
        lo, hi = self.mass_range
        at_limit = mass_kg_s >= self.mach_mass_limit or math.isclose(mass_kg_s, self.mach_mass_limit, rel_tol=1e-12)
        inside = (lo <= mass_kg_s <= hi or math.isclose(mass_kg_s, lo, rel_tol=1e-12) or math.isclose(mass_kg_s, hi, rel_tol=1e-12))
        status = ('CFD_REQUIRED_MACH' if at_limit else 'WITHIN_SAMPLED_RANGE' if inside else 'EXTRAPOLATION')
        projection = self.force_k * u * u
        return dict(gas=self.gas, obturator=self.obturator, mass_flow_kg_s=mass_kg_s,
                    inlet_velocity_m_s=u, force_N=None if at_limit else projection,
                    formal_force_projection_N=projection,
                    pressure_loss_kPa=None if at_limit else self.pressure_k * u * u,
                    mach_estimate=mach, mach_mass_limit_kg_s=self.mach_mass_limit,
                    mass_min_kg_s=lo, mass_max_kg_s=hi, status=status,
                    max_force_fit_error_pct=self.force_fit_max_error_pct,
                    max_force_CV_pct=max(p['force_CV_pct'] for p in self.points))


def quadratic_coefficient(points, key):
    # Least squares F=k U^2; equal weights on the three terminal means.
    return sum(p['velocity_m_s'] ** 2 * p[key] for p in points) / sum(p['velocity_m_s'] ** 4 for p in points)


def load_models(data_dir=DATA):
    data_dir = Path(data_dir)
    manifest = json.loads((data_dir / 'provenance.json').read_text())
    for name, expected in manifest['sha256'].items():
        if hashlib.sha256((data_dir / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Data integrity check failed: {name}. Rebuild the audited data bundle.')
    with (data_dir / 'final_high_pressure_responses.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 24, 'Expected 24 audited response records'
    numeric = ['velocity_m_s', 'rho_kg_m3', 'nu_m2_s', 'mean_pressure_drop_kPa', 'pressure_CV_pct', 'mean_axial_force_N', 'force_CV_pct']
    for r in rows:
        for k in numeric:
            r[k] = float(r[k])
            if not math.isfinite(r[k]) or r[k] <= 0:
                raise ValueError(f'Invalid {k} in response data')
    models = {}
    for gas, vel_file, sound_file in [('H2', 'mach_velocity_data.json', 'sound_speed.json'), ('N2', 'nitrogen_mach_velocity_data.json', 'nitrogen_sound_speed.json')]:
        raw = json.loads((data_dir / vel_file).read_text())
        if len(raw) != 12:
            raise ValueError('Expected twelve full-volume velocity records per gas')
        sound = json.loads((data_dir / sound_file).read_text())['sound_speed_m_s']
        for obt in GEOMETRIES:
            points = sorted([r for r in rows if r['gas'] == gas and r['obturator'] == obt], key=lambda r:r['velocity_m_s'])
            if [p['velocity_m_s'] for p in points] != [5, 10, 15]:
                raise ValueError('Missing or duplicated response point')
            if len({(p['rho_kg_m3'], p['nu_m2_s']) for p in points}) != 1:
                raise ValueError('Mixed fluid-property states')
            peaks = []
            for r in raw:
                if r['case'].endswith('_' + obt):
                    u = float(re.search(r'Flux(\d+)', r['case'])[1])
                    peak = float(r['max_cell_speed'])
                    if not math.isfinite(peak) or peak <= 0:
                        raise ValueError('Invalid volume velocity maximum')
                    peaks.append(dict(inlet_velocity=u, max_cell_speed=peak, iteration=str(r.get('iteration', r.get('time')))))
            peaks.sort(key=lambda r:r['inlet_velocity'])
            if [p['inlet_velocity'] for p in peaks] != [5, 10, 15]:
                raise ValueError('Missing or duplicated Mach point')
            models[gas, obt] = Response(gas, obt, points[0]['rho_kg_m3'], points[0]['nu_m2_s'], sound,
                tuple(points), tuple(peaks), quadratic_coefficient(points, 'mean_axial_force_N'),
                quadratic_coefficient(points, 'mean_pressure_drop_kPa'),
                max(p['max_cell_speed'] / p['inlet_velocity'] for p in peaks))
    return models, manifest


def export_results(models, gas, mass_kg_s, provenance):
    import io
    output = io.StringIO(newline='')
    records = []
    for obt in GEOMETRIES:
        record = models[gas, obt].evaluate(mass_kg_s)
        record.update(reference_temperature_K=233, reference_pressure_bar=437,
                      inlet_area_m2=AREA_M2, source_commit=provenance['source_commit'],
                      force_definition='positive CFD x; fixed obturator position',
                      mach_method='max observed Umax/Uin; projected reference Mach',
                      use_note='Not a spring stiffness or certified trip setting')
        records.append(record)
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader(); writer.writerows(records)
    return output.getvalue()
