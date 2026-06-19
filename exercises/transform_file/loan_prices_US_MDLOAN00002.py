#!/acsan/miniconda3/bin/python
"""
loan_prices_US_MDLOAN00002.py
-------------------
Convierte un fichero plano (CSV / TSV / con cualquier separador) al formato
esperado por el ADO destino de Asset Control:

    <CLAVE>|<col1>#<col2>#...#;<row1c1>#<row1c2>#...#;<row2...>;

Uso:

    loan_prices_US_MDLOAN00002.py <fichero_in> <clave> <campos> [<sep_in>]

Argumentos:
    fichero_in  Ruta del fichero de entrada (con cabecera en la primera linea).
    clave       Prefijo de la linea de salida (ej. INT_LOAN_OAS).
    campos      Cabeceras a extraer separadas por '|' (ej. "LX|FCN|OAS").
    sep_in      Separador de columnas en la entrada. Por defecto ','.

Salidas:
    <fichero_in>.prices  Fichero ya en formato destino.
    <fichero_in>.log     Log del proceso.

Codigos de salida (alineados con sysexits.h y la convencion POSIX):
    0    OK.
    1    Error inesperado en ejecucion (ver fichero .log).
    2    El fichero de entrada no existe.
    3    Lista de campos vacia.
    64   Uso incorrecto: faltan argumentos posicionales (EX_USAGE).

Rangos reservados que NO usamos (referencia):
    65-78    sysexits.h (BSD): EX_DATAERR, EX_NOINPUT, EX_SOFTWARE, etc.
    126-127  Comando no ejecutable / no encontrado (shell).
    128+N    Proceso terminado por la senal N.
    255      Codigo fuera de rango.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Sequence, Set

# ---------------------------------------------------------------------------
# Constantes del formato destino (no cambian para este flujo).
# ---------------------------------------------------------------------------

SEP_COL_OUT = "#"   # separador de columnas en la salida
SEP_REG_OUT = ";"   # separador de registros en la salida

# Indices (0-based) de columnas de DATOS que deben emitirse entre comillas
# simples en la salida. La cabecera nunca se entrecomilla.
# Ejemplo: {1} -> 'LX238555#\'00490138985860\'#100.3555#'
QUOTED_COL_INDEXES: Set[int] = {1}


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

class Logger:
    """Logger minimo que escribe a fichero y a stdout con timestamp."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.write_text("", encoding="utf-8")

    def write(self, message: str) -> None:
        line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}"
        print(line)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def resolve_indexes(header: Sequence[str], wanted: Sequence[str]) -> List[int]:
    """Devuelve los indices (0-based) de cada columna pedida en la cabecera."""
    return [header.index(name) for name in wanted]


def convert(
    *,
    fichero_in: Path,
    fichero_out: Path,
    clave: str,
    campos: Sequence[str],
    sep_in: str,
    logger: Logger,
) -> int:
    """Genera el fichero de salida y devuelve el numero de filas escritas."""
    with fichero_in.open("r", encoding="utf-8", errors="replace") as fh:
        lines = [ln.rstrip("\r\n") for ln in fh if ln.strip()]

    if not lines:
        raise ValueError("fichero de entrada vacio")

    header = lines[0].split(sep_in)
    try:
        indexes = resolve_indexes(header, campos)
    except ValueError as exc:
        raise ValueError(f"columna no encontrada en la cabecera: {exc}") from exc

    cabecera_out = SEP_COL_OUT.join(campos) + SEP_COL_OUT
    rows: List[str] = []
    for raw in lines[1:]:
        cols = raw.split(sep_in)
        try:
            values = [cols[i] for i in indexes]
        except IndexError:
            logger.write(f"AVISO: linea con menos columnas, se ignora: {raw!r}")
            continue
        # Aplica comillas simples a las columnas indicadas en QUOTED_COL_INDEXES.
        quoted = [
            f"'{v}'" if pos in QUOTED_COL_INDEXES else v
            for pos, v in enumerate(values)
        ]
        rows.append(SEP_COL_OUT.join(quoted) + SEP_COL_OUT)

    with fichero_out.open("w", encoding="utf-8") as out:
        out.write(f"{clave}|{cabecera_out}{SEP_REG_OUT}")
        for row in rows:
            out.write(row + SEP_REG_OUT)
        out.write("\n")

    return len(rows)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Sequence[str]) -> int:
    if len(argv) < 4:
        sys.stderr.write(
            "Uso: loan_prices_US_MDLOAN00002.py <fichero_in> <clave> <campos> [<sep_in>]\n"
        )
        return 64  # EX_USAGE

    fichero_in = Path(argv[1])
    clave = argv[2]
    campos = [c for c in argv[3].split("|") if c]
    sep_in = argv[4] if len(argv) > 4 else ","

    fichero_out = fichero_in.with_suffix(fichero_in.suffix + ".prices")
    fichero_log = fichero_in.with_suffix(fichero_in.suffix + ".log")

    logger = Logger(fichero_log)
    logger.write(f"***** Inicio: {fichero_in}  clave={clave}  campos={campos}  sep={sep_in!r}")

    if not fichero_in.is_file():
        logger.write(f"ERROR: no existe el fichero de entrada {fichero_in}")
        return 2
    if not campos:
        logger.write("ERROR: lista de campos vacia")
        return 3

    try:
        rows = convert(
            fichero_in=fichero_in,
            fichero_out=fichero_out,
            clave=clave,
            campos=campos,
            sep_in=sep_in,
            logger=logger,
        )
    except Exception as exc:  # noqa: BLE001
        logger.write(f"xxxxx Exception: {exc!r}")
        return 1

    logger.write(f"***** Filas escritas: {rows}")
    logger.write(f"***** Salida: {fichero_out}")
    logger.write("***** Fin")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
