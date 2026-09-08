# MetLife Odonto — Cotação de Planos Odontológicos (Databricks App)

Fluxo conversacional que coleta os dados do cliente **passo a passo**, grava no **Lakebase** e
recomenda o **melhor plano**. UI é um **simulador de WhatsApp**; o `/webhook` já está no formato
**Meta Cloud API** para plugar o WhatsApp Business API na **fase 2**. Perfis: **Individual** e **Família**.

## Fluxo (state machine)
consentimento (LGPD) → perfil → nº de vidas (família) → UF → idade → cobertura (Básico/Ortodontia/Completo)
→ orçamento/vida → nome → **recomendação do melhor plano** (grava em `cotacoes_odonto`).

## Dados no Lakebase (instância `metlife-omnipulse-db`, db `omnipulse`)
- `planos_odonto` — catálogo (Essencial/Família/Ortho/Completo).
- `cotacoes_odonto` — estado da conversa + campos coletados + plano recomendado (1 linha por sessão/telefone).
- `cotacao_mensagens` — transcript (auditoria).

## WhatsApp real (fase 2) — o que é preciso
1. **WhatsApp Business API**: Meta Cloud API (ou BSP Twilio/360dialog) — número verificado, `phone_number_id`, token, **templates aprovados**.
2. **Webhook público HTTPS**: a Meta chama `/webhook` (GET verify + POST mensagens). Databricks Apps são autenticados (SSO); para produção, exponha o webhook por um **middleware/API gateway público** que repassa ao app/endpoint, ou hospede o motor num **Model Serving**.
3. **Envio de resposta**: `POST /{phone_number_id}/messages` com o token (fase 2 — hoje o `/webhook` só devolve o texto).
4. **Secrets** (Databricks Secrets): token, verify token, phone_number_id.
5. **LGPD**: opt-in no início (já incluso) + masking de dados sensíveis.

## Deploy
```
databricks apps create metlife-odonto --profile <p>
databricks sync ./apps/metlife_odonto "/Workspace/Users/<voce>/app_odonto" --profile <p> --full
databricks apps deploy metlife-odonto --source-code-path "/Workspace/Users/<voce>/app_odonto" --profile <p>
```
Ligue a instância Lakebase como recurso `database` e conceda ao SP do app privilégios no schema `public`.
