# Prompt para Continuidade — Dashboard Bombeiros Nacional

Copie e cole este prompt ao iniciar uma nova conversa para retomar o projeto.

---

## Contexto

Sou aluno(a) do Mestrado IDP, disciplina de **Storytelling com Dados**.
Estou criando um dashboard individual com dados reais sobre a **Capacidade de Atendimento dos Corpos de Bombeiros Militar (CBM) no Brasil**.

Trabalho no **CBMDF** e tenho envolvimento direto com projetos institucionais de TIC.

## Pergunta Central do Dashboard

> "O país possui recursos humanos nos Corpos de Bombeiros suficientes para atender à sua população?"

## Requisitos do Trabalho

- Dashboard individual, dados reais com fontes citadas
- Mínimo 4 visualizações
- Uso intencional da cor como recurso narrativo (**paleta Okabe-Ito**)
- Títulos narrativos (conclusão, não label)
- Apresentação oral de 10 minutos
- **Prazo: 20/08/2026**

## Fontes de Dados

| Fonte | Descrição | Período |
|-------|-----------|---------|
| SENASP/MJSP | Perfil dos Corpos de Bombeiros Militar | Ano base 2024 |
| IBGE | Censo Demográfico 2022 | 2022 |
| IBGE | Projeção Populacional 2024 | 2024 |
| NFPA | Fire Department Profile 2020 | Referência: 1,54 bombeiros/1.000 hab. |

## Números-chave

| Indicador | Valor |
|-----------|-------|
| População Brasil (Censo 2022) | 202.083.020 |
| Efetivo total ativa (2024) | 68.878 |
| Referência NFPA (1,54/1.000) | 311.208 |
| Déficit nacional | 242.330 |
| Proporção atual | 0,34 /1.000 hab. |
| Crescimento 2020–2024 | +4,2% |
| UFs acima da meta | apenas DF (2,09) e AP (1,70) |
| Estado mais abaixo | PI (0,16) |

## Estrutura do Repositório

```
bombeiros_nacional/                    ← diretório do projeto
├── README.md                         ← documentação completa
├── dashboard_bombeiros.py            ← script Python (6 viz + dashboard completo PNG)
├── index.html                        ← dashboard React interativo (Plotly.js)
├── requirements.txt                  ← dependências Python
├── .gitignore                        ← exclui venv/, *.png, __pycache__/
├── base-dados/
│   ├── bd_ibge_censo_2022_municipio.csv
│   ├── bd_senas.mjsp_perfil_cbm_ano_base_2024.csv
│   ├── dados_dashboard.json          ← dados processados para o HTML
│   └── Anos_Base_2020_2024/          ← dados multianuais CBM
│       └── Ano_base_2020..2024/      ← (5 Excel files)
├── output/                           ← PNGs gerados pelo Python
│   ├── v1_deficit.png
│   ├── v2_mapa.png
│   ├── v3_lollipop.png
│   ├── v4_evolucao.png
│   ├── v5_boxplot.png
│   ├── v6_antes_depois.png
│   └── dashboard_completo.png
└── venv/                             ← ambiente Python (não versionado)
```

## Arquivos Principais

### dashboard_bombeiros.py (Python)
- 6 visualizações individuais + dashboard completo em layout único
- Paleta Okabe-Ito com vermelho (abaixo meta) e verde (acima meta)
- Anotações narrativas (caixas de insight) em cada gráfico
- Roda com: `source venv/bin/activate && python dashboard_bombeiros.py`
- Salva PNGs em `output/`

### index.html (React/Plotly.js)
- Dashboard web interativo, sem build (CDN React 18 + Plotly.js)
- 4 KPIs no topo + 5 visualizações interativas
- Dados embutidos em JSON (base-dados/dados_dashboard.json)
- Paleta Okabe-Ito, tooltips, responsive
- Para testar local: basta abrir o index.html no navegador

### base-dados/dados_dashboard.json
- Dados processados para o dashboard web
- Estrutura: { populacao, efetivo_total, meta_nacional, deficit, ufs[], evolucao[] }

## Paleta de Cores (Okabe-Ito)

```javascript
azul:      '#0072B2'  // dados principais
vermelho:  '#D55E00'  // déficit / abaixo da meta
verde:     '#009E73'  // acima da meta
laranja:   '#E69F00'  // destaque positivo
amarelo:   '#F0E442'  // caixas de insight
rosa:      '#CC79A7'  // destaque secundário
azul_cl:   '#56B4E9'  // dados neutros
preto:     '#000000'  // texto/eixos
cinza:     '#999999'  // notas de rodapé
```

## Visualizações Implementadas

| # | Título Narrativo | Tipo | Dados |
|---|---|---|---|
| 1 | "O Brasil tem déficit de 242 mil Bombeiros" | Barras comparativas | Efetivo vs meta NFPA |
| 2 | "A maioria dos estados está muito abaixo da referência" | Lollipop chart | Proporção por UF vs NFPA |
| 3 | "Efetivo cresceu apenas 4% em 5 anos" | Linhas com área | Evolução 2020–2024 |
| 4 | "Nenhuma região atinge a meta em média" | Box plot | Distribuição por região |
| 5 | "Messo os maiores CBM ficam aquém" | Barras agrupadas | Top 10 UFs: atual vs necessário |
| 6 | Mapa coroplético | Mapa | Proporção por UF (Python) |

## O que já foi feito

- [x] Exploração de dados e identificação de fontes
- [x] Leitura do paper original (trabalho_bombeiros_final.pdf)
- [x] Leitura dos requisitos do trabalho final
- [x] Criação do diretório `bombeiros_nacional` limpo
- [x] Cópia e organização dos dados
- [x] Script Python com 6 visualizações + dashboard completo
- [x] Anotações narrativas e textos storytelling em cada gráfico
- [x] Dashboard React interativo (index.html com Plotly.js)
- [x] README.md completo
- [x] requirements.txt e .gitignore
- [x] Repositório GitHub: https://github.com/timczbsb/bombeiros_nacional
- [x] 3 commits realizados e enviados

## O que pode ser melhorado

- [ ] Habilitar GitHub Pages para visualização online do index.html
- [ ] Adicionar transições/animações no dashboard React
- [ ] Incluir gráfico do mapa coroplético no HTML (atualmente só no Python)
- [ ] Adicionar filtros interativos (por região, por ano)
- [ ] Melhorar responsividade mobile
- [ ] Adicionar slide de apresentação oral (10 minutos)
- [ ] Incluir dados de orçamento/veículos do SENASP como visualização extra
- [ ] Comparação com outros países (dados internacionais)
- [ ] Adicionar seção sobre diversidade de gênero/raça nos CBM

## Comandos Úteis

```bash
# Ativar ambiente
cd bombeiros_nacional
source venv/bin/activate

# Rodar dashboard Python
python dashboard_bombeiros.py

# Abrir dashboard web (local)
xdg-open index.html

# Ver status do git
git log --oneline
git status

# Push de alterações
git add . && git commit -m "mensagem" && git push
```

## Referências Adicionais

- Paper original: `novaideia2/trabalho_bombeiros_final.pdf`
- Notebook antigo: `novaideia2/Fundamentos_CD_TrabFinal.ipynb`
- Portaria CBMDF 2025-2030: `novaideia2/referencias/`
- Ferramentas auxiliares: gapminder, dollar street
