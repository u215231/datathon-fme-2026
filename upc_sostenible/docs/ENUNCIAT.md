# Repte UPC Sostenible: Optimització de la Bateria del Campus
## Datathon 2026 — Transició Energètica i Descarbonització

### Context i Organització: UPC Sostenible

Aquest repte està promogut per **UPC Sostenible**, l'organització de la Universitat Politècnica de Catalunya responsable de coordinar la transició energètica, el pla d'acció climàtica i la gestió ambiental dels campus universitaris. UPC Sostenible treballa activament en la monitorització de consums a temps real, la instal·lació d'energia solar fotovoltaica i la reducció contínua de la petjada de carboni de la comunitat universitària.

### Descripció del Problema

El campus universitari compta amb una planta solar fotovoltaica i una corba de demanda elèctrica fluctuant que abasteix aules, laboratoris, servidors i instal·lacions de climatització. En el marc del seu pla de descarbonització, **UPC Sostenible** analitza la incorporació d'una **bateria industrial de 2.000 kWh (2 MWh) i 500 kW de potència**.

El repte consisteix a dissenyar un algorisme de control (`BatteryAgent`) capaç de programar, en intervals horaris, la consigna de potència de càrrega i descàrrega de la bateria. L'algorisme ha d'operar de forma seqüencial amb la informació disponible a temps real, amb dos objectius estratègics definits per UPC Sostenible:
1. **Minimització d'emissions (70% de la puntuació):** Reduir la petjada de $\text{CO}_2$ evitant consumir energia de la xarxa en les hores en què el mix elèctric peninsular és més contaminant.
2. **Eficiència econòmica (30% de la puntuació):** Reduir la factura elèctrica del campus aprofitant les hores amb preus més baixos al mercat regulat (PVPC).

---

### Especificacions Físiques de la Bateria

El sistema simulat correspon a una bateria industrial d'ions de liti amb els següents paràmetres tècnics:

* **Capacitat nominal:** $E_{\text{nom}} = 2.000\text{ kWh}\quad (2\text{ MWh})$.
* **Estat de càrrega permès ($\text{SOC}$):** $0{,}0 \le \text{SOC} \le 1{,}0\quad (0\text{ a }2.000\text{ kWh})$.
* **Potència màxima d'inversor:** $P_{\text{max}} = 500\text{ kW}$ tant per a injecció (càrrega, $P > 0$) com per a extracció (descàrrega, $P < 0$).
* **Rendiment de cicle complet (*Round-Trip Efficiency*):** $\eta = 90\%$.
  * Rendiment de càrrega: $\eta_c = \sqrt{\eta} \approx 94{,}87\%$.
  * Rendiment de descàrrega: $\eta_d = \sqrt{\eta} \approx 94{,}87\%$.
* **Estat de càrrega inicial ($\text{SOC}_0$):** $50\%$ de la capacitat nominal ($1.000\text{ kWh}$) a l'inici de cada període d'avaluació.
* **Resolució temporal de control:** $\Delta t = 1\text{ hora}$.

#### Dinàmica de l'Estat de Càrrega

Per a una consigna de potència $P_t$ a l'hora $t$:

$$\text{Si } P_t \ge 0 \text{ (Càrrega):}\quad \text{SOC}_{t+1} = \text{SOC}_t + P_t \cdot \Delta t \cdot \eta_c$$

$$\text{Si } P_t < 0 \text{ (Descàrrega):}\quad \text{SOC}_{t+1} = \text{SOC}_t + \frac{P_t \cdot \Delta t}{\eta_d}$$

Qualsevol consigna que vulneri els límits de potència $[-500, +500]\text{ kW}$ o que provoqui una saturació de capacitat fora de l'interval $[0, 2.000]\text{ kWh}$ és acotada automàticament pel simulador física i registra una penalització per infracció tècnica.

#### Balanç de Potència en el Punt de Connexió (PCC)

A cada hora $t$, la potència neta intercanviada amb la xarxa de distribució externa ve donada per:

$$P_{\text{xarxa}, t} = P_{\text{consum}, t} - P_{\text{solar}, t} + P_{\text{bateria}, t}$$

* Si $P_{\text{xarxa}, t} > 0$: El campus importa electricitat de la xarxa peninsular. S'aplica el preu horari del mercat regulat (PVPC) i s'assigna el factor d'emissió marginal horari de $\text{CO}_2$ del sistema elèctric peninsular.
* Si $P_{\text{xarxa}, t} \le 0$: La demanda queda totalment satisfeta per la generació fotovoltaica local i el suport de la bateria. En el model actual no es remunera l'energia excedentària abocada a la xarxa (preu d'exportació nul).

---

