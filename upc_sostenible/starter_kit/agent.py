"""
agent.py
Plantilla oficial de l'agent de control per al repte de la bateria de UPC Sostenible.
Datathon 2026.
"""

# import joblib  # Descomenteu si utilitzeu models serialitzats (.pkl)

class BatteryAgent:
    def __init__(self):
        """Inicialització de l'agent.
        S'executa una sola vegada a l'inici del període d'avaluació.
        Permet carregar models predictius o definir llindars d'operació.
        """
        # Paràmetres d'operació de la política de referència
        self.llindar_preu_carrega = 0.08      # €/kWh
        self.llindar_preu_descarrega = 0.16   # €/kWh
        self.potencia_nominal_kw = 500.0      # Potència màxima de l'inversor (kW)

        # Memòria històrica d'hores passades (permet consultar el passat dins de la simulació):
        # self.historial = []

    def act(self, obs: dict) -> float:
        """Determina la consigna de potència activa de la bateria per a l'hora actual.

        Paràmetres:
        -----------
        obs : dict amb les variables d'estat disponibles a l'hora actual:
            - "timestamp": pd.Timestamp amb la data i hora d'avaluació.
            - "hour": int de 0 a 23 (hora del dia).
            - "day_of_week": int de 0 (dilluns) a 6 (diumenge).
            - "soc_kwh": float amb l'energia emmagatzemada actual (0.0 a 2.000.0 kWh).
            - "soc_pct": float amb l'estat de càrrega relatiu [0.0, 1.0].
            - "preu_actual": float amb el preu del PVPC d'aquesta hora (€/kWh).
            - "co2_actual": float amb la intensitat de CO2 peninsular (kg CO2/kWh).
            - "preus_properes_24h": llista de preus horaris de les properes 24 hores (€/kWh).
            - "co2_properes_24h": llista de factors d'emissió de CO2 de les properes 24 hores (kg/kWh).
            - "noves_dades_5min": dades mesurades pels sensors en la darrera hora transcorreguda.

        Retorna:
        --------
        float : Consigna de potència activa en kW:
            > 0  -> Càrrega d'energia des de la xarxa interna (fins a +500.0 kW).
            < 0  -> Descàrrega d'energia cap al campus (fins a -500.0 kW).
            = 0  -> Bateria en mode d'espera (0.0 kW).
        """
        hora = obs["hour"]
        preu = obs["preu_actual"]
        soc = obs["soc_pct"]
        co2 = obs["co2_actual"]

        # Política heurística de referència basada en regles temporals:
        consigna = 0.0
        # 1. Període vall nocturn (01:00 a 06:00): Càrrega en hores de baixa emissió i baix cost
        if 1 <= hora <= 6 and preu < self.llindar_preu_carrega and soc < 0.85:
            consigna = 350.0

        # 2. Període solar central (11:00 a 15:00): Càrrega d'aprofitament amb preus moderats
        elif 11 <= hora <= 15 and preu < 0.10 and soc < 0.95:
            consigna = 250.0

        # 3. Període punta vespertí (18:00 a 22:00): Descàrrega per cobrir la demanda màxima del campus
        elif 18 <= hora <= 22 and (preu > self.llindar_preu_descarrega or co2 > 0.10) and soc > 0.15:
            consigna = -450.0

        # Clamping de seguretat física per evitar infraccions de retallada (clipping):
        # Capacitat màxima: 2.000 kWh, Rendiment: sqrt(0.90) ~= 0.9487
        soc_kwh = float(obs["soc_kwh"])
        rendiment_eta = 0.9487
        max_carrega = min(self.potencia_nominal_kw, (2000.0 - soc_kwh) / rendiment_eta)
        max_descarrega = min(self.potencia_nominal_kw, soc_kwh * rendiment_eta)

        return float(max(-max_descarrega, min(max_carrega, consigna)))
