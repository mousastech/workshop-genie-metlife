# Deploy no Databricks Free Edition (a partir do Git)

Guia passo a passo para **qualquer pessoa** reproduzir o núcleo do workshop
— dados sintéticos + camada semântica + **Genie** + dashboard AI/BI — em uma
conta **Databricks Free Edition**, clonando este repositório direto do Git.
Tudo roda em **compute serverless** e **sem instalar nada localmente** (nem
CLI, nem `jq`).

> **Tempo estimado:** ~15 min. **Custo:** zero (Free Edition).

---

## O que entra (e o que não entra) no Free Edition

| ✅ Reproduzível no Free Edition | ⛔ Fora de escopo (requer workspace pago) |
|---|---|
| Schema + 7 tabelas sintéticas | Apps (`apps/` — React+FastAPI+**Lakebase**) |
| 3 Metric Views (camada semântica) | Model Serving / endpoints |
| Glossário + tags de Domain | Jobs de orquestração/re-treino contínuo |
| 2 Genie Spaces | Lakebase (Postgres gerenciado) |
| Dashboard AI/BI | AI Gateway / governança de tráfego |

O caminho abaixo cobre o **núcleo do workshop** (dados + AI/BI + Genie), que é
o que 90% dos participantes precisa. O restante depende de recursos que o Free
Edition não expõe.

---

## Pré-requisitos

- Uma conta **Databricks Free Edition** — crie grátis em
  <https://www.databricks.com/learn/free-edition> (só precisa de e-mail).
  O Free Edition já vem com Unity Catalog e um SQL warehouse serverless
  (`Serverless Starter Warehouse`).

Nada mais. Todo o resto é feito pela interface web do workspace.

---

## Passo 1 · Clonar o repositório como Git folder

1. No workspace, barra lateral esquerda → **Workspace**.
2. Botão **Create** (canto superior direito) → **Git folder**.
3. Em **Git repository URL**, cole:

   ```
   https://github.com/mousastech/workshop-genie-metlife.git
   ```

4. **Git provider** = GitHub · deixe o nome da pasta como está → **Create Git folder**.

> Repositório público → **não precisa de token**. Se em algum momento pedirem
> credenciais, gere um GitHub PAT (escopo `repo`) e cadastre em
> **Settings → Linked accounts → Git integration**.

Pronto: você tem uma cópia versionada do kit dentro do seu workspace.

---

## Passo 2 · Criar o catálogo

O kit usa o catálogo `moi_ai_catalog` por padrão (fixo em ~180 lugares).
No Free Edition você **cria esse catálogo uma vez** e não precisa alterar mais nada.

Abra **SQL Editor** (barra lateral) ou uma célula de notebook e rode:

```sql
CREATE CATALOG IF NOT EXISTS moi_ai_catalog;
```

> **Prefere usar o catálogo padrão `workspace`?** Em vez do comando acima, faça
> um _find & replace_ de `moi_ai_catalog` → `workspace` na sua cópia do repo.
> Criar o catálogo é o caminho mais simples e recomendado.

---

## Passo 3 · Rodar o notebook guiado (cria tudo)

1. Na Git folder clonada, abra
   **`notebooks/metlife_workshop_demo.py`**.
2. No topo do notebook, no seletor de compute, escolha **Serverless**.
3. **Run all** (▶▶) e acompanhe as explicações célula a célula.

Isso cria, de forma idempotente (`CREATE OR REPLACE`):

- schema `moi_ai_catalog.metlife_workshop`;
- 7 tabelas (`produtos`, `corretores`, `clientes`, `apolices`, `premios`,
  `sinistros`, `sinistros_fraude_score`);
- 3 Metric Views (`mv_carteira`, `mv_arrecadacao`, `mv_sinistralidade`);
- glossário (13 termos) + tags de Domain.