### Dades Disponibles per a l'Entrenament

El conjunt d'entrenament (`data/train/`) recull dades horàries i cinc-minutals corresponents a un any complet (de setembre de 2025 a setembre de 2026), excloent exactament els darrers 7 dies de cada mes natural, que queden reservats per a la fase d'avaluació cega.

El conjunt està compost per 6 arxius CSV:

1. **`contador.csv`**: Registre del comptador fiscal del campus (resolució 5 minuts). Inclou potència activa importada i exportada, tensions, corrents i potència reactiva.
2. **`inversor.csv`**: Telemetria dels 3 inversors fotovoltaics del campus (resolució 5 minuts). Inclou potències actives AC/DC, corrents per string i temperatura dels equips.
3. **`meteo.csv`**: Registre de l'estació meteorològica instal·lada al terrat del campus (resolució 5 minuts). Mesura irradiància global solar ($\text{W}/\text{m}^2$), temperatura ambient, temperatura de mòdul i velocitat del vent.
4. **`entrades_salides.csv`**: Senyals digitals i relés d'estat de càrregues industrials del campus.
5. **`precio_pvpc.csv`**: Preu voluntari per al petit consumidor (PVPC) oficial publicat per Red Eléctrica de España / OMIE en format horari (€/kWh).
6. **`co2_red.csv`**: Intensitat horària d'emissions de gasos d'efecte hivernacle del mix elèctric peninsular a temps real (kg $\text{CO}_2$/kWh), obtinguda de l'API de Red Eléctrica de España.

---

### Protocol d'Avaluació i Simulació Seqüencial

L'avaluació es realitza sobre el conjunt de test ocult (`data/test_hidden/`), que comprèn 12 setmanes distribuïdes homogèniament al llarg de l'any (exactament els últims 7 dies de cada mes: 2.016 hores en total).

El procés d'execució és estrictament seqüencial per garantir l'absència de filtració d'informació futura (*data leakage*). A cada pas temporal $t$, el mètode `act(obs)` de l'agent rep un diccionari amb les següents dades:

```python
obs = {
    "timestamp": Timestamp,          # Data i hora de la decisió
    "hour": int,                     # Hora del dia (0 a 23)
    "day_of_week": int,              # Dia de la setmana (0 = dilluns, 6 = diumenge)
    "soc_kwh": float,                # Energia emmagatzemada actual (kWh)
    "soc_pct": float,                # Estat de càrrega relatiu [0.0, 1.0]
    "preu_actual": float,            # Preu PVPC de l'hora actual (€/kWh)
    "co2_actual": float,             # Intensitat d'emissió de CO2 d'aquesta hora (kg/kWh)
    "preus_properes_24h": list,      # Vector de preus de les properes 24 hores (mercat diari)
    "co2_properes_24h": list,        # Vector d'intensitat de CO2 previst per a les 24 hores següents
    "noves_dades_5min": {            # Telemetria mesurada en la darrera hora t-1 -> t
        "ultim_consum_kw": float,
        "ultima_solar_kw": float
    }
}
```

L'agent ha de retornar un valor en coma flotant que representi la potència consignada $P_t$ en kW:
* $P_t > 0$: Consigna de càrrega (fins a $+500{,}0\text{ kW}$).
* $P_t < 0$: Consigna de descàrrega (fins a $-500{,}0\text{ kW}$).
* $P_t = 0$: Bateria en repòs ($0{,}0\text{ kW}$).

---

### Funció Objectiu i Criteri de Puntuació

La solució de cada participant es compara de forma directa contra l'escenari base del campus operant sense sistema d'emmagatzematge (*Baseline*):

#### 1. Reducció d'Emissions de $\text{CO}_2$ (Pes: 70%)
$$\Delta\text{CO}_2(\%) = \frac{\text{Emissions}_{\text{baseline}} - \text{Emissions}_{\text{agent}}}{\text{Emissions}_{\text{baseline}}} \times 100$$

#### 2. Reducció del Cost Econòmic d'Importació (Pes: 30%)
$$\Delta\text{Cost}(\%) = \frac{\text{Cost}_{\text{baseline}} - \text{Cost}_{\text{agent}}}{\text{Cost}_{\text{baseline}}} \times 100$$

#### 3. Puntuació Global Oficial (*Score*)
$$\text{Score} = \max\Big(0,\; 0{,}70 \cdot \Delta\text{CO}_2(\%) + 0{,}30 \cdot \Delta\text{Cost}(\%) - 1{,}00 \cdot \text{Infraccions}\Big)$$

