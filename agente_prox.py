"""
Punto de Entrada Principal — AgenteProx.
Ejecuta el ciclo orquestador modular de acuerdo a la especificación SPEC-01.
"""
import sys
import os

# Asegurar que el directorio raíz esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.engine.orchestrator import run_orchestrator, main

if __name__ == "__main__":
    main()
