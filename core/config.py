# Configurações globais do sistema

ATIVO_PADRAO = "BTCUSDT"
TIMEFRAME = "1m"
STOP_DIARIO = 3
META_DIARIA = 5
FONTE_PRIORITARIA = "binance"
DB_PATH = "data/sinais.db"

# Modo de operação do sistema: "opcao_binaria" ou "daytrade"
MODO_OPERACAO = "opcao_binaria"

# Configurações específicas para cada modo
EXPIRACAO_CANDLES = 1  # utilizado para opcao_binaria
STOP_LOSS_PERCENT = 0.003  # utilizado para daytrade
TAKE_PROFIT_PERCENT = 0.007  # utilizado para daytrade
