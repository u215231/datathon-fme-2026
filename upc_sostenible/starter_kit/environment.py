"""
starter_kit / environment.py
Entorn de simulació seqüencial pas a pas per al repte 'Carrega la Bateria!' (Datathon UPC Sostenible).
Avalua qualsevol BatteryAgent contra les dades del campus de forma rigorosa i sense data leakage.
"""

import json
import os
from pathlib import Path
import numpy as np
import pandas as pd

class CampusBatteryEnv:
    def __init__(self, hourly_data: pd.DataFrame, spec: dict = None, export_price: float = 0.0):
        """
        hourly_data: DataFrame indexat o amb columna 'Fecha' i columnes:
                     ['load_kw', 'pv_kw', 'precio_eur_per_kwh', 'co2_kg_per_kwh']
        spec: diccionari amb les especificacions físiques de la bateria.
        """
        if spec is None:
            spec_path = Path(__file__).parent / "battery_spec.json"
            with open(spec_path, encoding="utf-8") as f:
                spec = json.load(f)
                
        self.spec = spec
        self.export_price = export_price
        
        # Paràmetres de la bateria
        self.cap = float(spec["capacity_kwh"])
        self.power = float(spec["power_kw"])
        self.eta = float(spec["efficiency"])
        self.eta_c = self.eta ** 0.5
        self.eta_d = self.eta ** 0.5
        self.soc_init = float(spec["soc_init"]) * self.cap
        self.soc_min = float(spec["soc_min"]) * self.cap
        self.soc_max = float(spec["soc_max"]) * self.cap
        self.dt = float(spec.get("dt_hours", 1.0))
        
        self.df = hourly_data.copy().reset_index()
        if "Fecha" in self.df.columns:
            self.df["Fecha"] = pd.to_datetime(self.df["Fecha"])
        else:
            self.df["Fecha"] = pd.date_range("2026-01-01", periods=len(self.df), freq="1h")
            
        self.n = len(self.df)
        self.reset()

    def reset(self):
        self.t = 0
        self.soc = self.soc_init
        self.soc_series = []
        self.actions = []
        self.grid = []
        self.exports = []
        self.clipped = 0
        self.violations = 0
        self.infraccions_per_step = []
        return self._get_obs()

    def _get_obs(self):
        if self.t >= self.n:
            return None
            
        row = self.df.iloc[self.t]
        ts = row["Fecha"]
        
        # Previsions conegudes per a les properes 24 hores (PVPC i CO2)
        h_end = min(self.t + 24, self.n)
        future_prices = self.df["precio_eur_per_kwh"].iloc[self.t:h_end].values.tolist()
        future_co2 = self.df["co2_kg_per_kwh"].iloc[self.t:h_end].values.tolist()
        
        # Última hora transcorreguda (dades de t-1 a t)
        last_load = float(self.df["load_kw"].iloc[self.t - 1]) if self.t > 0 else float(row["load_kw"])
        last_pv = float(self.df["pv_kw"].iloc[self.t - 1]) if self.t > 0 else float(row["pv_kw"])
        
        obs = {
            "timestamp": ts,
            "hour": ts.hour,
            "day_of_week": ts.dayofweek,
            "soc_kwh": float(self.soc),
            "soc_pct": float(self.soc / self.cap),
            "soc_percent": float(self.soc / self.cap * 100),
            "preu_actual": float(row["precio_eur_per_kwh"]),
            "co2_actual": float(row["co2_kg_per_kwh"]),
            "preus_properes_24h": future_prices,
            "co2_properes_24h": future_co2,
            "noves_dades_5min": {
                "ultim_consum_kw": last_load,
                "ultima_solar_kw": last_pv
            }
        }
        return obs

    def step(self, action_kw: float):
        """Aplica l'acció en kW, valida la física i avança 1 hora."""
        p_req = float(action_kw)
        self.actions.append(p_req)
        infr_now = 0
        
        # 1. Limitar per potència màxima [-500, +500] kW
        p = np.clip(p_req, -self.power, self.power)
        if p != p_req:
            self.clipped += 1
            infr_now += 1

        # 2. Dinàmica del SOC
        if p > 0:  # Carregar
            max_c = (self.soc_max - self.soc) / (self.dt * self.eta_c)
            p_actual = min(p, max(0.0, max_c))
            if p_actual < p:
                self.clipped += 1
                infr_now += 1
            self.soc += p_actual * self.dt * self.eta_c
        elif p < 0:  # Descarregar
            max_d = (self.soc - self.soc_min) * self.eta_d / self.dt
            p_actual = -min(-p, max(0.0, max_d))
            if p_actual > p:
                self.clipped += 1
                infr_now += 1
            self.soc += p_actual * self.dt / self.eta_d
        else:
            p_actual = 0.0

        # Límits de seguretat del SOC
        if self.soc < self.soc_min - 1e-6 or self.soc > self.soc_max + 1e-6:
            self.violations += 1
            infr_now += 1
        self.soc = np.clip(self.soc, self.soc_min, self.soc_max)
        self.soc_series.append(self.soc)
        self.infraccions_per_step.append(infr_now)

        # 3. Balanç de xarxa amb el consum i la solar reals d'aquesta hora
        row = self.df.iloc[self.t]
        load = float(row["load_kw"])
        pv = float(row["pv_kw"])
        
        net = load - pv + p_actual
        if net > 0:
            self.grid.append(net)
            self.exports.append(0.0)
        else:
            self.grid.append(0.0)
            self.exports.append(-net)

        self.t += 1
        done = (self.t >= self.n)
        next_obs = None if done else self._get_obs()
        return next_obs, done

    def evaluate_results(self, alpha=0.7, beta=0.3, mask=None):
        """Calcula les mètriques finals comparant amb el Baseline sense bateria (opcionalment filtrades per una màscara temporal)."""
        grid = np.asarray(self.grid)
        exports = np.asarray(self.exports)
        price = self.df["precio_eur_per_kwh"].values[:len(grid)]
        co2 = self.df["co2_kg_per_kwh"].values[:len(grid)]

        # Baseline sense bateria: grid_base = max(0, load - pv)
        load = self.df["load_kw"].values[:len(grid)]
        pv = self.df["pv_kw"].values[:len(grid)]
        base_grid = np.maximum(load - pv, 0.0)

        if mask is not None:
            m = np.asarray(mask)[:len(grid)]
            infr_arr = np.asarray(self.infraccions_per_step)[:len(grid)]
            infraccions = int(np.sum(infr_arr[m]))
            grid = grid[m]
            exports = exports[m]
            price = price[m]
            co2 = co2[m]
            base_grid = base_grid[m]
        else:
            infraccions = int(self.clipped + self.violations)

        cost_participant = float(np.sum(grid * price) - np.sum(exports * self.export_price))
        co2_participant = float(np.sum(grid * co2))

        cost_base = float(np.sum(base_grid * price))
        co2_base = float(np.sum(base_grid * co2))

        d_co2 = (co2_base - co2_participant) / co2_base if co2_base > 0 else 0.0
        d_cost = (cost_base - cost_participant) / cost_base if cost_base > 0 else 0.0

        # Penalització per infraccions físiques (0.20 punts de Score per cada infracció)
        penalties = 0.002 * infraccions
        score = alpha * d_co2 + beta * d_cost - penalties

        return {
            "score": round(max(0.0, score * 100), 2),  # Punts sobre 100
            "co2_estalviat_pct": round(d_co2 * 100, 2),
            "cost_estalviat_pct": round(d_cost * 100, 2),
            "co2_estalviat_kg": round(co2_base - co2_participant, 1),
            "cost_estalviat_eur": round(cost_base - cost_participant, 2),
            "co2_participant_kg": round(co2_participant, 1),
            "cost_participant_eur": round(cost_participant, 2),
            "co2_baseline_kg": round(co2_base, 1),
            "cost_baseline_eur": round(cost_base, 2),
            "infraccions": infraccions,
        }

def run_agent_simulation(agent, hourly_data: pd.DataFrame, spec: dict = None):
    """Funció d'utilitat per executar un agent complet sobre una sèrie de dades."""
    env = CampusBatteryEnv(hourly_data, spec=spec)
    obs = env.reset()
    done = False
    while not done:
        action = agent.act(obs)
        obs, done = env.step(action)
    return env.evaluate_results()

