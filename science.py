"""Simplified science models behind NanoQuest.
EDUCATIONAL VALUES ONLY. Check against nanomedicine literature and cite sources."""
import numpy as np

K_WATER = 0.6      # W/m.K, water
K_FE3O4 = 7.0      # W/m.K, magnetite

STABLE_MIN_NM = 10
STABLE_MAX_NM = 30

BODY_TEMP = 37.0
HYPER_MIN = 42.0
HYPER_MAX = 45.0
TOXIC_CONC = 4.0         # mg/mL
HEATING_COEFF = 0.0125   # deg C per (mg/mL . mT^2)

RELEASE_BASE = 0.05      # 1/h
RELEASE_PER_CONC = 0.05  # 1/h per mg/mL


def volume_fraction(v_particles, v_fluid):
    return v_particles / (v_particles + v_fluid)


def maxwell_k_eff(phi, k_f=K_WATER, k_p=K_FE3O4):
    num = k_p + 2 * k_f + 2 * phi * (k_p - k_f)
    den = k_p + 2 * k_f - phi * (k_p - k_f)
    return k_f * num / den


def stability_index(d_nm):
    """>= 1 means stable. Equals 1 at 10 nm and 30 nm, peaks in between."""
    return min(d_nm / STABLE_MIN_NM, STABLE_MAX_NM / d_nm)


def body_temperature(conc_mg_ml, field_mT):
    return BODY_TEMP + HEATING_COEFF * conc_mg_ml * field_mT ** 2


def reference_therapy(conc_mg_ml, field_mT):
    if conc_mg_ml > TOXIC_CONC:
        return "TOXIC"
    temp = body_temperature(conc_mg_ml, field_mT)
    if temp < HYPER_MIN:
        return "TOO_COLD"
    if temp <= HYPER_MAX:
        return "THERAPEUTIC"
    return "TOO_HOT"


def release_fraction(t_hours, conc_mg_ml):
    k = RELEASE_BASE + RELEASE_PER_CONC * conc_mg_ml
    return 1 - np.exp(-k * np.asarray(t_hours, dtype=float))
