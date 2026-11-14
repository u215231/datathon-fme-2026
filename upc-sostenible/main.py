import pandas as pd

df_contador = pd.read_csv("data/train/contador.csv", parse_dates=["Fecha"]).set_index("Fecha")
demanda_raw = (-df_contador["Contador - POTENCIA ACTIVA EXPORTADA (kW)"]).clip(lower=0, upper=5000)
load_hourly = demanda_raw.resample("1h").mean().dropna()

df_inversor = pd.read_csv("data/train/inversor.csv", parse_dates=["Fecha"]).set_index("Fecha")
inv_cols = [c for c in df_inversor.columns if "POTENCIA ACTIVA" in c and "FASE" not in c]
pv_raw = df_inversor[inv_cols].sum(axis=1).clip(lower=0)
pv_hourly = pv_raw.resample("1h").mean().dropna()

df_pvpc = pd.read_csv("data/train/precio_pvpc.csv", parse_dates=["Fecha"]).set_index("Fecha")
df_co2 = pd.read_csv("data/train/co2_red.csv", parse_dates=["Fecha"]).set_index("Fecha")

df_campus_hourly = pd.DataFrame({
    "load_kw": load_hourly,
    "pv_kw": pv_hourly,
    "precio_eur_per_kwh": df_pvpc["precio_eur_per_kwh"],
    "co2_kg_per_kwh": df_co2["co2_kg_per_kwh"]
}).dropna()

print(f"Dataset preparat: {len(df_campus_hourly)} hores d'entrenament registrades.")
print(df_campus_hourly.head())