On les penalitzacions resten directament **$1{,}00$ punts oficials per cada infracció física** registrada pel simulador (consigna que superi el límit de potència de l'inversor de $\pm 500\text{ kW}$ o que intenti carregar/descarregar la bateria fora del rang de capacitat de $0$ a $2.000\text{ kWh}$).

---

### Gestió de la Memòria Històrica i Dades del Passat

Moltes estratègies avançades d'optimització necessiten conèixer què ha passat en les hores o dies anteriors. L'arquitectura del repte permet fer-ho de dues maneres complementàries:

#### 1. Dades històriques durant la simulació (Memòria d'estat a `self`)
Atès que `BatteryAgent` és una classe de Python persistent durant tota la simulació, podeu emmagatzemar qualsevol observació passada dins d'atributs de l'objecte (per exemple, `self.historial`):

```python
class BatteryAgent:
    def __init__(self):
        # Estructura de dades per acumular el registre històric
        self.historial = []

    def act(self, obs: dict) -> float:
        # Registrem l'estat d'aquesta hora per a consultes futures
        self.historial.append({
            "hora": obs["hour"],
            "preu": obs["preu_actual"],
            "co2": obs["co2_actual"],
            "consum": obs["noves_dades_5min"]["ultim_consum_kw"]
        })

        # Exemple: Consultar el consum de fa 24 hores (ahir a la mateixa hora)
        if len(self.historial) >= 24:
            consum_ahir = self.historial[-24]["consum"]
            # Utilitzar el consum d'ahir per ajustar la decisió actual...
```

#### 2. Dades de mesos anteriors d'entrenament (`data/train/`)
Si voleu incorporar coneixement extret del conjunt d'entrenament (com ara models de Machine Learning, patrons estacionals per mes o taules de consum mitjà per dia de la setmana):
* Entreneu el model o genereu les taules de paràmetres prèviament al vostre ordinador.
* Deseu el model amb `joblib.dump(model, "model.pkl")` o en format `JSON` / `pickle`.
* Incloeu el fitxer `.pkl` dins de l'arxiu `submission.zip`.
* Carregueu-lo a l'inici de la simulació dins del mètode `__init__()` mitjançant `joblib.load("model.pkl")`.

---

### Requisits i Normativa del Lliurament

El lliurament es formalitza a través de la plataforma web mitjançant la càrrega d'un arxiu comprimit `submission.zip` (o directament l'arxiu `agent.py` si no s'utilitzen models binaris).

L'arxiu comprimit ha de contenir:
1. **`agent.py`**: Codi font que implementi obligatòriament la classe `BatteryAgent` amb el mètode `act(obs)`.
2. **Fitxers auxiliars de models serialitzats** (per exemple, `model.pkl` utilitzant `joblib` o `pickle`), en cas que la solució utilitzi models predictius preentrenats.
3. **Mòduls de codi auxiliars** (com ara fitxers `.py` locals o arxius de configuració `.json`).

---

### Entorn d'Execució i Política de Biblioteques

Per garantir la reproducibilitat, la seguretat i la igualtat de condicions entre tots els equips, l'avaluador del servidor s'executa sobre un entorn Python 3 controlat amb les eines de computació científica i aprenentatge automàtic més utilitzades.

#### 1. Biblioteques Permeses (Preinstal·lades al Servidor)

Totes les solucions poden importar i utilitzar lliurement les següents biblioteques:

| Biblioteca | Categoria / Descripció | Ús Recomanat |
| :--- | :--- | :--- |
| **`numpy`** | Àlgebra lineal i arrays numèrics | Operacions vectoritzades, càlculs matricials i d'eficiència. |
| **`pandas`** | Anàlisi i manipulació de sèries temporals | Gestió de dataframes, agrupacions i agregacions horàries. |
| **`scipy`** | Computació científica i optimització numèrica | Algoritmes d'optimització, ajust de corbes i funcions matemàtiques. |
| **`scikit-learn`** | Machine Learning supervisat i no supervisat | Inferència amb models de regressió (arbres, Random Forest, etc.). |
| **`joblib`** | Serialització eficient d'estructures de dades | Càrrega offline ràpida de fitxers `.pkl` binaris a `__init__()`. |
| **`xgboost`** | Models de Gradient Boosting per a dades tabulars | Inferència de consum i radiació amb models potenciats per gradients. |
| **`lightgbm`** | Algoritmes lleugers de Gradient Boosting | Predicció d'alta velocitat d'execució en inferència horària. |
| **`math`, `random`** | Càlculs matemàtics i generadors | Truncaments, arrodoniments, lògica probabilística. |
| **`datetime`** | Gestió de calendaris i marques temporals | Processament d'hores, dies de la setmana i estacionalitat. |
| **`collections`, `itertools`** | Estructures de dades optimitzades | Cues circulars (`deque`), comptadors i iteradors d'alt rendiment. |
| **`json`, `pathlib`** | Gestió de fitxers locals i estructures | Lectura d'arxius de paràmetres locals continguts al `.zip`. |
| **`typing`, `dataclasses`** | Anotacions de tipus i models de dades | Estructuració neta i mantenible del codi de l'agent. |

> **Nota:** Totes les biblioteques de la biblioteca estàndard de Python dedicades a lògica de computació (`itertools`, `functools`, `heapq`, `bisect`, `re`, `copy`, `pickle`) són plenament admeses.

---

#### 2. Biblioteques i Crides Estrictament Prohibides

Abans d'executar qualsevol arxiu lliurat, el servidor analitza l'arbre sintàctic abstracte (**AST**) del codi. Si es detecta qualsevol de les biblioteques o funcions següents, **la solució serà rebutjada automàticament** amb una notificació de seguretat:

| Tipus de Restricció | Mòduls o Funcions Vetats | Motiu Tècnic del Bloqueig |
| :--- | :--- | :--- |
| **Accés a xarxa i connexions remotes** | `requests`, `urllib`, `socket`, `http`, `ftplib`, `aiohttp`, `paramiko`, `telnetlib` | **Integritat:** Les avaluacions han de ser totalment autosuficients i no poden consultar APIs externes o filtrar dades secretes. |
| **Comandes de terminal i subprocessos** | `os.system()`, `os.popen()`, mòdul `subprocess`, `sys.exit()`, `shutil.rmtree()`, `pty`, `posix` | **Aïllament de la infraestructura:** Cap agent pot alterar els processos del servidor, crear subprocessos paral·lels ni apagar la màquina. |
| **Execució dinàmica de codi no verificat** | `eval()`, `exec()` sobre cadenes de text no segures | **Validació estàtica:** El codi s'ha d'interpretar de forma estructurada i auditable pel jurat de la UPC. |
| **Lectura de dades de test secretes** | Intents d'accedir a rutes externes com `data/test_hidden` o rutes absolutes del servidor | **Antifrau:** El simulador s'executa en un directori temporal aïllat; l'agent només ha de rebre l'estat a través del diccionari `obs`. |

---

#### 3. Com resoldre necessitats tècniques habituals de forma autoritzada

* **Com utilitzar la informació dels dies o mesos anteriors?**
  Guardant les observacions passades dins d'un atribut de la classe `BatteryAgent` (com ara `self.historial = []`) o carregant models serialitzats a `__init__()`. No cal ni està permès fer crides a fitxers del sistema ni xarxa.
* **Com utilitzar models entrenats a l'ordinador local?**
  Serialitzeu el model al vostre equip amb `joblib.dump(model, "model_bateria.pkl")`, incloeu aquest fitxer a l'arrel de `submission.zip` i carregueu-lo a `__init__()` mitjançant `joblib.load(Path(__file__).parent / "model_bateria.pkl")`.
* **Com llegir taules de configuració o matrius d'hiperparàmetres?**
  Desant un fitxer `parametres.json` dins del `.zip` i llegint-lo amb `json.load()` o com una matriu de `numpy`.

---

#### 4. Normativa Operativa del Servidor

Per garantir la concurrència i estabilitat de la plataforma per a tots els equips:
* **Límit de lliuraments:** Cada equip disposa d'un màxim de **10 lliuraments per franja horària** (fins a 30 lliuraments en total al llarg del Datathon):
  1. **Torn 1 (Dissabte diürn):** 10 lliuraments fins a les 21:00h.
  2. **Torn 2 (Dissabte nit):** 10 lliuraments des de les 21:00h fins a Diumenge a les 08:00h.
  3. **Torn 3 (Diumenge diürn):** 10 lliuraments des de les 08:00h fins al tancament oficial del repte.
* **Temps límit d'execució (*Timeout*):** Cada simulació té un temps màxim autoritzat d'**1 minut (60 segons)**. Els processos que superin aquest llindar seran cancel·lats automàticament per seguretat.
* **Mida màxima d'arxiu:** El fitxer comprimit de tramesa no pot superar els **25 MB**.
* **Identificació i PIN de seguretat:** En el primer lliurament, cada equip estableix un PIN secret (mínim 4 caràcters) i els noms i cognoms dels integrants. Els lliuraments posteriors sota el mateix nom requeriran aquest PIN per evitar suplantacions d'identitat o esgotament indegut d'intents per part de tercers.
* **Trameses fallides:** Els intents que no s'executin satisfactòriament per errors de sintaxi o manca de definició de classes a l'arxiu no consumeixen la quota d'intents de l'equip.
