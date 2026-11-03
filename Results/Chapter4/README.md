# Chapter 4 figures and derived data

This directory supports only Chapter 4 (`04_Chapter3.tex`).

## Provenance

- Integral response source: `analysis/final_high_pressure_responses.csv`, repository revision `6ff0c5b819ad09fecfe88034e4a0c721ade30d23`. All 12 hydrogen means were independently recalculated from local `postProcessing` histories and agree to the source table's reported precision.
- `coefficient_data.json`: pressure coefficient = mean pressure drop in Pa / (0.5 rho Uin^2); axial-force coefficient = mean Fx / (0.5 rho Uin^2 Ain), with Ain = pi (0.0078/2)^2 m2, the nominal inlet area defined in Chapter 3. Original force values are already dimensional. The two coefficient tables use all 24 audited cases, including the corrected shorter N2/U05/A run.
- `sound_speed.json`: normal hydrogen, CoolProp 8.0.0 HEOS, T = 233 K and absolute P = 43.7 MPa; speed of sound 1611.7774059916314 m/s, density 33.790256780579504 kg/m3. EOS: Leachman et al., DOI 10.1063/1.3160306. CFD density is retained at 33.77 kg/m3. The ideal-gas comparison uses gamma = 1.4 and molar mass 0.00201588 kg/mol.
- `mach_velocity_data.json`: final iteration 3000 for all 12 hydrogen cases. The full-domain maximum comes directly from original binary `processor*/3000/U` internal fields (little-endian 64-bit scalar triples), scanning one processor at a time. The decoded cell counts match ParaView's mesh counts. `max_cell_location` records processor and zero-based local cell index; it is not a spatial coordinate.
- Channel-region sampled peak: maximum of interpolated speed on y = 0 and z = 0 within 0.035 <= x <= 0.046 m. Peak coordinates and plane are retained. This is not a complete sampling of every hole. The independent volume maximum bounds all resolved cell-centred channel speeds.
- Mach numbers are velocity divided by a fixed reference sound speed, not an energy-coupled local thermodynamic solution. Peak quantities are not 301-sample averages.

## Figures

Eight PNGs show H2, Uin = 15 m/s, obturators A-D, plane y = 0, iteration 3000. The 1800 x 520 layout is sized for stacked full-width panels in the thesis. Geometry, orthographic camera and per-variable colour ranges are identical across all panels. The velocity map is Turbo; pressure is Coolwarm. These are the user's selected palettes.

The limits retain those used across all twelve hydrogen cases and both slice planes: velocity 0 to 140.9807253958359 m/s; outlet-referenced pressure -224227.6223730469 to 299348.2618457032 Pa. Coolwarm's neutral colour is at the range midpoint, not at zero. Pressure conversion is rhoInf * OpenFOAM kinematic p. Cell-to-point interpolation precedes slicing.

ParaView 6.1.1 reported non-manifold triangulation warnings on the source meshes. The slices were nonempty and visually inspected, but small local omissions cannot be excluded. The raw-volume velocity maximum is calculated independently of those contour operations. The source simulations were read only.

## Recompute coefficient and Mach table values

Run `python Results/Chapter4/recompute_tables.py` from the repository root. This recomputes coefficients from the audited CSV and Mach numbers from the archived velocity extrema, checking them against the JSON data. Re-extracting extrema requires the original OpenFOAM files, which are intentionally not committed to the thesis repository.
