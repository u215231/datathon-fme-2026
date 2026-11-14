**Desenvolupar aquest projecte en 24 hores és totalment viable**. El repte està dissenyat específicament per a una competició de 24 hores i té una estructura modular que permet començar amb una solució funcional senzilla i anar-la millorant iterativament.

---

### 1. Què hem de fer? (El Repte i l'Objectiu)

L'objectiu principal és programar un algorisme de control dins d'una classe Python anomenada **`BatteryAgent`** (al fitxer `agent.py`) amb el mètode **`act(obs) -> float`**. Aquest mètode rep cada hora l'estat del sistema (`obs`) i ha de retornar la consigna de potència de càrrega o descàrrega ($P_t \in [-500, +500]\text{ kW}$) d'una **bateria industrial de 2.000 kWh**.

- **Funció objectiu a maximitzar:**  
  $$\text{Score} = \max\Big(0,\; 0{,}70 \cdot \Delta\text{CO}_2(\%) + 0{,}30 \cdot \Delta\text{Cost}(\%) - 1{,}00 \cdot \text{Infraccions}\Big)$$
- **Prioritats:** El **70% de la puntuació** depèn de reduir les emissions de $\text{CO}_2$ (evitant importar de la xarxa en hores contaminants) i el **30%** de reduir el cost econòmic (PVPC).
- **Regla d'or (Anti-penalització):** Cada consigna que superi els límits de l'inversor ($\pm 500\text{ kW}$) o que intenti carregar/descarregar fora del rang $[0, 2.000]\text{ kWh}$ resta **1,00 punt net** de la nota final.

---

### 2. Què hem de predir (i què NO cal predir)?

Un dels grans avantatges de l'enunciat és que **l'avaluador ja ens facilita la informació futura del mercat**:
- **NO cal predir el preu ni el $\text{CO}_2$:** El diccionari `obs` inclou directament els vectors **`preus_properes_24h`** i **`co2_properes_24h`** amb els valors oficials previstos per a les 24 hores següents.
- **SÍ hem de predir:**
  1. **Demanda elèctrica del campus ($P_{\text{consum}}$):** Predicció a 24 hores vista a partir de l'històric del comptador fiscal (`contador.csv`) i les últimes telemetries (`noves_dades_5min`).
  2. **Generació fotovoltaica ($P_{\text{solar}}$):** Predicció a 24 hores vista a partir de la telemetria dels inversors (`inversor.csv`) i de l'estació meteorològica (`meteo.csv`, irradiància i temperatura).
  * *Estratègia simplificada:* Es pot predir directament la **demanda neta** ($P_{\text{net}} = P_{\text{consum}} - P_{\text{solar}}$) per reduir la complexitat a un sol model predictiu.

---

### 3. Quins tipus d'anàlisi hem de fer?

1. **Anàlisi Exploratòria de Dades (EDA):**
   * Agregació temporal de les sèries de 5 minuts a resolució horària (`resample('1h').mean()`).
   * Identificació dels patrons diaris i setmanals del campus (diferència entre dies feiners, caps de setmana i estacions).
   * Anàlisi de correlació entre la irradiància solar ($\text{W}/\text{m}^2$) i la producció elèctrica.
   * Estudi de la covariància entre el preu PVPC i el factor d'emissió de $\text{CO}_2$ per determinar quines hores són simultàniament barates i netes.
2. **Modelització Predictiva (Machine Learning):**
   * Treballar amb models de regressió lleugers com **`LightGBM`**, **`XGBoost`** o **`RandomForest`** (preinstal·lats al servidor).
   * Crear variables d'entorn temporal (hora del dia, dia de la setmana, mes, variables *lagged*) per predir la corba de consum i generació solar.
3. **Optimització Prescriptiva (Model Predictive Control - MPC):**
   * Resolució d'un problema d'**Optimització Lineal (LP)** a cada pas temporal utilitzant `scipy.optimize.linprog`.
   * Formulació de les restriccions d'estat de càrrega tenint en compte el rendiment de càrrega i descàrrega ($\eta_c = \eta_d \approx 94{,}87\%$).

---

### 4. Com ho programem? (Full de ruta per a 24 hores)

| Franja Temporal | Objectiu i Tasques Clau | Lliurables / Producte |
| :--- | :--- | :--- |
| **Hores 0 – 3** | **EDA, Neteja i Evaluador Local**<br>• Carregar i agrupar dades horàries.<br>• Crear un script local de backtesting (`evaluator.py`) per calcular l'Score exacte.<br>• Crear un agent d'heurística simple (regles fixes) i fer un primer lliurament de prova. | Base de codi funcional + baseline submés |
| **Hores 3 – 8** | **Enginyeria de Característiques i Predicció ML**<br>• Generar *features* temporals i estacionals.<br>• Entrenar model LightGBM/XGBoost per predir $P_{\text{net}}$ a 24h vista.<br>• Guardar el model serialitzat en `model.pkl` amb `joblib`. | Models predictius entrenats i serialitzats |
| **Hores 8 – 16** | **Algorisme d'Optimització (MPC / Programació Lineal)**<br>• Formular la funció de cost combinada ($0{,}70 \cdot \text{CO}_2 + 0{,}30 \cdot \text{Preu}$).<br>• Resoldre l'optimització de les 24h futures amb `scipy.optimize` a cada crida de `act(obs)`.<br>• Executar l'acció $P_t$ de la primera hora i avançar la finestra. | Agent basat en MPC fully funcional |
| **Hores 16 – 20** | **Filtre Anti-Infracció i Post-Processament**<br>• Implementar un retallat (*clipping*) de seguretat estricte al final de `act(obs)` que garanteixi $0 \le \text{SOC}_{t+1} \le 2000$ i $-500 \le P_t \le 500$.<br>• Assegurar zero infraccions en tot el conjunt de test. | Agent robust sense penalitzacions |
| **Hores 20 – 24** | **Backtesting Final i Lliurament Definitiu**<br>• Executar simulacions completes sobre totes les setmanes d'entrenament.<br>• Ajustar hiperparàmetres i empacar el `submission.zip` final. | `submission.zip` final enviat |