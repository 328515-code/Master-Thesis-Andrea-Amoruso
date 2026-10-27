# Preliminary SIM_DoE_2210 hydrogen data audit

Source: uploaded archive `Simulations setup and postpro.rar`, path `Hydrogen/Sim_H2_Flux{05,10,15}_Obt_{A,B,C,D}/postProcessing/`.

Values in `H2_2210_terminal_window.csv` were obtained from the area-averaged kinematic inlet and outlet pressures and the axial pressure-plus-viscous forces in the OpenFOAM function-object output files. The mean and population standard deviation cover iterations 2700–3000 inclusive (301 samples).

**Fluid-property provenance:** Every uploaded hydrogen case uses `nu = 1.05e-04 m^2/s` and `rhoInf = 0.0838 kg/m^3`. Pressure differences in Pa are computed as 0.0838 × mean [P_in − P_out] in m²/s². The `forces.dat` vectors are already in newtons with `rhoInf` included; do not multiply them by density again.

**Scope and limitations:** This is a descriptive terminal-window screening, not validated convergence. The archive lacks solver residual histories, outlet flow measurements and grid-sensitivity evidence; nitrogen case folders contain no `postProcessing` output files. The reference-state properties correspond to approximately 1 atm and 20°C, **not** to 437 bar and −40°C. Force sign refers to the global x axis, not necessarily the mechanical closing direction.

The full 24-case factorial design describes configurations, not 24 verified CFD responses.
