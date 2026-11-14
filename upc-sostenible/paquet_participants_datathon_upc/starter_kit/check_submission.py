"""
starter_kit/check_submission.py
Script local de validació ràpida per als participants del Repte UPC Sostenible.
Execució:
    python check_submission.py
    python check_submission.py agent.py
    python check_submission.py submission.zip
"""

import sys
import os
import ast
import time
import zipfile
import tempfile
import shutil
import importlib.util
from pathlib import Path

# Codis de color per a terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

FORBIDDEN_MODULES = {
    "os", "sys", "shutil", "subprocess", "socket", "urllib", "requests", "http",
    "ftplib", "paramiko", "telnetlib", "pty", "posix", "ctypes", "importlib",
    "inspect", "gc", "builtins", "fcntl", "signal", "threading", "multiprocessing"
}
FORBIDDEN_CALLS = {
    "system", "popen", "spawn", "spawnl", "spawnle", "spawnlp", "spawnlpe",
    "spawnv", "spawnve", "spawnvp", "spawnvpe", "rmtree", "get_objects",
    "currentframe", "stack"
}
FORBIDDEN_BUILTINS = {
    "eval", "exec", "__import__", "compile", "breakpoint", "globals", "locals", "vars"
}
FORBIDDEN_ATTRS = {
    "f_back", "f_locals", "f_globals", "__subclasses__", "__builtins__", "__globals__", "__code__"
}

def check_ast(py_path: Path):
    try:
        content = py_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(py_path.name))
    except Exception as e:
        return f"Error de sintaxi: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_MODULES:
                    return f"Mòdul prohibit detectat: '{root}'. Utilitzeu biblioteques permeses (numpy, pandas, scikit-learn, joblib, etc.)."
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in FORBIDDEN_MODULES:
                    return f"Mòdul prohibit detectat: '{root}'."
        elif isinstance(node, ast.Attribute):
            if node.attr in FORBIDDEN_ATTRS:
                return f"Accés intern no autoritzat: '{node.attr}'."
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_CALLS:
                return f"Funció de sistema no autoritzada: '{node.func.attr}()'."
            elif isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_BUILTINS:
                return f"Funció dinàmica no autoritzada: '{node.func.id}()'."
    return None

