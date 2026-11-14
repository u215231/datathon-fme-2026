# Repte UPC Sostenible: Optimització de la Bateria del Campus
## Datathon 2026 — Transició Energètica i Descarbonització

Repositori oficial del repte d'optimització energètica, ciència de dades i transició ecològica promogut per **UPC Sostenible** per a la gestió d'una bateria industrial de 2.000 kWh i 500 kW connectada al campus de la Universitat Politècnica de Catalunya.

L'objectiu dels participants és programar una política de control (`BatteryAgent`) per gestionar de forma òptima la càrrega i descàrrega de la bateria en intervals horaris, minimitzant simultàniament les emissions de $\text{CO}_2$ de la xarxa elèctrica (70% del pes) i el cost econòmic de la factura elèctrica (30% del pes) respecte a l'escenari base del campus operant sense emmagatzematge.

---

### Estructura del Projecte

```text
├── docs/                           # Documentació oficial del repte
│   ├── ENUNCIAT.md                 # Bases tècniques i formulació matemàtica del problema
│   ├── GUIA_VARIABLES.md           # Especificació detallada de telemetries i sensors
│   └── enunciat_participants_latex.md # Documentació complementària en format LaTeX
│
├── starter_kit/                    # Paquet de treball per als participants
│   ├── README.md                   # Guia ràpida de desenvolupament
│   ├── agent.py                    # Plantilla de la classe BatteryAgent (heurística base)
│   ├── check_submission.py         # Validador local de solucions per a la consola
│   ├── environment.py              # Motor de simulació seqüencial i avaluador de mètriques
│   ├── battery_spec.json           # Paràmetres físics del sistema d'emmagatzematge
│   └── tutorial.ipynb              # Quadern Jupyter de referència
│
├── data/                           # Conjunts de dades
│   ├── train/                      # Dades d'entrenament (6 fitxers CSV d'un any sencer)
│   └── test_hidden/                # Conjunt de test secret utilitzat per la plataforma web
│
├── scripts/                        # Scripts interns de curació de dades
│   ├── consolidate_data.py         # Consolidació de telemetries brutes de sensors
│   ├── download_ree.py             # Descàrrega de preus PVPC i intensitat de CO2 (API REE)
│   └── split_train_test.py         # Generador de les particions temporals train/test
│
├── app.py                          # Plataforma web oficial d'avaluació i Leaderboard (Streamlit)
├── requirements.txt                # Dependències de Python del sistema
└── README.md                       # Documentació general
```

---

### Execució de la Plataforma Web Localment

Per iniciar el servei d'avaluació i classificació en temps real:

```bash
pip install -r requirements.txt
streamlit run app.py
```
