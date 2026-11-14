# Enunciat Oficial per als Participants (Format LaTeX)

Aquest document conté el codi font complet en LaTeX de l'**enunciat oficial del repte per als participants** de la Datathon 2026. Està redactat amb un estil d'enginyeria rigorós, precís i clar, sense retòrica innecessària, explicant pas a pas la formulació física de la bateria, el balanç elèctric, la interfície de programació de l'agent, el format de les dades d'entrenament, el sistema de puntuació i els requisits tècnics de lliurament.

Per compilar-lo a PDF, podeu copiar el codi següent directament a Overleaf, TeXShop o compilar-lo amb `pdflatex` o `xelatex`.

```latex
\documentclass[11pt,a4paper]{article}

% --- Paquets bàsics i tipografia ---
\usepackage[catalan]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{textcomp}
\usepackage{eurosym}

% --- Geometria de la pàgina ---
\usepackage[top=2.2cm, bottom=2.2cm, left=2.3cm, right=2.3cm]{geometry}

% --- Matemàtiques ---
\usepackage{amsmath,amssymb,amsfonts}

% --- Taules ---
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}

% --- Colors corporatius UPC ---
\usepackage{xcolor}
\definecolor{upcblue}{RGB}{0,102,179}      % Blau institucional UPC
\definecolor{upcdark}{RGB}{20,40,65}       % Blau fosc per títols
\definecolor{upcgreen}{RGB}{46,125,50}     % Verd
\definecolor{codebg}{RGB}{247,249,251}     % Fons de codi
\definecolor{bordergray}{RGB}{210,215,220} % Vores

% --- Caixes destacades ---
\usepackage[framemethod=TikZ]{mdframed}
\mdfdefinestyle{notebox}{%
    linecolor=upcblue,
    outerlinewidth=1pt,
    roundcorner=3pt,
    innertopmargin=6pt,
    innerbottommargin=6pt,
    innerrightmargin=10pt,
    innerleftmargin=10pt,
    backgroundcolor=upcblue!4
}

\mdfdefinestyle{warnbox}{%
    linecolor=red!70!black,
    outerlinewidth=1pt,
    roundcorner=3pt,
    innertopmargin=6pt,
    innerbottommargin=6pt,
    innerrightmargin=10pt,
    innerleftmargin=10pt,
    backgroundcolor=red!4
}

% --- Entorn de codi font ---
\usepackage{listings}
\lstset{
    language=Python,
    basicstyle=\ttfamily\footnotesize,
    keywordstyle=\bfseries\color{upcblue},
    commentstyle=\itshape\color{gray},
    stringstyle=\color{upcgreen},
    backgroundcolor=\color{codebg},
    frame=single,
    rulecolor=\color{bordergray},
    breaklines=true,
    showstringspaces=false,
    tabsize=4
}

% --- Format de títols ---
\usepackage{titlesec}
\titleformat{\section}{\color{upcdark}\normalfont\large\bfseries}{\thesection.}{0.6em}{}[\titlerule]
\titleformat{\subsection}{\color{upcdark}\normalfont\normalsize\bfseries}{\thesubsection.}{0.5em}{}
\titleformat{\subsubsection}{\color{upcdark}\normalfont\small\bfseries}{\thesubsubsection.}{0.4em}{}

% --- Hipervincles ---
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=upcblue,
    urlcolor=upcblue,
    pdftitle={Enunciat Oficial - Repte UPC Sostenible Datathon 2026},
    pdfauthor={UPC Sostenible - Universitat Politècnica de Catalunya}
}

% ==============================================================================
% ENCAPÇALAMENT I TÍTOL
% ==============================================================================
\title{
    \vspace{-1.2cm}
    \textbf{\large Datathon UPC 2026 --- Transició Energètica i Sostenibilitat}\\[0.2em]
    \textbf{\Large Repte UPC Sostenible: Optimització de la Bateria del Campus}\\[0.3em]
    \normalsize Plec Tècnic i Especificacions Oficials per als Equips Participants
}
\author{\textbf{UPC Sostenible} --- Universitat Politècnica de Catalunya}
\date{Durada de la competició: 24 hores}

% ==============================================================================
% CONTINGUT PRINCIPAL
% ==============================================================================
\begin{document}

\maketitle

\begin{mdframed}[style=notebox]
\textbf{Resum Operatiu del Repte:}
Heu de programar un agent intel·ligent en Python (\texttt{BatteryAgent}) capaç de decidir la consigna horària de potència de càrrega o descàrrega d'una \textbf{bateria industrial de 2.000~kWh i 500~kW} instal·lada al campus universitari. L'algorisme rebrà la informació de forma estrictament seqüencial hora a hora i ha de minimitzar simultàniament la petjada de $\text{CO}_2$ de la xarxa elèctrica externa (70\% del pes) i el cost econòmic de l'energia importada (30\% del pes), evitant qualsevol violació dels límits físics de la bateria.
\end{mdframed}

% ------------------------------------------------------------------------------
\section{Context i Descripció del Problema}
% ------------------------------------------------------------------------------

El campus universitari disposa d'una instal·lació solar fotovoltaica en coberta i d'una demanda elèctrica agregada (aules, laboratoris, climatització i centres de càlcul) que varia contínuament al llarg del dia i de les estacions de l'any.

Dins del Pla d'Acció Climàtica de la UPC, s'estudia la integració d'un sistema d'emmagatzematge elèctric estacionari basat en una bateria industrial. L'objectiu no és només emmagatzemar l'energia solar excedentària, sinó també aprofitar la flexibilitat de la bateria per:
\begin{enumerate}
    \item Carregar de la xarxa en les hores en què el mix elèctric peninsular presenta una intensitat mínima d'emissions de $\text{CO}_2$ i/o preus econòmics molt baixos.
    \item Descarregar per cobrir la demanda del campus en les hores punta, quan l'energia importada és més contaminant i més cara.
\end{enumerate}

% ------------------------------------------------------------------------------
\section{Model Físic i Balanç Elèctric al Punt de Connexió (PCC)}
% ------------------------------------------------------------------------------

\subsection{Paràmetres Físics de la Bateria Industrial}
El sistema simulat correspon a una bateria d'ions de liti de tipus industrial connectada a la xarxa interna del campus a través d'un inversor bidireccional:

\begin{table}[h]
\centering
\small
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{l l X}
\toprule
\textbf{Paràmetre} & \textbf{Valor} & \textbf{Descripció} \\
\midrule
Capacitat energètica útil ($E_{\text{nom}}$) & $2.000\text{ kWh}$ ($2\text{ MWh}$) & Rang operatiu: $\text{SOC}_t \in [0, 2.000]\text{ kWh}$ ($0{,}0 \le \text{SOC}_{\%} \le 1{,}0$). \\
Potència límit de l'inversor ($P_{\max}$) & $\pm 500\text{ kW}$ & Rang de consigna permès: $[-500{,}0, +500{,}0]\text{ kW}$. \\
Rendiment de cicle complet ($\eta$) & $90\%$ & Rendiment global d'anada i tornada (\emph{round-trip efficiency}). \\
Rendiment de càrrega ($\eta_c$) & $\sqrt{0,90} \approx 94{,}87\%$ & Fracció de potència de xarxa que arriba a la bateria. \\
Rendiment de descàrrega ($\eta_d$) & $\sqrt{0,90} \approx 94{,}87\%$ & Fracció d'energia extreta de la bateria útil a la xarxa. \\
Estat de càrrega inicial ($\text{SOC}_0$) & $50\%$ ($1.000\text{ kWh}$) & Condició inicial a l'hora $t = 0$. \\
Interval de control ($\Delta t$) & $1\text{ hora}$ & Resolució de la presa de decisions. \\
\bottomrule
\end{tabularx}
\caption{Especificacions físiques de la bateria industrial.}
\end{table}

\subsection{Dinàmica de l'Estat de Càrrega}
Donada una consigna de potència $P_t$ consignada a l'hora $t$:
\begin{itemize}
    \item \textbf{Càrrega ($P_t \ge 0$):} La bateria absorbeix energia amb pèrdues de càrrega:
    \begin{equation}
        \text{SOC}_{t+1} = \text{SOC}_t + P_t \cdot \Delta t \cdot \eta_c
    \end{equation}
    \item \textbf{Descàrrega ($P_t < 0$):} La bateria injecta energia útil $|P_t|$ a la instal·lació interna del campus, requerint una extracció interna superior degut a les pèrdues:
    \begin{equation}
        \text{SOC}_{t+1} = \text{SOC}_t + \frac{P_t \cdot \Delta t}{\eta_d} \qquad (P_t < 0)
    \end{equation}
\end{itemize}

\subsection{Balanç de Potència al Punt de Connexió Comú (PCC)}
A cada hora $t$, la potència neta intercanviada amb la xarxa exterior és la suma del consum intern del campus, la generació solar fotovoltaica i la consigna de la bateria:
\begin{equation}
    P_{\text{xarxa}, t} = P_{\text{consum}, t} - P_{\text{solar}, t} + P_{\text{bateria}, t}
\end{equation}

\noindent Les conseqüències operatives d'aquest balanç són:
\begin{itemize}
    \item \textbf{Importació de la xarxa ($P_{\text{xarxa}, t} > 0$):} El campus absorbeix electricitat de la xarxa peninsular. S'aplica el cost del mercat regulat (PVPC) i s'assigna la intensitat d'emissió de $\text{CO}_2$ d'aquesta hora:
    \begin{align}
        \text{Cost}_t &= P_{\text{xarxa}, t} \cdot \Delta t \cdot \text{Preu}_t \\
        \text{Emissions}_t &= P_{\text{xarxa}, t} \cdot \Delta t \cdot \text{Factor CO}_{2, t}
    \end{align}
    \item \textbf{Autosuficiència o excedent ($P_{\text{xarxa}, t} \le 0$):} La generació solar combinada amb la bateria cobreix tota la demanda del campus. En el model actual \textbf{no es remunera l'energia abocada a la xarxa} (cost i emissions nuls per a aquestes hores).
\end{itemize}

% ------------------------------------------------------------------------------
\section{Dades Disponibles per a l'Entrenament (\texttt{data/train/})}
% ------------------------------------------------------------------------------

El repositori inclou dades històriques d'un any sencer (de setembre de 2025 a setembre de 2026), restant exclosos els darrers 7 dies de cada mes natural (reservats per a l'avaluació cega del servidor):

\begin{enumerate}
    \item \texttt{contador.csv} (cadència de 5 minuts): Lectures del comptador fiscal general. Inclou la potència activa exportada, reactiva, tensions trifàsiques i corrents.
    \begin{mdframed}[style=notebox]
    \textbf{Càlcul clau del consum del campus:} Segons el conveni del comptador fiscal, la importació d'energia es registra com a valors negatius de potència exportada. Per obtenir el consum net en positiu:
    \begin{equation}
        P_{\text{consum}} = \max\big(0,\; -\text{Potència Activa Exportada}\big)
    \end{equation}
    \end{mdframed}
    \item \texttt{inversor.csv} (cadència de 5 minuts): Telemetria dels tres inversors fotovoltaics del campus. La generació fotovoltaica total és la suma de la potència activa AC dels tres equips:
    \begin{equation}
        P_{\text{solar}} = P_{\text{inv, 1}} + P_{\text{inv, 2}} + P_{\text{inv, 3}}
    \end{equation}
    \item \texttt{meteo.csv} (cadència de 5 minuts): Dades de l'estació meteorològica de coberta (irradiància global en $\text{W}/\text{m}^2$, temperatura de l'aire ambient, temperatura dels panells i velocitat del vent).
    \item \texttt{entrades\_salides.csv} (cadència de 5 minuts): Senyals binaris (0/1) que indiquen l'estat d'activació de maquinària auxiliar del campus (bombes, compressors, ventilació).
    \item \texttt{precio\_pvpc.csv} (cadència horària, 1~h): Preu oficial de l'energia al mercat regulat peninsular en \euro/kWh.
    \item \texttt{co2\_red.csv} (cadència horària, 1~h): Intensitat d'emissió del mix elèctric peninsular a temps real en $\text{kg CO}_2/\text{kWh}$.
\end{enumerate}

\noindent Per alinear les dades de 5 minuts amb l'escala horària del controlador, cal calcular la mitjana aritmètica dels 12 intervals de 5 minuts que conformen cada hora.

% ------------------------------------------------------------------------------
\section{Interfície de Programació de l'Agent (\texttt{agent.py})}
% ------------------------------------------------------------------------------

La vostra solució s'ha d'estructurar en un fitxer anomenat obligatòriament \texttt{agent.py}, el qual ha d'implementar la classe \texttt{BatteryAgent}:

\begin{lstlisting}
class BatteryAgent:
    def __init__(self):
        """Inicialitzacio de l'agent i carrega opcional de models preentrenats."""
        self.historial = []  # Memoria persistent al llarg de la simulacio

    def act(self, obs: dict) -> float:
        """Rep l'estat actual i retorna la consigna de potencia en kW."""
        # Exemple trivial: bateria en repos
        return 0.0
\end{lstlisting}

\subsection{Estructura del Diccionari d'Observació (\texttt{obs})}
A cada hora $t$, el mètode \texttt{act(obs)} rep un diccionari amb els següents camps:

\begin{table}[h]
\centering
\small
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{l l l X}
\toprule
\textbf{Clau del Diccionari} & \textbf{Tipus} & \textbf{Unitats} & \textbf{Descripció Tècnica} \\
\midrule
\texttt{timestamp} & \texttt{Timestamp} & --- & Marca temporal de l'hora de decisió actual. \\
\texttt{hour} & \texttt{int} & h & Hora del dia actual ($0 \le h \le 23$). \\
\texttt{day\_of\_week} & \texttt{int} & --- & Dia de la setmana ($0 = \text{Dilluns}, 6 = \text{Diumenge}$). \\
\texttt{soc\_kwh} & \texttt{float} & kWh & Energia actual emmagatzemada a la bateria. \\
\texttt{soc\_pct} & \texttt{float} & $[0, 1]$ & Estat de càrrega normalitzat ($\text{soc\_kwh} / 2.000$). \\
\texttt{preu\_actual} & \texttt{float} & \euro/kWh & Preu del mercat PVPC per a l'hora actual. \\
\texttt{co2\_actual} & \texttt{float} & $\text{kg}/\text{kWh}$ & Intensitat d'emissions de $\text{CO}_2$ de l'hora actual. \\
\texttt{preus\_properes\_24h} & \texttt{list[float]} & \euro/kWh & Vector de preus coneguts per a les properes 24 hores. \\
\texttt{co2\_properes\_24h} & \texttt{list[float]} & $\text{kg}/\text{kWh}$ & Vector d'emissions previstes per a les 24 hores següents. \\
\texttt{noves\_dades\_5min} & \texttt{dict} & --- & Mesures de la darrera hora ($t-1 \to t$): \\
\quad \texttt{ultim\_consum\_kw} & \texttt{float} & kW & Consum mitjà del campus en l'última hora. \\
\quad \texttt{ultima\_solar\_kw} & \texttt{float} & kW & Producció solar mitjana en l'última hora. \\
\bottomrule
\end{tabularx}
\caption{Descripció dels camps transmesos al diccionari d'observació \texttt{obs}.}
\end{table}

\subsection{Valor de Retorn}
El mètode \texttt{act(obs)} ha de retornar un valor numèric (\texttt{float}):
\begin{itemize}
    \item $P_t > 0$: Consigna de càrrega (fins a $+500{,}0\text{ kW}$).
    \item $P_t < 0$: Consigna de descàrrega (fins a $-500{,}0\text{ kW}$).
    \item $P_t = 0{,}0$: Bateria en repòs.
\end{itemize}

% ------------------------------------------------------------------------------
\section{Funció Objectiu i Sistema de Puntuació}
% ------------------------------------------------------------------------------

El rendiment de l'agent s'avalua sobre el conjunt de test de 2.016 hores, comparant-lo de forma directa amb el comportament del campus sense bateria (\emph{Baseline}):

\subsection{1. Reducció d'Emissions de $\text{CO}_2$ (Pes: 70\%)}
\begin{equation}
    \Delta\text{CO}_2(\%) = \frac{\text{Emissions}_{\text{baseline}} - \text{Emissions}_{\text{agent}}}{\text{Emissions}_{\text{baseline}}} \times 100
\end{equation}

\subsection{2. Reducció del Cost Econòmic d'Importació (Pes: 30\%)}
\begin{equation}
    \Delta\text{Cost}(\%) = \frac{\text{Cost}_{\text{baseline}} - \text{Cost}_{\text{agent}}}{\text{Cost}_{\text{baseline}}} \times 100
\end{equation}

\subsection{3. Puntuació Global Oficial (\emph{Score})}
\begin{equation}
    \text{Score} = \max\Big(0,\; 0{,}70 \cdot \Delta\text{CO}_2(\%) + 0{,}30 \cdot \Delta\text{Cost}(\%) - 1{,}00 \cdot \text{Infraccions}\Big)
\end{equation}

\begin{mdframed}[style=warnbox]
\textbf{Penalització per Infraccions Físiques:}
Cada vegada que la consigna $P_t$ de l'agent intenti superar els límits de l'inversor ($\pm 500\text{ kW}$) o provoqui que la bateria surti del rang físic útil ($0\text{ a }2.000\text{ kWh}$), el simulador comptabilitza una infracció i retalla automàticament la consigna. \textbf{Cada infracció resta directament $1{,}00$ punts de la puntuació final.} Assegureu-vos que el vostre agent respecti els límits del $\text{SOC}$ abans d'emetre la consigna.
\end{mdframed}

% ------------------------------------------------------------------------------
\section{Normativa Tècnica i Condicions del Servidor}
% ------------------------------------------------------------------------------

\subsection{Biblioteques Autoritzades}
L'entorn d'execució compta amb Python 3 i les principals eines de computació científica preinstal·lades:
\begin{itemize}
    \item \texttt{numpy}, \texttt{pandas}, \texttt{scipy}, \texttt{scikit-learn}, \texttt{joblib}, \texttt{xgboost}, \texttt{lightgbm}.
    \item Mòduls estàndard de Python: \texttt{math}, \texttt{random}, \texttt{datetime}, \texttt{collections}, \texttt{itertools}, \texttt{json}, \texttt{pathlib}, \texttt{copy}, \texttt{typing}.
\end{itemize}

\subsection{Inspecció Estàtica de Seguretat (AST)}
Abans de ser executat, el codi és sotmès a una verificació automàtica de l'arbre sintàctic (AST). \textbf{Qualsevol de les següents accions provocarà el rebuig immediat de la solució}:
\begin{itemize}
    \item Connexions de xarxa o consultes a internet (\texttt{requests}, \texttt{urllib}, \texttt{socket}, etc.).
    \item Execució de comandes de terminal o creació de subprocessos (\texttt{os.system}, \texttt{subprocess}, \texttt{sys.exit}).
    \item Execució dinàmica de codi no controlat (\texttt{eval}, \texttt{exec}).
    \item Intents de lectura directa del sistema de fitxers del servidor o accés a les dades secretes de test.
\end{itemize}

\subsection{Límits Operatius}
\begin{itemize}
    \item \textbf{Temps límit d'execució:} Màxim de \textbf{60 segons} per avaluar la simulació de les 2.016 hores completes.
    \item \textbf{Mida màxima del fitxer de lliurament:} \textbf{25 MB}.
    \item \textbf{Límit de lliuraments:} \textbf{10 intents vàlids per equip i dia}.
    \item \textbf{PIN de seguretat:} En el vostre primer enviament, definiu un PIN d'equip (mínim 4 dígits/caràcters) que haureu d'utilitzar en tots els lliuraments posteriors.
\end{itemize}

% ------------------------------------------------------------------------------
\section{Guia de Lliurament i Comprovació Local}
% ------------------------------------------------------------------------------

\subsection{Estructura de l'Arxiu de Lliurament}
Podeu pujar directament l'arxiu \texttt{agent.py} a la pestanya de lliuraments del tauler web. Si la vostra solució depèn de models preentrenats o arxius auxiliars de paràmetres, heu de comprimir-los conjuntament en un fitxer \texttt{submission.zip}:

\begin{lstlisting}
submission.zip
├── agent.py               # Obligatori: conte la classe BatteryAgent
├── model_consum.pkl       # Opcional: model serialitzat amb joblib
└── config.json            # Opcional: fitxers auxiliars de parametres
\end{lstlisting}

\subsection{Carrega Correcta d'Arxius des de \texttt{agent.py}}
Per carregar arxius auxiliars de forma robusta tant en local com en el servidor, utilitzeu sempre la ruta relativa del propi mòdul mitjançant \texttt{pathlib}:

\begin{lstlisting}
from pathlib import Path
import joblib

class BatteryAgent:
    def __init__(self):
        directori_actual = Path(__file__).resolve().parent
        ruta_model = directori_actual / "model_consum.pkl"
        
        if ruta_model.exists():
            self.model = joblib.load(ruta_model)
        else:
            self.model = None
\end{lstlisting}

\subsection{Script de Verificació Local Recomanat}
Abans de pujar la vostra solució al servidor, valideu que el vostre agent compleix la interfície i no produeix errors d'execució executant localment:
\begin{lstlisting}[language=bash]
python check_submission.py submission.zip
\end{lstlisting}

\vspace{1cm}
\begin{center}
\textbf{Molta sort a tots els equips!} \\
\emph{Que el vostre algorisme assoleixi la màxima eficiència i descarbonització al campus.}
\end{center}

\end{document}
```
