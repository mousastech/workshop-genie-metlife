# MetLife · Track Técnico (Sandbox) — Runbook

Infraestrutura do **track técnico** do workshop, executado no **sandbox compartilhado do cliente** (workspace Databricks completo — **não** Free Edition).

**Premissa de arquitetura (CAF Brasil DataHub & Self-Service Zone):** a ingestão e o tratamento (Bronze → Silver) são **upstream, responsabilidade da Argentina**. Este track trabalha **somente na camada GOLD**, dentro da self-service zone do Brasil. CI/CD alvo: **Azure DevOps + Databricks Asset Bundles**.

Namespace padrão (ajuste se o sandbox usar outro): catálogo **`metlife_sandbox`**, schema Gold **`workshop_gold`**.

---

## Pré-requisitos que o cliente precisa habilitar no sandbox

- [ ] **Unity Catalog** ativo + permissão para criar o catálogo `metlife_sandbox` (ou um catálogo equivalente já provisionado).
- [ ] **SQL Warehouse serverless** ligado (para os labs SQL).
- [ ] **Grupo de participantes** `workshop_metlife_tecnico` (e, opcional, `workshop_metlife_admin` para os labs de row filter / column mask enxergarem dados sem máscara).
- [ ] **Delta Sharing habilitado** no metastore (Bloco 5 — provider).
- [ ] **Git integration (Repos)** apontando para **Azure DevOps** + um **service principal (OAuth M2M)** com secret para o pipeline de CI/CD.
- [ ] Nosso **acesso com antecedência** (admin ou janela de setup) para semear o Gold, o Genie e o dashboard.
- [ ] *(Opcional — se mantidos ML/Apps)* **Model Serving** e **Databricks Apps** habilitados no tenant.

---

## Ordem de execução dos scripts (`sandbox/sql/`)

| Ordem | Script | O que faz | Bloco da sessão |
|---|---|---|---|
| 1 | `00_setup_gold.sql` | Cria catálogo + schema Gold + grants; instruções para gerar as 7 tabelas Gold | Setup (pré-evento) |
| 2 | `10_user_scratch.sql` | Cada participante cria `scratch_<user>` e uma view derivada do Gold | 0 · Setup / 2 · Gold |
| 3 | `20_uc_governance.sql` | Grants, tags/Domain, lineage, **row filter**, **column mask**, audit, custo | 3 · Governança UC |
| 4 | `30_delta_sharing.sql` | **Share** do Gold (provider) + **recipient** Open Sharing (consumo) | 5 · Delta Sharing |

### Gerar as 7 tabelas Gold (Gold-only)

As tabelas são geradas pelos scripts **100% SQL** do repositório (PyPI é bloqueado): `sql/01_produtos.sql` … `sql/07_fraude.sql`. Para o sandbox, troque o namespace de origem `moi_ai_catalog.metlife_workshop` → `metlife_sandbox.workshop_gold`. A partir da raiz do repo:

```bash
for f in sql/0[1-7]_*.sql; do
  sed 's/moi_ai_catalog\.metlife_workshop/metlife_sandbox.workshop_gold/g' "$f" \
    | databricks sql query --warehouse-id <WAREHOUSE_ID> --query - ;
done
```

(ou cole cada script no SQL Editor após o find/replace do namespace.)

**Checkpoint de reconciliação:** `apolices = 8000` · `premios = 177523` · `sinistros = 2500`.

> **Sandbox compartilhado:** o Gold é **somente leitura** para os participantes. Cada um escreve **apenas** no seu `scratch_<user>` (isolamento derivado de `current_user()` em `10_user_scratch.sql`). Os labs de governança (row filter / column mask) usam pertencimento a grupo (`is_account_group_member`) — quem não é `workshop_metlife_admin` vê os dados filtrados/mascarados.

---

## CI/CD — Azure DevOps + Asset Bundles (Bloco 4)

- `bundle/databricks.yml` — bundle com um job Gold-layer e target `dev` apontando para o sandbox (`${var.sandbox_host}`).
- `azure-pipelines.yml` — pipeline que instala o Databricks CLI e roda `bundle validate` (em PR) e `bundle deploy -t dev` (em push na `main`), autenticando por **service principal (OAuth M2M)**.

Variáveis secretas do pipeline: `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`.

Deploy manual (para demonstrar antes do CI): `cd sandbox/bundle && databricks bundle deploy -t dev`.

Ajuste em `databricks.yml`: `sandbox_host`, `warehouse_id`, `notebook_path` (aponte para o notebook Gold real — ex.: `notebooks/metlife_workshop_class_sessao1_dataeng.py` publicado no workspace).

---

## Mapa labs → blocos da Sessão 2 (Técnica, ~4h30)

| Bloco | Artefato |
|---|---|
| 0 · Setup & isolamento | `sql/10_user_scratch.sql` |
| 1 · Arquitetura & Gold | Catalog Explorer (localizar Gold) |
| 2 · Camada Gold | `sql/10_user_scratch.sql` (view derivada) |
| 3 · Governança UC | `sql/20_uc_governance.sql` |
| 4 · CI/CD (Azure DevOps) | `bundle/databricks.yml` + `azure-pipelines.yml` |
| 5 · Delta Sharing | `sql/30_delta_sharing.sql` |
| 6 · ML fraude | `../notebooks/metlife_ml_fraude_treino.py` |
| 7 · Apps & AI Gateway | `../apps/` + endpoint `metlife-fraude` |
| 8 · Orquestração | `../jobs/metlife_orquestracao_medallion.job.json` (adaptar Gold-only) |
