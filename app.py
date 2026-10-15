import io
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from simulation import simulate, metrics, DEFAULTS

st.set_page_config(page_title="Smart Classroom Digital Twin", page_icon="🏫", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
.hero {padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#102a43,#176b87); color: white; margin-bottom: 1rem;}
.hero h1 {font-size: 2.1rem; margin: 0;}
.hero p {opacity: .9; margin-bottom: 0;}
.small-note {font-size: .9rem; color: #6b7280;}
</style>
<div class="hero"><h1>🏫 Smart Classroom Digital Twin</h1>
<p>CO₂ monitoring · occupancy-aware ventilation · simulation and policy comparison</p></div>
""", unsafe_allow_html=True)
st.caption("Educational simulation only — parameters are illustrative and are not real Veltech or campus sensor readings.")

with st.sidebar:
    st.header("Simulation settings")
    seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42, step=1)
    room = st.slider("Room volume (m³)", 80, 400, 180, 10)
    people = st.slider("People during class", 0, 80, 28)
    generation = st.slider("CO₂ generation coefficient", 0.0010, 0.0100, 0.0048, 0.0001, format="%.4f")
    noise = st.slider("Sensor noise SD (ppm)", 0.0, 60.0, 18.0, 1.0)
    low_flow = st.slider("Low ventilation (m³/h)", 30, 250, 110, 10)
    mid_flow = st.slider("Smart mid / high baseline flow (m³/h)", 150, 700, 420, 10)
    high_flow = st.slider("Smart high flow (m³/h)", 250, 900, 520, 10)
    t1 = st.slider("Smart controller threshold 1 (ppm)", 600, 1200, 900, 10)
    t2 = st.slider("Smart controller threshold 2 (ppm)", 800, 1600, 1050, 10)
    st.caption("The schedule is fixed in this demo: class periods at minutes 20–179 and 210–329.")

params = dict(room_volume_m3=room, occupants=people, generation_m3_person_hour=generation,
              sensor_noise_sd_ppm=noise, smart_low_flow_m3_h=low_flow,
              smart_mid_flow_m3_h=mid_flow, smart_high_flow_m3_h=high_flow,
              threshold_1_ppm=t1, threshold_2_ppm=max(t1,t2), seed=int(seed))
data = {p: simulate(p, **params) for p in ("smart", "low", "high")}
score = pd.DataFrame({name.title(): metrics(df) for name, df in data.items()}).T

st.subheader("Policy scorecard")
cols = st.columns(4)
for col, (label, value) in zip(cols, [
    ("Smart mean occupied CO₂", f"{metrics(data['smart'])['Mean occupied CO₂ (ppm)']:.1f} ppm"),
    ("Smart peak CO₂", f"{metrics(data['smart'])['Peak CO₂ (ppm)']:.1f} ppm"),
    ("Smart minutes >1000 ppm", str(metrics(data['smart'])['Occupied minutes >1000 ppm'])),
    ("Smart mean ventilation", f"{metrics(data['smart'])['Mean ventilation (m³/h)']:.1f} m³/h"),
]):
    col.metric(label, value)

tab1, tab2, tab3, tab4 = st.tabs(["CO₂ trends", "Ventilation control", "Sensor & anomalies", "Data & credibility"])
with tab1:
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for policy, label in [("smart","Smart control"),("low","Low fixed"),("high","High fixed")]:
        ax.plot(data[policy]["clock_hour"], data[policy]["co2_ppm"], label=label, linewidth=2)
    ax.axhline(1000, linestyle="--", label="Illustrative 1000 ppm reference")
    ax.set(xlabel="Clock time (hours from 09:00)", ylabel="CO₂ (ppm)", title="Simulated classroom CO₂ by ventilation policy")
    ax.grid(alpha=.25); ax.legend(ncol=2); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.dataframe(score, use_container_width=True)
with tab2:
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.step(data["smart"]["clock_hour"], data["smart"]["ventilation_m3_h"], where="post")
    ax.set(xlabel="Clock time", ylabel="Ventilation (m³/h)", title="Smart controller decisions")
    ax.grid(alpha=.25); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.info("The controller reacts to the simulated noisy sensor reading. It is a teaching example, not an HVAC control recommendation.")
with tab3:
    d = data["smart"]
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(d["clock_hour"], d["co2_ppm"], label="Twin state")
    ax.plot(d["clock_hour"], d["sensor_ppm"], alpha=.55, label="Noisy sensor")
    flagged = d[d["sensor_jump_flag"]]
    if not flagged.empty: ax.scatter(flagged["clock_hour"], flagged["sensor_ppm"], marker="x", label="Jump flagged")
    ax.set(xlabel="Clock time", ylabel="CO₂ (ppm)", title="Simulated sensor vs twin state")
    ax.grid(alpha=.25); ax.legend(); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.metric("Sensor jump flags for review", int(d["sensor_jump_flag"].sum()))
    st.caption("Flags mark absolute adjacent reading changes above 120 ppm; flagged data are not automatically removed.")
with tab4:
    st.subheader("Minute-level simulation data")
    selected = st.selectbox("Dataset", ["smart", "low", "high"])
    st.dataframe(data[selected], use_container_width=True, height=350)
    csv = data[selected].to_csv(index=False).encode("utf-8")
    st.download_button("Download selected policy CSV", csv, file_name=f"{selected}_simulation.csv", mime="text/csv")
    score_csv = score.to_csv().encode("utf-8")
    st.download_button("Download policy scorecard CSV", score_csv, file_name="policy_scorecard.csv", mime="text/csv")
    st.subheader("Model credibility and limitations")
    st.markdown("""
    - **Model:** single, well-mixed 180 m³ baseline zone with a one-minute Euler update.
    - **Inputs:** illustrative occupancy schedule, CO₂ generation, ventilation and sensor noise.
    - **Calibration:** a synthetic-data sensitivity exercise is not independent field validation.
    - **Reference line:** 1000 ppm is an illustrative comparison line, not a universal legal or health threshold.
    - **Not included:** humidity, particulates, VOCs, spatial airflow, fan power curves or equipment limits.
    - **Safety:** never connect this prototype to real HVAC equipment without measured data, independent validation and facilities/safety approval.
    """)

st.divider()
st.caption("Reproducibility: identical inputs and random seed produce the same simulation. Results are simulated, not measurements.")
