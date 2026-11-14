# Kit d'Inici (Starter Kit) — Repte UPC Sostenible
## Datathon 2026 — Optimització de la Bateria del Campus

Aquest directori conté els mòduls de programació, dades de configuració física i el quadern de referència per al desenvolupament dels algorismes de control.

### Contingut del Directori

* **`agent.py`**: Plantilla oficial que defineix la classe `BatteryAgent`. Conté la implementació del mètode `act(obs)` on s'ha d'incorporar la política de decisió. S'inclou una heurística bàsica funcional com a punt de partida.
* **`check_submission.py`**: Script de validació tècnica local. Permet testejar l'agent o el paquet `submission.zip` abans de trametre'l a la web oficial (`python check_submission.py agent.py`).
* **`environment.py`**: Entorn de simulació seqüencial local (`CampusBatteryEnv`). Reprodueix la dinàmica d'estat de càrrega, els rendiments de conversió i calcula les mètriques oficials de puntuació.
* **`battery_spec.json`**: Paràmetres físics del sistema d'emmagatzematge industrial (capacitat 2.000 kWh, potència límit 500 kW, rendiment de cicle complet del 90%).
* **`tutorial.ipynb`**: Quadern Jupyter de referència. Il·lustra el procediment de càrrega de dades d'entrenament, alineació horària, anàlisi exploratòria, execució de la simulació i entrenament d'un model de predicció supervisat.

### Instruccions de Desenvolupament

1. Executar el quadern `tutorial.ipynb` per analitzar la corba de càrrega i generació fotovoltaica del campus.
2. Desenvolupar i validar la lògica de control a `agent.py`.
3. Verificar localment que l'agent no generi infraccions físiques sobre el simulador `environment.py`.
4. Per a lliuraments amb models supervisats serialitzats, empaquetar els fitxers en un arxiu `submission.zip` que contingui `agent.py` i els fitxers binaris `.pkl`.
5. Trametre el fitxer a través de la plataforma web oficial per a la seva avaluació automàtica sobre les setmanes de test secret.