def main():
    print(f"\n{BOLD}{CYAN}=== Verificador Local de Solucions — Repte UPC Sostenible ==={RESET}\n")

    # Determinar arxiu
    target_arg = sys.argv[1] if len(sys.argv) > 1 else "agent.py"
    target_path = Path(target_arg).resolve()

    if not target_path.exists():
        print(f"{RED}[ERROR] No s'ha trobat el fitxer: {target_path}{RESET}")
        print("Ús: python check_submission.py [agent.py o submission.zip]")
        sys.exit(1)

    print(f"[*] Analitzant arxiu: {BOLD}{target_path.name}{RESET} ({target_path.stat().st_size / 1024:.1f} KB)")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        if target_path.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(target_path, "r") as z:
                    z.extractall(tmp_path)
            except Exception as e:
                print(f"{RED}[ERROR] L'arxiu ZIP està danyat o no es pot descomprimir: {e}{RESET}")
                sys.exit(1)
        else:
            shutil.copy(target_path, tmp_path / "agent.py")

        agent_files = [f for f in tmp_path.rglob("agent.py") if "__MACOSX" not in f.parts and not f.name.startswith("._")]
        if not agent_files:
            print(f"{RED}[ERROR] No s'ha trobat cap fitxer 'agent.py' dins del paquet.{RESET}")
            sys.exit(1)

        agent_file = agent_files[0]
        print(f"{GREEN}[OK]{RESET} Fitxer 'agent.py' localitzat correctament.")

        # Comprovació AST (ignorant fitxers de metadades macOS)
        for py_f in tmp_path.rglob("*.py"):
            if "__MACOSX" in py_f.parts or py_f.name.startswith("._"):
                continue
            err = check_ast(py_f)
            if err:
                print(f"{RED}[REBUTJAT PER SEGURETAT]{RESET} {py_f.name}: {err}")
                sys.exit(1)
        print(f"{GREEN}[OK]{RESET} Escàner de sintaxi i seguretat superat (sense crides prohibides).")

        # Importació
        orig_cwd = os.getcwd()
        os.chdir(str(agent_file.parent))
        sys.path.insert(0, str(agent_file.parent))

        try:
            spec = importlib.util.spec_from_file_location("test_agent_mod", str(agent_file))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            if not hasattr(mod, "BatteryAgent"):
                print(f"{RED}[ERROR] El fitxer 'agent.py' no defineix la classe obligatòria 'BatteryAgent'.{RESET}")
                sys.exit(1)
            print(f"{GREEN}[OK]{RESET} Classe 'BatteryAgent' trobada.")

            # Instanciació
            t0 = time.time()
            agent = mod.BatteryAgent()
            t_init = (time.time() - t0) * 1000
            print(f"{GREEN}[OK]{RESET} Instanciació de BatteryAgent() completada en {t_init:.2f} ms.")

            if not hasattr(agent, "act") or not callable(agent.act):
                print(f"{RED}[ERROR] L'objecte BatteryAgent no disposa del mètode callable 'act(obs)'.{RESET}")
                sys.exit(1)

            # Simulació de 24 hores de prova amb un diccionari obs representatiu
            print("[*] Executant 24 passos d'inferència de prova...")
            latencies = []
            sample_acts = []

            for step in range(24):
                hour = step % 24
                obs_test = {
                    "timestamp": "2026-01-15 12:00:00",
                    "hour": hour,
                    "day_of_week": (step // 24) % 7,
                    "soc_kwh": 1000.0,
                    "soc_pct": 0.50,
                    "soc_percent": 50.0,
                    "preu_actual": 0.12 + 0.05 * (hour >= 18 and hour <= 21),
                    "co2_actual": 0.15 + 0.08 * (hour >= 20 and hour <= 23),
                    "preus_properes_24h": [0.14] * 24,
                    "co2_properes_24h": [0.18] * 24,
                    "noves_dades_5min": {
                        "ultim_consum_kw": 420.0 + 50.0 * (hour >= 9 and hour <= 18),
                        "ultima_solar_kw": 120.0 if (hour >= 11 and hour <= 16) else 0.0
                    }
                }

                t_step = time.time()
                action = agent.act(obs_test)
                latencies.append((time.time() - t_step) * 1000)

                # Validar retorn
                if not isinstance(action, (int, float)):
                    try:
                        import numpy as np
                        if not isinstance(action, np.number):
                            raise TypeError()
                    except Exception:
                        print(f"{RED}[ERROR Pas {step}] act(obs) ha retornat {type(action).__name__} enlloc d'un float o int!{RESET}")
                        sys.exit(1)

                val = float(action)
                if val != val: # NaN
                    print(f"{RED}[ERROR Pas {step}] act(obs) ha retornat NaN!{RESET}")
                    sys.exit(1)

                if step < 5:
                    sample_acts.append(val)

            avg_lat = sum(latencies) / len(latencies)
            print(f"{GREEN}[OK]{RESET} 24 passos executats satisfactòriament.")
            print(f"    - Temps mitjà per pas d'inferència: {BOLD}{avg_lat:.3f} ms{RESET}")
            print(f"    - Mostra de consignes retornades: {[round(a, 1) for a in sample_acts]}")

            # Fitxers auxiliars
            aux_files = [f.name for f in agent_file.parent.iterdir() if f.is_file() and f.name != "agent.py"]
            if aux_files:
                print(f"    - Fitxers auxiliars/models detectats: {aux_files}")

            print(f"\n{BOLD}{GREEN}>>> RESULTAT: LA SOLUCIÓ ÉS VÀLIDA I ESTÀ A PUNT PER SER LLIURADA A LA WEB! <<<{RESET}\n")

        except Exception as e:
            print(f"\n{RED}[ERROR DURANT L'EXECUCIÓ]{RESET}")
            print(f"{type(e).__name__}: {e}")
            print(f"\n{YELLOW}Consell:{RESET} Assegureu-vos que si carregueu un fitxer '.pkl', utilitzeu:")
            print("    Path(__file__).parent / 'el_vostre_model.pkl'")
            print("enlloc d'una ruta absoluta del vostre disc local.")
            sys.exit(1)
        finally:
            os.chdir(orig_cwd)

if __name__ == "__main__":
    main()
