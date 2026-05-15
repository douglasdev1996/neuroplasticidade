import os

# Configurações de Captura
TARGET_URL = "https://playnabets.com/casino/spribe/ap_spribe_8369"
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "data/history.csv")

# ===== CLASSIFICAÇÃO DE VELAS (AJUSTADA) =====
# Baixa (Recolhimento/Loss): < 3x
# Boa (Entrada/Oportunidade): 5x - 9.9x  
# Rosa (Objetivo): >= 10x

BAIXA_THRESHOLD = 3.0      # Não entrar abaixo de 3x
ENTRADA_MIN = 5.0          # Entrar a partir de 5x
ENTRADA_MAX = 9.99         # Até 9.99x é boa oportunidade
ROSA_THRESHOLD = 10.0      # Rosa a partir de 10x
PINK_THRESHOLD = 10.0      # Compatibilidade com código antigo

# Configurações de Análise
LOSS_THRESHOLD = 1.50
MA_FAST = 3
MA_SLOW = 10

# Padrões de Entrada
MIN_LOSS_SEQUENCE = 2
TARGET_MULTIPLIER = 5.0    # Alvo mínimo de entrada: 5x

# Limites de Aprendizado
MAX_HISTORY = 500
CALIBRATION_ROUNDS = 30

# Tema
THEME_COLOR = "#7F77DD"
SUCCESS_COLOR = "#639922"
WARNING_COLOR = "#BA7517"
DANGER_COLOR = "#E24B4A"
INFO_COLOR = "#185FA5"
