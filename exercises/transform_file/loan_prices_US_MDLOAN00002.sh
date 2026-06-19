#!/usr/bin/ksh
#==============================================================================
# loan_prices_US_MDLOAN00002.sh
#------------------------------------------------------------------------------
# Convierte un fichero plano al formato:
#   <CLAVE>|<col1>#<col2>#...#;<row1c1>#<row1c2>#...#;...
#
# Uso:
#   loan_prices_US_MDLOAN00002.sh <FILENAME> <CLAVE> <INTERFAZ> [<SEP_ENTRADA>]
#
#   FILENAME      Ruta del fichero de entrada.
#   CLAVE         Prefijo de la linea de salida (ej. INT_LOAN_OAS).
#   INTERFAZ      Interfaz en INTSAN_CURVE de donde leer la lista CAMPOS.
#   SEP_ENTRADA   Separador de columnas del fichero de entrada (default ',').
#
# Salida:
#   ${FILENAME}.prices
#   ${FILENAME}.log
#
# Reference files:
# Load_loan.sh, lee_fichero_loan.py
#
# Codigos de salida (alineados con la convencion de Bash + sysexits.h):
#   0   OK.
#   1   Uso incorrecto: faltan FILENAME / CLAVE / INTERFAZ.
#   2   Fichero de entrada invalido (no existe, no legible o vacio).
#   3   No se pudo obtener CAMPOS desde la interfaz en INTSAN_CURVE.
#   4   Fallo en la conversion a formato Unix (cp / dos2unix / sed / mv).
#   *   Cualquier otro valor proviene de lee_fichero_loan.py (ver su cabecera).
#
# Codigos reservados que NO usamos (referencia):
#   64-78   sysexits.h (BSD). 126 no ejecutable. 127 no encontrado.
#   128+N   muerto por senal N. 255 fuera de rango.
#==============================================================================

# export PATH=$PATH:/usr/cluster/bin:/usr/local/bin:./:${AC_SYSTEM}/bin/external

# =========================================
# Call Environment variables
# =========================================
. /acsan$AC_SYSTEM/local/bin/imfenv.sh

SCRIPT_NAME=$(basename "$0")

CAPT_PATH=/acsan$AC_SYSTEM/in/GBMRISK/INTSAN/

# =========================================
# Logs definition
# =========================================
log_info()    { echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO]  $*"; }
log_warning() { echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN]  $*"; }
log_error()   { echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" >&2; }


#######################################
# Print the script's command-line usage to STDOUT.
# Globals:
#   SCRIPT_NAME - basename of the running script.
# Arguments:
#   None.
# Outputs:
#   Writes the usage banner to STDOUT.
# Returns:
#   0.
#######################################
function usage
{
	log_info "$SCRIPT_NAME -f FILENAME -i INTERFAZ -d FECHA"
	log_info "-f Nombre del fichero plano de entrada"
	log_info "-i Interfaz donde se guarda la configuración de la captura"
	log_info "-d Fecha"
}


# Si el numero de parametros no es igual a 3
if [ $# -ne 6 ];
then
	log_error "+++Numero incorrecto de argumentos+++ "
	usage
	exit 1
fi

while getopts f:i:d: opt
do
	case $opt in
		f) FILENAME=$OPTARG
		;;
        i) INTERFAZ=$OPTARG
		;;
        d) FECHA=$OPTARG
		;;
		*)
		echo "Unknown option '-$OPTARG'"
	esac
done


if [[ $FILENAME == "" || $INTERFAZ == "" || $FECHA == "" ]]
then
        echo "Debes introducir todos los parametros"
		usage
        exit 2
fi

FILENAME=${CAPT_PATH}${FILENAME}
FILENAME=${FILENAME/DATE/$FECHA}

# =========================================
# Validacion del fichero de entrada
# =========================================
if [ ! -s "${FILENAME}" ]; then
    log_error "El fichero ${FILENAME} no existe o esta vacio"
    exit 2
fi

# =========================================
# Recupera la configuración desde INTSAN_CURVE
# =========================================

