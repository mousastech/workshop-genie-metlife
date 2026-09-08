# Roteiro de demo — Fluxo de Fraude (OmniPulse AI) · ~2 min

**App:** https://metlife-omnipulse-7474658545709121.aws.databricksapps.com → aba **🩺 Fast-Claims**
**Mensagem-chave:** "Do dado governado à decisão explicável — e o modelo aprende a cada decisão."

| Tempo | Ação (o que clicar) | O que dizer / o que aparece (por baixo) |
|------|----------------------|------------------------------------------|
| 0:00–0:20 | Abrir a aba **Fast-Claims** | "Fila de sinistros de **alto risco**, priorizada pelo **modelo de fraude**. Score e nível de risco vêm do Gold do Lakehouse." |
| 0:20–0:55 | Clicar **🔎 Investigar** na 1ª linha (maior score) | Abre o **painel de análise explicável**: **Passo 1** modelo **ao vivo** (endpoint `metlife-fraude` v2 + **AI Gateway**), **Passo 2** os **4 critérios** (⚠️/✓ com explicação — ocorrência < 180 dias, valor elevado, score, tempo de liquidação), **Passo 3** motivo do alerta + **veredito**. "O analista vê **por que** é suspeito." |
| 0:55–1:20 | Clicar **Abrir investigação (SLA 72h)** | Status vira **"Em análise"**; caso **persistido no Lakebase** (`investigacoes`), com SLA. "Camada **transacional** governada, não só analítica." |
| 1:20–1:40 | Clicar **Confirmar fraude** (ou **Marcar legítimo**) | Grava o **rótulo** no Lakebase (`feedback`, 1/0) + auditoria. "O **feedback humano** vira dado de treino." |
| 1:40–2:00 | Fechar contando o ciclo (falar, sem clicar) | "Um **Job** consome o `feedback` → **re-treina** o modelo → registra **nova versão `@champion`** no Unity Catalog → **swap zero-downtime** no endpoint. O modelo **aprende com cada decisão**." |

## Provas rápidas (se perguntarem)
- **Governança de IA:** endpoint com **AI Gateway** (rate limit 60/min, **inference tables**, usage tracking).
- **Persistência:** `SELECT * FROM decisions/investigacoes/feedback` no Lakebase mostra os cliques.
- **Versionamento:** `modelo_fraude_serving` com **v1 + v2** no UC; endpoint servindo **v2**.

## Bônus (se sobrar tempo)
- Aba **🛡️ Churn Shield**: score de propensão a cancelamento + ação de retenção.
- Aba **🤖 BrokerX Copilot**: KPIs + **Genie** (pergunta em linguagem natural sobre a carteira) → ponte para a **Sessão 2 (negócio)**.
