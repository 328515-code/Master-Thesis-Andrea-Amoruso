# EFV threshold design tool

Select hydrogen or nitrogen and enter a threshold mass flow in **g/s**. The app compares axial force and pressure loss for obturators Aâ€“D, shows the CFD points and fitted parabolas, and marks an estimated local Mach 0.3 boundary for each geometry.

## Run locally

Use Python **3.13** (the tested runtime). On Windows, double-click `run_windows.cmd`; the first run creates an isolated environment at `%USERPROFILE%\.efv-tool\py313` and installs the dependencies. This short path avoids Windows path-length errors when the project is inside a deeply nested thesis folder. An old `.venv` inside the project is not used by this launcher. To install without opening the app, run `run_windows.cmd --setup-only`.

For manual Windows setup, run these commands in Command Prompt from `design_tool`:

```text
py -3.13 -m venv "%USERPROFILE%\.efv-tool\py313"
"%USERPROFILE%\.efv-tool\py313\Scripts\python.exe" -m pip install -r requirements.txt
"%USERPROFILE%\.efv-tool\py313\Scripts\python.exe" -m streamlit run streamlit_app.py
```

On macOS or Linux:

```text
python -m venv .venv
```

Activate it with `source .venv/bin/activate`, then:

```text
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Run these commands from `design_tool`. The application opens in a browser. After installation, calculations use only bundled data and need neither an internet connection nor OpenFOAM, ParaView or CoolProp. Python plus the installed dependencies are required: this is a Streamlit web application, not a standalone compiled `.exe`.

## Hosted access

The same directory can be hosted on a Streamlit-compatible server, including Streamlit Community Cloud. Set the entry point to `design_tool/streamlit_app.py` and use Python 3.13; the adjacent `requirements.txt` supplies the dependencies. A hosted instance allows access from devices with a browser while the server is running. No online deployment is included in this delivery. See https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies .

## Interpretation

- The reference state is **437 bar absolute, 233 K**, with the fixed CFD obturator position. Only gas and mass flow are design inputs; the app does not adjust thermodynamic state or geometry dimensions.
- Actual flow conversion uses `rho * 4.658925e-5 * U` in kg/s. This discretized inlet area differs from the nominal area used to normalize the force coefficient in Chapter 4.
- For each gas and geometry, equal-weight least squares fits `F = k_F * UÂ²` through zero to three terminal force means (5, 10 and 15 m/s). This is a regression-based interpolation within the sampled interval, not an exact three-point interpolant. Pressure loss is fitted independently with the same form.
- Dashed parts outside the CFD interval are unvalidated extrapolations, even if the Mach estimate is below 0.3. Additional CFD is needed before using these extrapolated loads for a spring setting.
- The Mach screen uses `alpha = max(Umax_3D / Uin)` over the three full-volume maxima and `Mach_est = alpha * Uin / sound_speed`. Its boundary is an estimate obtained by projecting that amplification, not a measured transition or a guaranteed upper bound at unsimulated flows.
- At or above the boundary, force and pressure design outputs are withheld. A dotted curve and cross still locate the **formal mathematical projection**; the CSV labels that projection separately. It must not be used as a spring-design load.
- Nitrogen A's estimated boundary is approximately **335.09 g/s**, slightly below the highest simulated flow (336.39 g/s), although the observed peak at that CFD point is Mach 0.2979. The larger amplification observed at 5 m/s makes the envelope deliberately more restrictive. It does not contradict the archived field maximum.
- Force is the positive CFD x-component. Verify the closing direction and account for preload, friction, stroke and other loads. The tool does not calculate spring stiffness or predict transient closure. Low Mach alone does not validate constant density at the large nitrogen pressure losses.
- Error bars are temporal standard deviations reconstructed from terminal CVs, not confidence intervals or prediction uncertainties. Hydrogen B's maximum pointwise fit mismatch is about 15.65%; inspect this diagnostic before using the smoothed curve.

## Data provenance and regeneration

`data/provenance.json` identifies the exact thesis source revision and SHA-256 hashes of the copied audited files. Files are integrity-checked at launch. All 24 force/pressure response means and 24 volume peaks are retained. Most integral averages cover iterations 2700â€“3000; N2 A at 5 m/s uses 1072â€“1372, and its velocity field is from iteration 1000. Other velocity fields use iteration 3000.

For a new CFD campaign, replace the audited inputs and explicitly regenerate the provenance manifest after checking the state, units, geometry and averaging windows. Do not edit a single table value merely to bypass the integrity check. Every new campaign requires reassessing the fit and the Mach amplification assumption.

To validate or regenerate the thesis figures:

```text
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python make_thesis_figures.py
```

Tests cover the analytic fit, mass-flow units, all eight Mach boundaries, exact-boundary withholding, extrapolation, zero/invalid inputs, short-run provenance, altered-data rejection, CSV semantics and Streamlit interaction. Figure generation uses the same model as the application and writes to `../Results/Chapter5`.
