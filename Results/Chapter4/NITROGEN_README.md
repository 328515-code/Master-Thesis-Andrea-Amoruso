# Nitrogen Chapter 4 additions

Source: local `Nitrogen/Sim_N2_Flux{05,10,15}_Obt_{A,B,C,D}` OpenFOAM cases, inspected 2026-11-04. Original simulation files were read only. ParaView 6.1.1 processed one copied case at a time, without its graphical interface; staging copies were discarded after successful extraction.

## Coverage and limitations

- Twelve complete volumes were processed, with 52 processor subdomains each.
- A at 5 m/s uses iteration 1000, the latest complete saved U/p volume. The integral histories in the thesis extend to 1372 and are averaged over 1072Ã¢â‚¬â€œ1372; the volume diagnostic is not from that interval.
- The other eleven processed cases use iteration 3000. All four 15 m/s cases used in the figures are complete.
- ParaView reported isolated non-manifold cells that could not be contoured. These can cause local slice omissions. The full-domain velocity maximum is independently scanned from the original cell-centred U arrays and is unaffected by the contour filter.

## Definitions

`nitrogen_mach_velocity_data.json` records unrounded speeds, solver iterations, cell counts, slice ranges and peak locations. `max_cell_location` is processor name and zero-based local cell index, not a global coordinate.

The full-domain peak is the largest norm of the internal cell-centred U vectors over every processor. The reader's loaded volume cell count was checked against the raw field count. The channel-slice peak uses interpolated point velocities on y=0 and z=0 in 0.035 <= x <= 0.046 m. It is a sampled channel-region diagnostic, not a maximum over every channel.

Mach = speed / 593.3679237855702 m/s. `nitrogen_sound_speed.json` records CoolProp 8.0.0 HEOS::Nitrogen at 233 K and 43.7 MPa, using the Span et al. equation of state (DOI 10.1063/1.1349047; https://coolprop.org/fluid_properties/fluids/Nitrogen.html). This is a fixed-reference diagnostic, not a local compressible thermodynamic solution. The largest available Mach is 0.2979451801, close to 0.3.

Active simulation density is 481.352 kg/m3 and kinematic viscosity is 7.932e-8 m2/s. U dimensions are [0 1 -1 0 0 0 0]; p dimensions are [0 2 -2 0 0 0 0]. Other saved fields include k, omega, nut, yPlus and surface field phi. Displayed pressure is rho*p, in Pa, relative to the zero-pressure outlet.

## Figures

Eight PNGs show y=0 at 15 m/s, iteration 3000. Each is 1800 x 520 pixels with the same orthographic camera and spatial scale. Velocity uses matplotlib Turbo and pressure Coolwarm, sampled at 256 colours. Fixed ranges cover both planes of the twelve complete nitrogen cases:

- Velocity: 0 to 140.61379950830292 m/s.
- Pressure: -3300125.3384140623 to 4272714.4470156245 Pa.

These ranges differ from the hydrogen ranges. Equal colours across the two gas sets do not denote equal values. Coolwarm is linearly mapped over the full range; its white midpoint is not zero pressure.

## Recalculation

`nitrogen_recompute.py` checks the archived maxima, ranges and Mach values using Python's standard library. The full local extraction workflow and compact VTM slices are retained separately under `Thesis_PostProcessing/Nitrogen_Update`; they are not simulation inputs or GitHub thesis source files.
