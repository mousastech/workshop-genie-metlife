# MetLife OmniPulse AI — Databricks App (React + FastAPI + Lakebase)

Cockpit do **MetLife Intelligence Hub** com 3 módulos de IA, servido como **Databricks App** (frontend React + backend FastAPI), sobre o Gold do Lakehouse, o endpoint de fraude (Model Serving + AI Gateway) e o **Lakebase** (transacional).

## Módulos
| Módulo | O que faz | Tecnologia |
|---|---|---|
| **1 · Fast-Claims** | Fila de triagem de sinistros de **alto risco de fraude**, com score do modelo e ações (Investigar/Aprovar) | Model Serving `metlife-fraude` + AI Gateway |
| **2 · Churn Shield** | Score de **propensão a cancelamento** (inadimplência, suspensão, ticket) + ação de retenção | Gold + regra/ML; régua no WhatsApp (fase 2) |
| **3 · BrokerX Copilot** | KPIs da carteira + **Genie** (NL sobre o Gold) para o corretor | Databricks Genie + Metric Views |

## Arquitetura
```
React (SPA)  ──►  FastAPI  ──►  SQL Warehouse (Gold: gold_*)        [leitura analítica]
                     │      ──►  Model Serving metlife-fraude (AI Gateway)  [score de fraude]
                     └──────►  Lakebase Postgres (omnipulse)         [transacional: decisões, tb_*]
```
- **Reads** analíticos no Gold via warehouse; **score** de fraude no endpoint governado por AI Gateway; **writes** transacionais (decisões, ações) no **Lakebase**.
- **Lakebase** `projects/metlife-omnipulse` · db `omnipulse` · tabelas `tb_sinistros_analise` (semeada), `tb_apolices_ativas`, `tb_financeiro_arrecadacao`, `decisions`.

## WhatsApp / Omni-channel — Fase 2 (documentado)
O canal WhatsApp é **externo ao Databricks** e entra na Fase 2:
```
[Cliente/Corretor] ─ WhatsApp Business API (Meta/Twilio) ─► [Middleware webhook (FastAPI/Node)] ─► [Databricks Model Serving + Agents]
```
- Middleware recebe a mensagem/imagem, chama o endpoint (fraude/UW) e responde no WhatsApp.
- Intenções: **Sinistro** (Vision RAG lê laudo/PDF → pré-aprova), **Cobrança/Churn** (propõe renegociação/Pix).
- Requer credenciais do BSP (Meta/Twilio) e um endpoint público para o webhook — infra do cliente.

## Deploy
```bash
PROFILE=fevm-moi-ai
databricks sync ./apps/metlife_omnipulse "/Workspace/Users/<voce>/app_omnipulse" --profile $PROFILE --full
databricks apps create metlife-omnipulse --profile $PROFILE
databricks apps deploy metlife-omnipulse --source-code-path "/Workspace/Users/<voce>/app_omnipulse" --profile $PROFILE
```
Conceda ao **service principal do app**: `SELECT` no schema `metlife_pipeline`, `CAN_USE` no warehouse, `CAN_QUERY` no endpoint `metlife-fraude`, e acesso ao Lakebase (recurso `database`).

## Governança
- **AI Gateway** no endpoint: rate limit 60/min, **inference tables** (`metlife_pipeline.fraude_ep_*`), usage tracking.
- **Unity Catalog**: SELECT mínimo ao SP; LGPD/HIPAA via column masks/row filters (fase de governança).
