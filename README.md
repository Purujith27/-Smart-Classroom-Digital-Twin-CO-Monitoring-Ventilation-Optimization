# Smart Classroom Digital Twin — Final Project Package

## What this package contains
- `app.py` — interactive Streamlit dashboard with configurable parameters, three ventilation policies, charts, metrics and CSV downloads.
- `simulation.py` — reusable and documented simulation engine.
- `Smart_Classroom_Digital_Twin.ipynb` — original notebook supplied with the project.
- `Technical_Report.pdf` — supplied technical report.
- `outputs/` — supplied example CSV and chart outputs.
- `tests/test_simulation.py` — automated tests for reproducibility, bounds and baseline behavior.
- `ANTIGRAVITY_PROMPT.md` — copy/paste prompt for Google Antigravity to build a polished production-style frontend around this project.

## Run locally (Windows)
1. Install Python 3.10 or newer.
2. Extract this ZIP to a normal folder.
3. Open that folder in Terminal / PowerShell.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
5. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. Run the tests:
   ```powershell
   python -m unittest discover -s tests -v
   ```
7. Launch the app:
   ```powershell
   streamlit run app.py
   ```
8. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```

## Important model notes
This is an educational simulation. Occupancy, room volume, generation coefficient, sensor noise and ventilation rates are illustrative. They are not live Veltech measurements. The controller must not be used to operate real building equipment. Real deployment would require synchronized field measurements, independent calibration/validation, uncertainty analysis and safety/facilities approval. CO₂ alone does not measure all indoor air-quality risks.

## Final submission checklist
- [ ] Run all tests successfully.
- [ ] Run the dashboard and verify every tab.
- [ ] Change a few sidebar parameters and confirm plots/metrics update.
- [ ] Download both policy CSV and selected simulation CSV.
- [ ] Capture screenshots of overview, CO₂ trends, controller decisions and data export.
- [ ] Keep the technical report's results consistent with the generated run; do not claim synthetic data are campus measurements.
- [ ] Add student name, register number, department and institution only where required by your submission format.
