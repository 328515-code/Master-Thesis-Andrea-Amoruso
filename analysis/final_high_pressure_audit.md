# Final high-pressure simulation response audit

The attached high-pressure CFD archive is the numerical source for these results. This audit records 24 geometrically defined CFD cases (12 H2 and 12 N2), each with pressure, force, inlet-flow and yPlus histories through solver iteration 3000. The nominal study state in the archive is 437 bar and 233 K; the actual boundary condition is a zero *kinematic-pressure reference*, and the fluid state is represented through the constant-density and viscosity inputs.

**Gas properties from active dictionaries**: H2 nu=2.709e-7 m2/s, rhoInf=33.77 kg/m3; N2 nu=7.932e-8 m2/s, rhoInf=481.352 kg/m3.

**Processing**: for each case, match output values by solver iteration and compute the arithmetic mean and population CV over iterations 2700 through 3000 inclusive (301 samples). Delta-p [Pa] = rhoInf*(P_in-P_out), where P is an area-averaged kinematic pressure; F_x [N] is the sum of the recorded dimensional pressure and viscous force x-components and must not be multiplied by rhoInf again. The CSV retains pressure in kPa and axial force in N. CV is a descriptive terminal-window screening statistic, not proof of convergence.

**Source-integrity issue**: The nitrogen, 5 m/s, obturator A case's five postProcessing numerical histories are byte-for-byte identical to the corresponding hydrogen case, even though their OpenFOAM constant/physicalProperties and system/forces dictionaries use different values. This is flagged as REVIEW_DUPLICATED_H2_CASE in the CSV and not included as an independent N2 response in the thesis tables. Please verify against the original N2 computation or re-export the correct postProcessing files before drawing conclusions for this point.

**Numerical-quality cautions**: Hydrogen obturator B at 10 and 15 m/s has substantial terminal variation; hydrogen B at 15 m/s has pressure CV 10.246% and force CV 12.461%. Maximum obturator yPlus ranges from about 156 to 1256 for H2 and reaches approximately 4306 for N2. The highest N2 delta-p is about 4.225 MPa (9.7% of 43.7 MPa). The archive contains no comprehensive solver residual logs or grid-sensitivity reports in the inspected case files. These data support descriptive CFD comparison, not validated valve closure or certification.

H2 is the principal refuelling-gas study. N2 is a supplementary industrial-fluid comparison at equal inlet velocity; its substantially higher density means the flow rates are not comparable on an equal-mass-flow basis.
