# Configuracion Global
# ==================

DEBUG_PORT = 9222
AGENT_PORT = 5555
AGENT_TIMEOUT = 5

TEAMS_CHANNEL_URL = "https://teams.microsoft.com/v2/#/channel/19%3A0113cb42e12f407fb933b4b1ac742dca%40thread.tacv2/logs_proxmox?groupId=9300d12e-bf09-4717-aefd-bc1a35d87fac&tenantId=caca42e2-ad4a-4d19-824c-3ff3709bd840"

# ====== CONFIGURACIÓN DE DESTINOS DE TEAMS ======
# Puedes usar cualquiera de estas opciones o combinarlas a tu gusto.
# Nota: La variable de alertas soporta una lista si quieres enviar a varios lugares a la vez.

# --- PRODUCCIÓN REAL ---
TEAMS_SUPPORT_GROUP_NAME = "RPA izzi soporte II" 
TEAMS_ALERT_GROUP_NAME = "logs_proxmox"

# --- PRUEBAS EN CHAT PERSONAL ---
# TEAMS_SUPPORT_GROUP_NAME = "Miguel Angel Ramos Castellanos"
# TEAMS_ALERT_GROUP_NAME = "Miguel Angel Ramos Castellanos"

# --- PRUEBAS EN CHAT PERSONAL + REPORTES EN LOGS_PROXMOX ---
#TEAMS_SUPPORT_GROUP_NAME = "Miguel Angel Ramos Castellanos"  # Pides los reinicios en tu chat
#TEAMS_ALERT_GROUP_NAME = "logs_proxmox"                       # Las alertas van a logs_proxmox
# =============================================== 

# Criterios de Analisis (Soporte)
CRITERIOS = [
    "no conectado",
    "no conectados",
    "sin registros",
    "no ha tomado registros",
    "no tomo registros",
    "bot detenido",
    "sin conexión",
    "no responde",
    "sin tomar registros",
]

# Criterios Regex
CRITERIOS_REGEX = [
    # --- Negaciones / Fallos explícitos ---
    r"no.*registro",       # "no toma registros", "no registro"
    r"sin.*registro",      # "sin registros"
    r"no.*conecta",        # "no se conecta", "no conectada"
    r"sin.*conexi",        # "sin conexión"
    r"no.*toma",           # "no toma", "no está tomando"
    r"falta.*registro",    # "faltan registros"
    r"deten.*proceso",     # "detenido el proceso"
    
    # --- Solicitudes de Acción (Verbos) ---
    r"revisar",            # "favor de revisar", "pueden revisar"
    r"checar",             # "pueden checar", "chequen"
    r"validar",            # "validar ip"
    r"verificar",          # "verificar esta ip"
    
    # --- Solicitudes de Ayuda (LO QUE FALTABA) ---
    r"apoyo",              # "apoyo con esta ip"
    r"ayuda",              # "ayuda con...", "ayudar a..."
    
    # --- Acciones Técnicas ---
    r"conectar",           # "ayudar a conectar", "para conectar"
    r"reinic",             # "reiniciar", "reinicio"
    
    # --- Estados de Error ---
    r"falla",              # "tengo falla", "fallando"
    r"error",              # "marca error"
    r"traba",              # "se trabó", "trabada"
    r"colga",              # "colgada", "se colgó"
    r"pasm",               # "pasmada"
]

# Cache
LAST_TEAMS_HASH = None
ALERTS_SENT_CACHE = set()

