# Capacidade de Atendimento dos Corpos de Bombeiros no Brasil

Dashboard de storytelling com dados sobre a capacidade de atendimento dos Corpos de Bombeiros Militar (CBM) em relação à população brasileira.

**Pergunta central:** O país possui recursos humanos nos Corpos de Bombeiros suficientes para atender à sua população?

## Resultados principais

| Indicador | Valor |
|-----------|-------|
| Efetivo total ativa (2024) | 68.878 |
| Referência NFPA (1,54/1.000 hab.) | 311.208 |
| Déficit nacional | **242.330** |
| Proporção atual | 0,34 /1.000 hab. |
| UFs acima da meta | apenas DF e AP |
| Crescimento 2020–2024 | +4,2% |

## Visualizações

O dashboard gera 7 figuras com paleta **Okabe-Ito** (acessível para daltônicos):

1. **Déficit numérico** — barras comparando efetivo atual vs. meta NFPA
2. **Mapa coroplético** — proporção de bombeiros por UF
3. **Lollipop chart** — cada UF posicionada em relação à referência
4. **Evolução temporal** — efetivo e proporção de 2020 a 2024
5. **Box plot por região** — distribuição entre regiões brasileiras
6. **Antes vs. Depois** — top 10 UFs: efetivo atual vs. necessário
7. **Dashboard completo** — layout único com todas as visualizações

## Como executar

```bash
# Clonar o repositório
git clone https://github.com/timczbsb/bombeiros_nacional.git
cd bombeiros_nacional

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar o script
python dashboard_bombeiros.py
```

As imagens são salvas na pasta `output/`.

## Estrutura do repositório

```
bombeiros_nacional/
├── dashboard_bombeiros.py          # Script principal
├── requirements.txt                # Dependências Python
├── .gitignore
├── base-dados/
│   ├── bd_ibge_censo_2022_municipio.csv
│   ├── bd_senas.mjsp_perfil_cbm_ano_base_2024.csv
│   └── Anos_Base_2020_2024/        # Dados multianuais CBM
└── output/                         # PNGs gerados (gitignore)
```

## Fontes de dados

| Fonte | Descrição | Período |
|-------|-----------|---------|
| SENASP/MJSP | Perfil dos Corpos de Bombeiros Militar | Ano base 2024 |
| IBGE | Censo Demográfico 2022 | 2022 |
| IBGE | Projeção Populacional | 2024 |
| NFPA | Fire Department Profile | 2020 |

**Referência internacional:** NFPA Research 2022 — 1,54 bombeiros militares por 1.000 habitantes.

## Dependências

- Python 3.10+
- matplotlib >= 3.11
- pandas >= 2.0
- numpy >= 1.24
- openpyxl >= 3.1
- geopandas >= 1.0
- geobr >= 1.0
- requests >= 2.31

## Licença

Projeto acadêmico — Mestrado IDP, 2026.