CAMPOS=`echo 'data=first(ts("'$INTERFAZ'",[1,0],"INTSAN_CURVE","treeid=INTERNAL"));return data[lsearch(first(transpose(data)),"CAMPOS")][1];' | ac_evalform`
GLOBAL_CODE=`echo 'data=first(ts("'$INTERFAZ'",[1,0],"INTSAN_CURVE","treeid=INTERNAL"));return data[lsearch(first(transpose(data)),"GLOBAL_CODE")][1];' | ac_evalform`
SEP=`echo 'data=first(ts("'$INTERFAZ'",[1,0],"INTSAN_CURVE","treeid=INTERNAL"));return data[lsearch(first(transpose(data)),"SEP")][1];' | ac_evalform`

# ATTRIBUTE_CFG_COMMAND="data=first(ts('${INTERFAZ}',[1,0],'INTSAN_CURVE','treeid=INTERNAL'));campos=remove(contractVal=data[lsearch(first(transpose(data)),'CAMPOS')],0);return campos[0];"
# CAMPOS=`echo $ATTRIBUTE_CFG_COMMAND | ac_evalform`

log_info "CAMPOS: ${CAMPOS}"
log_info "GLOBAL_CODE: ${GLOBAL_CODE}"
log_info "SEP: ${SEP}"

if [[ -z "${CAMPOS}" || -z "${GLOBAL_CODE}" || -z "${SEP}" ]]; then
	log_warning "El ADO de config ${INTERFAZ} no tiene los atributos necesarios para continuar "
	log_warning "Salimos del script"
	exit 3
fi


# =========================================
# Conversion a formato Unix (LF)
# =========================================

# Trabajamos sobre una copia para no mutar el fichero original.
CONVERTED_FILE="${FILENAME}.unix"
if ! cp -p "${FILENAME}" "${CONVERTED_FILE}"; then
    log_error "No se pudo crear la copia de trabajo ${CONVERTED_FILE}"
    exit 4
fi

# Intento principal: dos2unix. Si falla (tipicamente por problemas de
# propietario al renombrar el temporal en AC), usamos sed como fallback.
DOS2UNIX_OUTPUT=$(dos2unix "${CONVERTED_FILE}" 2>&1)
DOS2UNIX_EXIT=$?

if [[ ${DOS2UNIX_EXIT} -ne 0 ]]; then
    log_warning "${DOS2UNIX_OUTPUT}"
    log_warning "fallo dos2unix (probable problema de propietario). Usando fallback sed..."
    if ! sed -i 's/\r$//' "${CONVERTED_FILE}"; then
        log_error "El fallback sed tambien fallo sobre ${CONVERTED_FILE}"
        rm -f "${CONVERTED_FILE}"
        exit 4
    fi
    log_info "Conversion CRLF->LF completada via sed"
else
    log_info "dos2unix ejecutado exitosamente"
fi

# Elimina el BOM UTF-8 de la primera linea si existiera.
sed -i '1s/^\xEF\xBB\xBF//' "${CONVERTED_FILE}"

# Conversion OK: reemplazamos el original por la copia convertida,
# manteniendo el mismo nombre de fichero.
if ! mv "${CONVERTED_FILE}" "${FILENAME}"; then
    log_error "No se pudo reemplazar ${FILENAME} con la version convertida"
    rm -f "${CONVERTED_FILE}"
    exit 4
fi
log_info "Fichero ${FILENAME} normalizado a formato Unix"


# =========================================
# Procesamiento del fichero
# =========================================

PYTHON_SCRIPT_NAME="loan_prices_US_MDLOAN00002.py"
PYTHON_SCRIPT=${PATH_LOCAL_BIN}"/"${PYTHON_SCRIPT_NAME}

if [ ! -s "${PYTHON_SCRIPT}" ]; then
    log_error "El script ${PYTHON_SCRIPT} no existe o esta vacio"
    exit 1
fi

log_info "Ejecutando script ${PYTHON_SCRIPT}"

python3 "${PYTHON_SCRIPT}" "${FILENAME}" "${GLOBAL_CODE}" "${CAMPOS}" "${SEP}"

if [ ! -s "${FILENAME}.prices" ]; then
    log_error "El fichero ${FILENAME}.prices no existe o esta vacio"
    exit 1
fi

log_info "Fichero ${FILENAME}.prices generado correctamente"

exit 0
