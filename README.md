# Sinalis.AI

Este repositório contém um protótipo modular para coleta e geração de sinais de 
opções binárias usando dados do par **BTCUSDT** na API da Binance.

## Estrutura

- `sinalis/` – pacote com os módulos de coleta de dados, cálculos de indicadores,
  detecção de padrões, classificação de sinais e gestão de risco.
- `main.py` – executável simples que chama o pipeline do pacote.
- `signals.db` – banco SQLite criado automaticamente para armazenamento das 
informações.

## Requisitos

- Python 3.12 ou superior
- Dependências listadas em `requirements.txt`

Instalação das dependências:

```bash
pip install -r requirements.txt
```

## Execução

O pipeline pode ser executado com:

```bash
python -m sinalis
```

ou ainda:

```bash
python main.py
```

O script roda continuamente a cada 5 minutos coletando novos candles, calculando
indicadores e registrando no banco. Caso não seja possível acessar a API da
Binance, verifique restrições de rede.

### Integração com outras APIs

Para enviar os sinais gerados para outro serviço, defina a variável
`API_ENDPOINT` em `sinalis/config.py` com a URL desejada. O módulo
`sinalis.api` enviará automaticamente um POST com as informações do sinal
sempre que um "compra" ou "venda" for identificado.
