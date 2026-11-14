# Guia Tècnica de Variables i Telemetria dels Sensors
## Repte UPC Sostenible — Datathon 2026

Aquest document detalla l'estructura, el significat físic, les unitats de mesura i les consideracions d'enginyeria de dades per a cadascun dels fitxers disponibles al directori `data/train/`.

Tots els fitxers contenen la columna temporal **`Fecha`** (format `AAAA-MM-DD HH:MM:SS`), que constitueix la clau primària d'alineació per a totes les sèries temporals.

---

### 1. Comptador Fiscal General (`contador.csv`)

Aquest fitxer prové de la unitat de mesura fiscal instal·lada en el centre de transformació del campus, en el punt de connexió comú (PCC) amb la xarxa elèctrica de distribució. La resolució temporal és de 5 minuts (288 registres diaris).

#### Variables Clau per al Repte

| Variable | Unitat | Descripció Tècnica |
|---|---|---|
| `Fecha` | - | Marca de temps oficial (UTC+1 / UTC+2 segons horari d'estiu). |
| `Contador - POTENCIA ACTIVA EXPORTADA (kW)` | kW | Potència activa instantània amb conveni de signes del comptador. Els valors negatius indiquen **importació d'energia de la xarxa** (consum del campus superior a la generació solar). Per obtenir el consum en positiu: $P_{\text{consum}} = -\text{Potència Exportada}$. |
| `Meter 1 - ENERGIA ACTIVA IMPORTADA (kWh)` | kWh | Energia activa acumulada absorbida des de la xarxa de distribució. |
| `Meter 1 - ENERGIA ACTIVA EXPORTADA (kWh)` | kWh | Energia activa acumulada abocada a la xarxa (habitualment nul·la o propera a zero, ja que el campus és consumidor net continu). |
| `Contador - POTENCIA REACTIVA (kVAr)` | kVAr | Potència reactiva instantània total en el punt de mesura. |
| `Contador - FACTOR DE POTENCIA` | - | Factor de potència instantani ($\cos \varphi$), oscil·lant entre 0 i 1. Reflecteix l'eficiència del transport elèctric intern. |
| `Contador - TENSION AC FASE 1-N (V)` | V | Tensió eficaç simple de la fase 1 respecte a neutre (nominal ~230 V). |
| `Contador - TENSION AC FASE 2-N (V)` | V | Tensió eficaç simple de la fase 2 respecte a neutre. |
| `Contador - TENSION AC FASE 3-N (V)` | V | Tensió eficaç simple de la fase 3 respecte a neutre. |
| `Contador - CORRIENTE AC FASE 1 (A)` | A | Corrent eficaç circulant per la línia de la fase 1. |
| `Contador - CORRIENTE AC FASE 2 (A)` | A | Corrent eficaç circulant per la línia de la fase 2. |
| `Contador - CORRIENTE AC FASE 3 (A)` | A | Corrent eficaç circulant per la línia de la fase 3. |

#### Metadades de Comunicació i Diagnòstic
* `ESTADO COM` i `CALIDAD COM`: Indicadors de fiabilitat del canal de telemetria Modbus/RTU. Valors de qualitat inferiors a 100 poden correspondre a incidències de comunicació puntuals.

---

### 2. Inversors Fotovoltaics (`inversor.csv`)

Recull la telemetria dels 3 inversors solars trifàsics de la planta fotovoltaica del campus. La freqüència d'adquisició és de 5 minuts.

#### Càlcul de la Potència Fotovoltaica Total
Per determinar la generació solar total instantània del campus, cal afegir les potències actives de sortida AC dels tres equips:

$$P_{\text{solar, total}} = P_{\text{inv, 1}} + P_{\text{inv, 2}} + P_{\text{inv, 3}}$$

On cada $P_{\text{inv, } i}$ correspon a la columna respectiva de potència activa (`Inversor i - POTENCIA ACTIVA (kW)`).

#### Variables Principals per Equip ($i \in \{1, 2, 3\}$)

| Variable | Unitat | Descripció Tècnica |
|---|---|---|
| `Inversor i - POTENCIA ACTIVA (kW)` | kW | Potència activa AC total injectada pel conjunt de les 3 fases de l'inversor. |
| `Inversor i - POTENCIA ACTIVA FASE 1/2/3 (kW)` | kW | Desglossament de la potència activa generada per cadascuna de les fases AC. |
| `Inversor i - ENERGIA ACTIVA (kWh)` | kWh | Comptador acumulador d'energia produïda històricament per l'equip. |
| `Inversor i - POTENCIA DC (kW)` | kW | Potència total de corrent continu generada pel camp fotovoltaic a l'entrada de l'inversor. La relació $P_{\text{AC}} / P_{\text{DC}}$ proporciona el rendiment instantani de conversió de l'inversor. |
| `Inversor i - POTENCIA DC IN 01..06 (kW)` | kW | Potència de cadascun dels canals dels seguidors de punt de màxima potència (MPPT). |
| `Inversor i - TENSION DC (V)` | V | Tensió del bus de contínua a l'entrada de l'equip. |
| `Inversor i - TEMPERATURA INT (degC)` | °C | Temperatura interna de l'electrònica de potència de l'inversor. Temperatures superiors a 65 °C poden provocar retallada de potència (*derating*) per protecció tèrmica. |
| `Inversor i - RESISTENCIA AISLAMIENTO (Ohm)` | $\Omega$ | Paràmetre de seguretat elèctrica de l'aïllament del camp fotovoltaic respecte a terra. |

---

### 3. Estació Meteorològica (`meteo.csv`)

L'estació meteorològica està ubicada al terrat d'un dels edificis principals del campus, en el mateix pla que les estructures dels panells solars. Aporta les variables exògenes necessàries per als models predictius de generació fotovoltaica i de demanda tèrmica de climatització. Resolució: 5 minuts.

| Variable | Unitat | Descripció Tècnica |
|---|---|---|
| `IRRADIANCIA` (i canals 1 i 2) | $\text{W}/\text{m}^2$ | Irradiància solar global incident sobre el pla dels mòduls mesurada per piranòmetre calibrat. És la variable física amb major correlació amb la generació elèctrica fotovoltaica. |
| `TEMPERATURA AMBIENTE` | °C | Temperatura de l'aire ambient exterior. Determina en gran mesura la corba de càrrega de climatització (HVAC) del campus a l'estiu (refrigeració) i a l'hivern (bombes de calor). |
| `TEMPERATURA PANEL` | °C | Temperatura superficial dels mòduls de silici. Com a referència física, el coeficient de temperatura típic dels panells fotovoltaics és de $-0{,}4\%/^\circ\text{C}$ sobre la potència màxima per cada grau per sobre de 25 °C. |
| `VELOCIDAD VIENTO` | $\text{m}/\text{s}$ | Velocitat del vent mesurada per anemòmetre. Incideix directament en la refrigeració convectiva dels panells. |
| `HORAS SOL PICO` | h | Integració d'hores de sol pic acumulades al llarg de la jornada (energia radiant acumulada normalitzada a $1.000\text{ W}/\text{m}^2$). |

---

### 4. Mòdul d'Entrades i Sortides Digitals (`entrades_salides.csv`)

Registra els canals binaris procedents d'un autòmat d'adquisició de senyals industrials (mòdul Moxa IoLogik). Aquests senyals indiquen l'estat operatiu (marxa/aturada, 1/0) de determinades càrregues elèctriques auxiliars del campus (bombes, compressors o ventilació forçada).

---

### 5. Preu del Mercat Elèctric Regulat (`precio_pvpc.csv`)

Dades oficials del mercat elèctric peninsular publicades per Red Eléctrica de España / OMIE. Freqüència: **horària (1 hora)**.

| Variable | Unitat | Descripció Tècnica |
|---|---|---|
| `Fecha` | - | Inici de l'interval horari corresponent. |
| `precio_eur_per_kwh` | €/kWh | Preu voluntari per al petit consumidor (PVPC). Reflecteix el cost marginal de l'energia al mercat majorista diari i intradiari, afegint-hi els peatges d'accés, càrrecs del sistema i costos d'ajust regulats. |

---

### 6. Factor d'Emissió de Carboni de la Xarxa (`co2_red.csv`)

Dades oficials de la intensitat d'emissions del mix de generació peninsular a temps real, obtingudes de la plataforma informativa de Red Eléctrica de España. Freqüència: **horària (1 hora)**.

| Variable | Unitat | Descripció Tècnica |
|---|---|---|
| `Fecha` | - | Inici de l'interval horari corresponent. |
| `co2_kg_per_kwh` | $\text{kg }\text{CO}_2/\text{kWh}$ | Factor d'emissió del mix de generació elèctrica peninsular per a cada hora. Varia dinàmicament en funció de la penetració de fonts renovables (hidràulica, eòlica, solar) i la participació de centrals de cicle combinat de gas natural o cogeneració. |

---

### Pautes per al Preprocessament i Alineació

1. **Re-mostreig temporal (*Resampling*):** Les sèries de 5 minuts (`contador.csv`, `inversor.csv`, `meteo.csv`) han de ser agregades a freqüència horària mitjançant el càlcul de la mitjana temporal de cada interval (`resample("1h").mean()`) per ser coherents amb la dinàmica de decisió de la bateria i els mercats d'electricitat.
2. **Filtratge de valors anòmals:** Es recomana aplicar un tall de coherència física sobre la potència activa exportada del comptador, limitant valors aberrants superiors a $5.000\text{ kW}$ o inferiors a $0\text{ kW}$ un cop canviat el signe.
3. **Imputació de buits:** En intervals amb pèrdua de comunicació puntual, es recomana aplicar interpolació lineal per a períodes curts ($\le 15\text{ min}$) o valors mitjans estacionals segons l'hora del dia.
