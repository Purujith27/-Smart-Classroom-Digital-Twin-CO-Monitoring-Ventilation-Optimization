"""Transparent single-zone classroom CO2 digital-twin simulation.
All defaults are illustrative, not real campus measurements.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

DEFAULTS = {
    "room_volume_m3": 180.0,
    "outdoor_co2_ppm": 420.0,
    "occupants": 28,
    "generation_m3_person_hour": 0.0048,
    "sensor_noise_sd_ppm": 18.0,
    "smart_low_flow_m3_h": 110.0,
    "smart_mid_flow_m3_h": 420.0,
    "smart_high_flow_m3_h": 520.0,
    "threshold_1_ppm": 900.0,
    "threshold_2_ppm": 1050.0,
    "minutes": 360,
    "seed": 42,
}

def simulate(policy="smart", *, room_volume_m3=180.0, outdoor_co2_ppm=420.0,
             occupants=28, generation_m3_person_hour=0.0048,
             sensor_noise_sd_ppm=18.0, smart_low_flow_m3_h=110.0,
             smart_mid_flow_m3_h=420.0, smart_high_flow_m3_h=520.0,
             threshold_1_ppm=900.0, threshold_2_ppm=1050.0,
             minutes=360, seed=42):
    """Return minute-level simulated observations for smart, low, or high policy."""
    if policy not in {"smart", "low", "high"}:
        raise ValueError("policy must be 'smart', 'low', or 'high'")
    if room_volume_m3 <= 0 or minutes < 1 or occupants < 0:
        raise ValueError("room volume/minutes must be positive and occupants non-negative")
    if generation_m3_person_hour < 0 or sensor_noise_sd_ppm < 0:
        raise ValueError("generation and sensor noise must be non-negative")
    rng = np.random.default_rng(seed)
    c = float(outdoor_co2_ppm)
    rows = []
    for m in range(1, int(minutes) + 1):
        occupied = (20 <= m < 180) or (210 <= m < 330)
        people = int(occupants if occupied else 0)
        sensor = c + rng.normal(0, sensor_noise_sd_ppm)
        if policy == "smart":
            q = smart_high_flow_m3_h if sensor >= threshold_2_ppm else (
                smart_mid_flow_m3_h if sensor >= threshold_1_ppm else smart_low_flow_m3_h)
        elif policy == "low":
            q = smart_low_flow_m3_h
        else:
            q = smart_mid_flow_m3_h
        # Euler update; time step = one minute = 1/60 hour.
        c = max(outdoor_co2_ppm, c + (1/60) * (
            people * generation_m3_person_hour * 1e6
            - q * (c - outdoor_co2_ppm)) / room_volume_m3)
        rows.append({
            "minute": m, "clock_hour": 9 + m/60, "occupied": int(occupied),
            "people": people, "co2_ppm": c, "sensor_ppm": sensor,
            "ventilation_m3_h": q, "policy": policy
        })
    df = pd.DataFrame(rows)
    df["sensor_jump_flag"] = df["sensor_ppm"].diff().abs().gt(120).fillna(False)
    return df

def metrics(df):
    occupied = df.loc[df["occupied"].eq(1)]
    return {
        "Peak CO₂ (ppm)": round(float(df["co2_ppm"].max()), 1),
        "Mean occupied CO₂ (ppm)": round(float(occupied["co2_ppm"].mean()), 1),
        "Occupied minutes >1000 ppm": int(occupied["co2_ppm"].gt(1000).sum()),
        "Mean ventilation (m³/h)": round(float(df["ventilation_m3_h"].mean()), 1),
        "Sensor jump flags": int(df["sensor_jump_flag"].sum()),
    }