# LISTAS DE MAQUINAS
# ==================
LISTA_VMS = [

    ("101(vix34)", "192.168.49.78"),
    ("102(vix33)", "192.168.49.77"),
    ("103(vix37)", "192.168.49.81"),
    ("104(vix46)", "192.168.51.91"),
    ("107(vix39)", "192.168.49.83"),
    ("108(vix40)", "192.168.49.84"),
    ("109(vix41)", "192.168.49.86"),
    ("110(vix42)", "192.168.49.87"),
    ("111(vix43)", "192.168.51.88"),
    ("112(vix44)", "192.168.51.89"),
    ("113(vix45)", "192.168.51.90"),
    ("114(vix47)", "192.168.49.181"),
    ("115(vix48)", "192.168.51.47"),
    ("116(vix49)", "192.168.49.0"),
    ("118(vix36)", "192.168.49.80"),
    ("120(AzRpa)", "192.168.48.224"),
    ("121(6Ram)", "192.168.51.57"),
    ("123(47RAM)", "192.168.48.91"), 

    ("111(vix31)", "192.168.49.43"),
    ("113(vix27)", "192.168.49.58"),
    ("114(vix21)", "192.168.49.90"),
    ("115(vix26)", "192.168.49.57"),
    ("116(vix25)", "192.168.49.37"),
    ("117(vix24)", "192.168.49.36"),
    ("118(vix22)", "192.168.51.48"),
    ("119(vix20)", "192.168.49.30"),
    ("120(vix19)", "192.168.49.29"),
    ("121(vix17)", "192.168.49.127"),
    ("122(vix16)", "192.168.49.26"),
    ("123(vix15)", "192.168.49.25"),
    ("124(vix14)", "192.168.49.31"),
    ("125(vix13)", "192.168.51.164"),
    ("126(vix11)", "192.168.49.21"),
    ("127(vix10)", "192.168.49.151"),
    ("129(vix32)", "192.168.49.76"),

    ("109 (prog18)", "192.168.49.71"),
    ("110 (prog19)", "192.168.49.72"),
    ("111 (prog20)", "192.168.49.73"),
    ("112 (prog21)", "192.168.49.74"),
    ("114 (prog22)", "192.168.49.75"),
    ("115 (prog23)", "192.168.49.105"),
    ("116 (prog25)", "192.168.49.69"),
    ("117 (prog26)", "192.168.49.68"),
    ("118 (prog3)", "192.168.51.178"),
    ("119 (prog29)", "192.168.49.67"),
    ("121 (Equipo14)", "192.168.51.111"),
    ("122 (Equipo13)", "192.168.51.108"),
    ("123 (Equipo12)", "192.168.51.104"),
    ("125 (Equipo10)", "192.168.51.96"),
    ("126 (Equipo9)", "192.168.51.95"),
    ("127 (Equipo19)", "192.168.49.94"),
    ("128 (Equipo18)", "192.168.49.178"),
    ("129 (Equipo8)", "192.168.51.44"),
    ("130 (Equipo7)", "192.168.51.30"),
    ("131 (Equipo6)", "192.168.51.28"),
    ("132 (Equipo3)", "192.168.51.16"),
    ("133 (Equipo4)", "192.168.51.17"),
    ("134 (Equipo5)", "192.168.51.20"),
    ("135 (Equipo2)", "192.168.51.14"),
    ("136 (Equipo1)", "192.168.51.13"),

    #("110 (Equipo19)", "192.168.49.94"), 
    #("113(Win10pro03-n2)", "192.168.49.8"),
    #("114(Win10pro04-n2", "192.168.49.6"),
    #("115(Win10pro04-n2)", "192.168.49.9"),
    #("116(Win10pro04-n2)", "192.168.49.10"),
    #("117(Win10pro04-n2)", "192.168.49.11"),
    #("118(Win10pro04-n2)", "192.168.49.12"),
    #("119(Win10pro-maquina35)", "192.168.49.93"),
    #("122(Win10pro04-n2)", "192.168.49.13")
]

IPS_HIJAS_VIX18 = [
    "192.168.51.220", "192.168.51.221", "192.168.61.4", "192.168.61.5",
    "192.168.61.18", "192.168.61.23", "192.168.61.28", "192.168.61.30",
    "192.168.61.31", "192.168.61.43", "192.168.61.45", "192.168.61.50",
    "192.168.61.51", "192.168.49.67", "192.168.49.68", "192.168.49.69",
    "192.168.49.70", "192.168.49.71", "192.168.49.72", "192.168.49.73",
    "192.168.49.74", "192.168.49.75", "192.168.49.105", "192.168.51.176",
    "192.168.51.177", "192.168.51.178", "192.168.51.189", "192.168.51.190",
    "192.168.51.191", "192.168.51.192", "192.168.51.193", "192.168.51.194",
    "192.168.51.195", "192.168.51.201", "192.168.51.202", "192.168.51.203",
    "192.168.51.204", "192.168.61.42"
]

# LISTA NEGRA: VMs que NO enviaran alerta a Teams (Apagadas / No usadas)
# IDs deben coincidir con el primer elemento de la tupla en LISTA_VMS (sin texto extra)
VMS_IGNORADAS_TEAMS = ["120(vix21c)", "130(vix18)", "133(vix21)", "165(Fidelizaciòn)", "111(vix33)", "161(AzRpa)", "162(6Ram)", "163(izziFtp)"]

# Criterios Regex

# Lista de respuestas aleatorias 
RESPUESTAS_SOPORTE = [
    "Un momento se revisa",
    "Se valida",
    "Lo validamos en un momento",
    "Hola lo revisamos",
    "Lo validamos"
    "Claro se valida",
    "Lo checamos un momento por favor", 
    "Revisamos los equipos",
    "Ya lo estamos atendiendo",
    "Se revisa"
]

RESPUESTAS_EXITO = [
    "Las ips ya están operando",
    "Los bots solicitados ya estan trabajando",
    "Ya se ejecutaron de nuevo las maquinas solicitadas",
    "Ya quedaron listas las maquinas",
    "Las maquinas ya estan trabajando"
]

# Cache de URLs para auto-recuperación de pestañas caídas/cerradas
CACHED_URLS = {
    "proxmox": None,
    "teams": TEAMS_CHANNEL_URL,
    "izzi": None
}