# Workshop AI/BI + Genie — MetLife

![Databricks](https://img.shields.io/badge/Databricks-AI%2FBI%20%2B%20Genie-FF3621?logo=databricks&logoColor=white)
![Genie Ontology](https://img.shields.io/badge/Genie-Ontology-1B3139)
![Industry](https://img.shields.io/badge/Ind%C3%BAstria-Seguros-0072B2)
![Language](https://img.shields.io/badge/SQL%20%C2%B7%20YAML%20%C2%B7%20Notebook-000000)
![License](https://img.shields.io/badge/License-MIT-green)

Kit completo e reproduzível de um **workshop prático de Databricks AI/BI + Genie** para a indústria de **seguros** (Vida & Previdência, Sinistros & Fraude, Distribuição & Corretores). Inclui dados sintéticos, camada semântica governada (Metric Views), Domain, glossário, dois Genie Spaces, um dashboard AI/BI e a base para o **Genie Ontology** — além de um notebook guiado estilo *Databricks Academy* e o roteiro da demo.

> Workshop de referência: **17/09**, dia inteiro em 2 sessões — **Sessão 1 (09h–11h) Data Engineering (técnico)**: constrói o pipeline medalhão Bronze→Silver→Gold; **Sessão 2 (11h–13h) Usuário de Negócio**: consome o Gold com AI/BI + Genie, sem código. Dados 100% sintéticos, criados apenas para treinamento.

📐 **Arquitetura e modelo de dados:** [`docs/arquitetura.md`](docs/arquitetura.md) (diagramas Mermaid).

---

## O que este repositório entrega

| Componente | Onde | Descrição |
|---|---|---|
| **Sessão 1 · Data Engineering (notebook)** | [`notebooks/metlife_workshop_class_sessao1_dataeng.py`](notebooks/metlife_workshop_class_sessao1_dataeng.py) | Aula guiada: pipeline medalhão Bronze→Silver→Gold que aterrissa no catálogo |
| **Pipeline medalhão (Lakeflow)** | [`pipelines/`](pipelines/) | Declarative Pipeline (SQL) produtivo — Auto Loader + expectations + Gold |
| **Sessão 2 · Negócio (notebook)** | [`notebooks/metlife_workshop_class_sessao2_business.py`](notebooks/metlife_workshop_class_sessao2_business.py) | Aula guiada AI/BI + Genie (consome o Gold) |
| **Notebook guiado (Academy)** | [`notebooks/metlife_workshop_demo.py`](notebooks/metlife_workshop_demo.py) | Reconstrói e explica todo o ambiente, com o **roteiro da demo** ao final |
| **Dados sintéticos** | [`sql/00`–`sql/07`](sql/) | 7 tabelas de seguros geradas 100% em SQL |
| **Camada semântica** | [`sql/10`–`sql/12`](sql/) | 3 Metric Views governados (carteira, arrecadação, sinistralidade) |
| **Domain + Glossário** | [`sql/13`, `sql/14`](sql/) | glossário certificado (13 termos) + tags de Unity Catalog |
| **Genie Spaces** | [`genie/`](genie/) | 2 espaços (tabelas cruas · camada semântica) + script de criação |
| **Dashboard AI/BI** | [`dashboard/`](dashboard/) | painel sobre os Metric Views + script de criação |
| **Documentos** | [`docs/`](docs/) | programa & laboratório (PT-BR) e session overview (EN) |
| **Página do workshop (HTML)** | [`site/workshop_metlife.html`](site/workshop_metlife.html) | guia visual da aula com identidade MetLife (abrir no navegador) |

---

## Pré-requisitos

- **Databricks CLI** autenticado (`databricks auth login --host <workspace> --profile <perfil>`).
- Um **catálogo Unity Catalog** gravável (padrão neste kit: `moi_ai_catalog`) e um **SQL warehouse**.
- `jq` instalado (para os scripts de Genie/dashboard).
- Runtime **DBR 17.2+** para os Metric Views (`version: 1.1`); 17.3+ para sinônimos.

---

## Runbook — ordem de execução

### 1. Dados + camada semântica + Domain (via notebook, recomendado)

Importe [`notebooks/metlife_workshop_demo.py`](notebooks/metlife_workshop_demo.py) no workspace (**Workspace → Import**) e execute de cima para baixo. Ele cria schema, 7 tabelas, 3 Metric Views, glossário e tags de Domain, com explicações e validações a cada passo.

**Alternativa por SQL puro** (ex.: DBSQL ou CLI), na ordem dos prefixos:

```bash
PROFILE=meu-profile          # perfil do Databricks CLI
for f in sql/00_setup_schema.sql sql/0*_*.sql sql/1[0-4]_*.sql; do
  echo ">> $f"
  databricks experimental aitools tools query --file "$f" --profile "$PROFILE"
done
```

### 2. Genie Spaces

```bash
PROFILE=meu-profile WAREHOUSE_ID=xxxxxxxx \
PARENT=/Workspace/Users/voce@empresa.com/genie_spaces \
  bash genie/create_genie_spaces.sh
```

Cria dois espaços: **tabelas** (exploração/laboratório) e **camada semântica** (só Metric Views — demonstra o Ontology). Guarde os `space_id` retornados.

### 3. Dashboard AI/BI

```bash
PROFILE=meu-profile WAREHOUSE_ID=xxxxxxxx \
PARENT=/Workspace/Users/voce@empresa.com/dashboards \
  bash dashboard/create_dashboard.sh
```

> Para linkar o botão **Ask Genie** do dashboard ao seu espaço, ajuste `uiSettings.genieSpace.overrideId` em [`dashboard/dashboard.json`](dashboard/dashboard.json) com o `space_id` do passo 2.

### 4. Genie Ontology (preview)

O **Genie Ontology** (Genie One, nível de conta) está em **Public Preview**. Depois de os artefatos acima existirem, **contate o time de conta Databricks** para habilitar o preview no workspace — ele passará a consumir Metric Views, Domain e glossário e a inferir contexto de dashboards/queries. Detalhes no notebook (Módulo 5) e em [`docs/programa_e_laboratorio_pt.md`](docs/programa_e_laboratorio_pt.md).

---

## Modelo de dados

```
apolices ─┬─ clientes          (cliente_id)
          ├─ corretores        (corretor_id)
          └─ produtos          (produto_id)
premios ──── apolices          (apolice_id)
sinistros ── apolices          (apolice_id)
sinistros_fraude_score ── sinistros (sinistro_id)
```

**Metric Views:** `mv_carteira` (fato apólices) · `mv_arrecadacao` (fato prêmios) · `mv_sinistralidade` (fato sinistros).

---

## Roteiro da demo (resumo)

1. Catálogo no Catalog Explorer → 2. Dashboard AI/BI (filtros/cross-filter) → 3. Genie sobre tabelas (linguagem natural → SQL) → 4. Curadoria (instruções, sinônimos) → 5. Camada semântica & Ontology (Genie usando `MEASURE()` sobre métricas certificadas) → 6. Fechamento (jornada de adoção).

Roteiro completo com perguntas e tempos: **Módulo 6 do notebook** e `docs/`.

**Números de bolso (gabarito):** Vida ≈ 2.801 / Previdência ≈ 2.753 apólices ativas · inadimplência ≈ 5,1% · persistência ≈ 95% · 261 sinistros suspeitos (≈10,4%) · liquidação média ≈ 67 dias.

---

## Notas técnicas (aprendidas montando este kit)

- **Metric Views via CLI/automação:** use YAML em *flow style* (`dimensions: [{...}, {...}]`) e o *source* como subconsulta SQL com o join pré-feito — evita problemas de indentação e do parser de `joins` em alguns ambientes.
- **`databricks lakeview create`:** sempre passe `--profile` (sem ele a CLI usa o profile DEFAULT e falha com *Invalid access token*), e `--dataset-catalog`/`--dataset-schema` são **flag-only**.
- **Tags governadas:** o metastore pode ter *tag policies* (ex.: `camada` só aceita `bronze/silver/gold`). Ajuste as chaves/valores em [`sql/14_domain_tags.sql`](sql/14_domain_tags.sql) conforme suas políticas.

---

*Dados sintéticos criados exclusivamente para fins de treinamento, no formato MetLife (seguros de vida, previdência, sinistros e distribuição). Não contêm dados reais nem PII.*