> **Tags de Domain (célula do Módulo de Domain):** se o metastore recusar
> alguma tag por _tag policy_, ignore o erro dessa célula específica — ela
> não afeta dados nem Genie. Ajuste as chaves em `sql/14_domain_tags.sql`
> se quiser.

**Confira os números de bolso (gabarito):** Vida ≈ 2.801 / Previdência ≈ 2.753
apólices ativas · inadimplência ≈ 5,1% · 261 sinistros suspeitos (≈10,4%).

---

## Passo 4 · Criar o Genie Space (pela UI — recomendado)

No Free Edition o caminho mais simples é criar o Genie Space pela interface
(o script `genie/create_genie_spaces.sh` exige CLI + `jq` + `warehouse_id` —
veja o **Anexo** se preferir automatizar).

1. Barra lateral → **Genie** → **New**.
2. **Warehouse** = `Serverless Starter Warehouse`.
3. **Add tables** → catálogo `moi_ai_catalog` → schema `metlife_workshop`.
   - **Genie de exploração:** selecione as **7 tabelas**.
   - **Genie da camada semântica (Ontology):** selecione só os **3 Metric
     Views** (`mv_*`) — é o que demonstra o Genie consumindo métricas
     certificadas com `MEASURE()`.
4. Dê um título (ex.: `MetLife — Seguros, Sinistros e Distribuição`) e salve.
5. Cole as **instruções/sinônimos** curados: copie os campos do arquivo
   `genie/genie_space_tabelas.json` (chave `instructions` / exemplos) para a
   aba **Instructions** do espaço.

Teste com perguntas em linguagem natural: _"Quantas apólices ativas por linha
de negócio?"_, _"Qual a taxa de sinistros suspeitos?"_.

---

## Passo 5 · Dashboard AI/BI (opcional)

- **Caminho simples:** a **sessão de negócio** (`notebooks/metlife_workshop_class_sessao1_business.py`)
  já guia a construção do painel no AI/BI passo a passo — abra e siga.
- **Caminho por arquivo:** o dashboard serializado está em
  `dashboard/dashboard.json`. Para publicá-lo automaticamente use o script
  `dashboard/create_dashboard.sh` (requer CLI — ver Anexo). Depois, para ligar
  o botão **Ask Genie** ao seu espaço, ajuste
  `uiSettings.genieSpace.overrideId` em `dashboard/dashboard.json` com o
  `space_id` do Passo 4.

---

## Limitações conhecidas do Free Edition

- **1 workspace / 1 metastore** por conta; SQL warehouse serverless
  **2X-Small** único, com cotas de uso.
- **Sem R e sem Scala** (o kit é 100% SQL + Python — ok).
- Sem SSO/SCIM e sem recursos administrativos de tier pago.
- **Genie Ontology** (Genie One, nível de conta) é preview de conta — no Free
  Edition use os Genie Spaces acima; o comportamento de Ontology completo
  depende de habilitação pelo time de conta em workspace pago.

---

## Anexo · Caminho por CLI (opcional, para quem já usa a Databricks CLI)

Se você tiver a **Databricks CLI** autenticada localmente e `jq` instalado,
pode automatizar Genie e dashboard em vez de usar a UI:

```bash
# autenticar (uma vez)
databricks auth login --host <sua-url-free-edition> --profile free

# descobrir o warehouse_id
databricks warehouses list --profile free

# Genie Spaces
PROFILE=free WAREHOUSE_ID=<id> \
PARENT=/Workspace/Users/<voce@email>/genie_spaces \
  bash genie/create_genie_spaces.sh

# Dashboard
PROFILE=free WAREHOUSE_ID=<id> \
PARENT=/Workspace/Users/<voce@email>/dashboards \
  bash dashboard/create_dashboard.sh
```

Os dados/camada semântica também podem ser criados por SQL puro (ver seção
"Runbook" do [`README.md`](../README.md)), mas o notebook do Passo 3 é o
caminho recomendado no Free Edition.
