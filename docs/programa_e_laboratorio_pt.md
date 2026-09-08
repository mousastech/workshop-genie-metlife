# MetLife — Workshop AI/BI + Genie | Programa e Laboratório Prático

<!-- toc -->

**Data:** 17 de setembro de 2026 · **Horário:** 11h00 – 13h00 (2h) · **Sessão 2 de 2 — trilha Usuário de Negócio** · **Formato:** Presencial, mão na massa · **Público:** Negócio (analistas e donos de área)

> **O dia em duas sessões:**
> - **Sessão 1 · 09h00–11h00 — Databricks para Usuário Técnico (Data Engineering).**
> - **Sessão 2 · 11h00–13h00 — Databricks para Usuário de Negócio (este documento): AI/BI + Genie.**

Este documento reúne (1) o **menu / programa**, (2) o **ambiente e acessos**, (3) o **laboratório prático passo a passo em português**, (4) o **módulo de Genie Ontology / camada semântica** e (5) o **gabarito**. Todo o laboratório roda sobre uma base sintética de seguros no formato MetLife (Vida, Previdência, sinistros/fraude e distribuição). O público de negócio **não precisa escrever SQL** — os trechos de SQL servem de gabarito/bastidores para o instrutor.

---

## 1. Menu do programa

| Horário | Bloco | O que vamos fazer |
|---------|-------|-------------------|
| 11h00 – 11h10 | **1. Abertura e a visão de AI/BI para seguros** | Por que análise conversacional; tour rápido da plataforma |
| 11h10 – 11h40 | **2. Dashboards AI/BI (mão na massa)** | Construir seu primeiro dashboard, sem código |
| 11h40 – 12h20 | **3. Genie — conversa em linguagem natural (mão na massa)** | Perguntas em linguagem natural sobre a base de seguros |
| 12h20 – 12h45 | **4. Genie confiável — curadoria e camada semântica** | Instruções, sinônimos, Metric Views, Domain, glossário e Ontology |
| 12h45 – 12h55 | **5. Laboratório de casos de uso MetLife** | Fraude, distribuição e persistência |
| 12h55 – 13h00 | **6. Encerramento e jornada de adoção** | Próximos passos e Q&A |

**Objetivos de aprendizagem.** Ao final, cada participante será capaz de: navegar a Databricks Data Intelligence Platform; construir e compartilhar um dashboard AI/BI sem código; fazer perguntas de negócio no Genie e interpretar as respostas; entender o que torna uma resposta do Genie *confiável* (instruções, sinônimos, **Metric Views**, **Domain**, **glossário** e exemplos certificados) e como isso alimenta o **Genie Ontology**; e aplicar tudo isso a três casos de uso MetLife.

---

## 2. Ambiente e acessos

- **Workspace:** [fevm-moi-ai.cloud.databricks.com](https://fevm-moi-ai.cloud.databricks.com/?o=7474658545709121)
- **Genie Space (tabelas / exploração):** [MetLife - Seguros, Sinistros e Distribuicao](https://fevm-moi-ai.cloud.databricks.com/genie/rooms/01f1ab8ced4b1c7d88c2984cedb40565?o=7474658545709121)
- **Genie Space (camada semântica / Metric Views):** [MetLife - Camada Semantica](https://fevm-moi-ai.cloud.databricks.com/genie/rooms/01f1ab9021281c98a4a183c6b5f80067?o=7474658545709121)
- **Dashboard AI/BI de referência:** [MetLife - Painel de Seguros](https://fevm-moi-ai.cloud.databricks.com/sql/dashboardsv3/01f1ab91baf51017b6a24adc9a23888e/published?o=7474658545709121)
- **Catálogo / schema dos dados:** `moi_ai_catalog.metlife_workshop`

Nenhuma instalação é necessária — tudo roda no navegador. As bases, os Metric Views e os Genie Spaces já estão prontos; começamos a perguntar desde o primeiro minuto.

### Modelo de dados (7 tabelas)

| Tabela | Grão | Conteúdo | Volume |
|--------|------|----------|--------|
| `apolices` | 1 linha por apólice | Vida e Previdência: produto, capital/reserva, prêmio, status, canal, região | ~8.000 |
| `clientes` | 1 linha por segurado | Demografia, cidade/UF/região, renda, segmento | ~5.000 |
| `corretores` | 1 linha por corretor | Canal, região/UF, data de credenciamento, meta anual | 150 |
| `produtos` | 1 linha por produto | Linha de negócio, tipo (Vida Individual, PGBL, VGBL...), taxa de carregamento | 12 |
| `premios` | 1 linha por competência/apólice | Pagamentos mensais: valor devido/pago, status, vencimento | ~177.000 |
| `sinistros` | 1 linha por sinistro | Tipo, datas, valor reclamado/pago, tempo de liquidação, suspeita de fraude | 2.500 |
| `sinistros_fraude_score` | 1 linha por sinistro | Score de fraude (0–100), nível de risco, motivo do alerta | 2.500 |

**Relacionamentos:** `apolices` liga-se a `clientes`, `corretores` e `produtos`; `premios` e `sinistros` ligam-se a `apolices`; `sinistros_fraude_score` liga-se a `sinistros`.

### Camada semântica governada (Metric Views)

| Metric View | Fato | Métricas principais |
|-------------|------|---------------------|
| `mv_carteira` | apólices | Apólices, Apólices Ativas, Prêmio Mensal Total, Capital Segurado, Reserva, Ticket Médio, Taxa de Cancelamento |
| `mv_arrecadacao` | prêmios | Valor Devido, Valor Arrecadado, Pagamentos Inadimplentes, **Taxa de Inadimplência**, **Taxa de Arrecadação (persistência)** |
| `mv_sinistralidade` | sinistros | Sinistros, Valor Reclamado, Valor Pago, **Tempo Médio de Liquidação**, Sinistros Suspeitos, **Taxa de Fraude**, Sinistros de Alto Risco |

Além disso: **glossário de negócio certificado** (`glossario_negocio`, 13 termos) e **Domain** aplicado via tags de Unity Catalog (`dominio_negocio = 'Seguros MetLife'`).

---

## 3. Laboratório prático (passo a passo)

> **Como usar este laboratório.** Cada exercício traz o **objetivo**, o **passo a passo** e a **pergunta exata** para digitar no Genie. As respostas esperadas estão na **Seção 5 — Gabarito**. Trabalhe no seu próprio ritmo; o instrutor acompanha por bloco.

### Laboratório A — Seu primeiro dashboard AI/BI (Bloco 2)

**Objetivo:** construir um dashboard executivo da carteira, sem escrever SQL.

1. No menu lateral do workspace, abra **Dashboards** e clique em **Create dashboard**.
2. Na aba **Data**, clique em **Add data** e adicione a tabela `moi_ai_catalog.metlife_workshop.apolices`.
3. Vá para a aba **Canvas** e crie os widgets abaixo com **Add visualization**:
   - **Contador (KPI):** total de apólices ativas → filtre `status_apolice = 'Ativa'` e use *Count*.
   - **Barras:** prêmio mensal total por `regiao` (eixo Y = *Sum* de `premio_mensal`; eixo X = `regiao`).
   - **Pizza/rosca:** distribuição de apólices por `linha_negocio`.
   - **Barras:** contagem de apólices por `status_apolice`.
4. Adicione um **filtro** de `linha_negocio` no topo do canvas e veja os widgets reagirem.
5. Clique em **Publish** para publicar o dashboard e explore o botão **Share**.

**Desafio (opcional):** adicione um widget de **prêmio médio por segmento de cliente** cruzando com a tabela `clientes` (dica: adicione `clientes` em *Data* e relacione por `cliente_id`).

> **Gabarito visual:** o [Dashboard AI/BI de referência](https://fevm-moi-ai.cloud.databricks.com/sql/dashboardsv3/01f1ab91baf51017b6a24adc9a23888e/published?o=7474658545709121) mostra como fica um painel completo sobre os Metric Views (KPIs, prêmio por região, arrecadação mensal, sinistros/fraude e top corretores), com botão "Ask Genie" integrado.

### Laboratório B — Primeira conversa no Genie (Bloco 3)

**Objetivo:** obter respostas de negócio em linguagem natural e ler o SQL gerado.

1. Abra o **[Genie Space (tabelas)](https://fevm-moi-ai.cloud.databricks.com/genie/rooms/01f1ab8ced4b1c7d88c2984cedb40565?o=7474658545709121)**.
2. Repare nas **perguntas sugeridas** na tela inicial — clique em uma delas para começar.
3. Digite, uma a uma, as perguntas abaixo. Depois de cada resposta, clique em **"Show generated code / SQL"** para ver a consulta que o Genie escreveu:
   - *"Quantas apólices ativas temos por linha de negócio?"*
   - *"Qual o prêmio mensal total por região?"*
   - *"Quais os 10 corretores com maior produção de prêmio?"*
4. Faça uma **pergunta de acompanhamento** sobre o último resultado, sem repetir o contexto:
   - *"E somente na região Sudeste?"*
   - *"Mostre em um gráfico de barras."*
5. Observe: quando a pergunta é clara e usa termos do negócio, o Genie acerta o SQL. Quando é ambígua, ele pede esclarecimento — isso é esperado.

**Dica de leitura crítica:** confira sempre a cláusula `WHERE` e os `GROUP BY` do SQL gerado. Foi isso que você perguntou?

### Laboratório C — Tornando o Genie confiável: curadoria (Bloco 4)

**Objetivo:** entender *por que* o Genie responde bem aqui — e como você faria o mesmo na base real da MetLife.

1. No Genie Space, abra as **Instructions** e leia as instruções de negócio já cadastradas — por exemplo, que *"prêmio" é o valor pago pelo segurado* e que *capital segurado só existe para Vida*.
2. Abra a lista de **tabelas** e veja as **descrições de colunas** e **sinônimos** (ex.: `premio_mensal` → "prêmio", "mensalidade").
3. Teste o efeito dos sinônimos perguntando com o vocabulário do negócio:
   - *"Qual a mensalidade média das apólices de Vida ativas?"* (o Genie entende "mensalidade" = prêmio).
   - *"Quantos segurados temos no segmento Premier?"*
4. Faça uma pergunta que exige **join** entre tabelas e confirme que funciona:
   - *"Qual o prêmio total por canal de distribuição do corretor?"*
   - *"Qual a renda média dos clientes com apólices de Previdência?"*
5. Abra os **exemplos de SQL certificados** e observe como eles ensinam padrões corretos.

### Laboratório D — Casos de uso MetLife (Bloco 5)

Escolha **pelo menos um** dos três trilhos e responda às perguntas no Genie.

**D1 — Sinistros e fraude**
- *"Qual o tempo médio de liquidação de sinistros por tipo?"*
- *"Quantos sinistros com suspeita de fraude temos e qual o valor total reclamado?"*
- *"Liste os sinistros de alto risco de fraude com o motivo do alerta."*

**D2 — Distribuição e corretores**
- *"Quais os 10 corretores com maior produção de prêmio?"*
- *"Qual o prêmio total por canal de distribuição?"*
- *"Qual canal tem o maior ticket médio de prêmio mensal?"*

**D3 — Persistência e inadimplência**
- *"Qual a taxa de inadimplência por região?"*
- *"Compare o percentual de pagamentos em atraso entre Vida e Previdência."*
- *"Qual a evolução mensal dos prêmios pagos em 2025?"*

**Fechamento:** monte 1 pergunta original de negócio, rode no Genie, valide o SQL e compartilhe com a turma.

### Laboratório E — Camada semântica e Metric Views (Bloco 4)

**Objetivo:** comparar perguntar sobre **tabelas cruas** vs. sobre **métricas governadas**, e ver a base do Genie Ontology na prática.

1. Abra o **[Genie Space (camada semântica)](https://fevm-moi-ai.cloud.databricks.com/genie/rooms/01f1ab9021281c98a4a183c6b5f80067?o=7474658545709121)** — ele aponta **apenas para os 3 Metric Views**, não para as tabelas cruas.
2. Faça as perguntas abaixo e repare que o Genie usa `MEASURE(...)` sobre métricas **já definidas e certificadas** (sem reinventar o cálculo):
   - *"Qual a taxa de arrecadação (persistência) por região?"*
   - *"Qual o tempo médio de liquidação e a taxa de fraude por tipo de sinistro?"*
   - *"Qual o ticket médio de prêmio por linha de negócio?"*
3. Compare com o Laboratório B: no Space de tabelas, o Genie **deriva** o cálculo; aqui ele **reutiliza** a definição canônica. Menos ambiguidade, mais consistência entre pessoas e dashboards.
4. Abra um dos Metric Views no Catalog Explorer (ex.: `mv_arrecadacao`) e veja as **medidas, dimensões e sinônimos** governados.

---

## 4. Genie Ontology e a camada semântica

**O que é.** O **Genie Ontology** é a camada de *contexto unificado* (um "mapa de negócio" / knowledge graph) que o **Genie One** (nível de conta) constrói sobre a organização, para responder com mais precisão e rastreabilidade. Ele combina dois tipos de contexto:

1. **Semânticas governadas do Unity Catalog** — que *você define*: **Metric Views**, **Domains** e **Pages/glossário**. É a fonte da verdade.
2. **Contexto inferido** — *snippets* que o Genie **extrai automaticamente** de dashboards, queries SQL, Metric Views e Genie Agents, com *authority scoring* (por fonte, frequência de uso e atualidade).

**O que já construímos para este workshop (blocos do ontology, prontos hoje):**

| Bloco do Ontology | O que criamos |
|-------------------|---------------|
| **Metric Views** | `mv_carteira`, `mv_arrecadacao`, `mv_sinistralidade` — métricas canônicas com sinônimos |
| **Domain** | Tags de Unity Catalog (`dominio_negocio = 'Seguros MetLife'`, `camada`, `certificado`, `area_negocio`) no schema, tabelas e Metric Views |
| **Glossário** | Tabela certificada `glossario_negocio` (13 termos: prêmio, sinistralidade, persistência, fraude...) |
| **Ativos certificados** | Genie Space de camada semântica + dashboards do Lab A geram *snippets* de alta autoridade |

**Habilitação do preview (passo pendente, fora deste ambiente).** O Genie Ontology (Genie One, nível de conta) está em **Public Preview** (set/2026). Para ativá-lo, **contate o time de conta Databricks** para incluir o workspace no preview. Depois de habilitado, o Genie One passa a consumir automaticamente os Metric Views, o Domain e o glossário que já deixamos prontos, e a inferir *snippets* das queries e dashboards do workshop. Os *snippets* são governados por permissões do Unity Catalog.

**Como promover o glossário/Domain ao nativo.** Quando o preview estiver ativo, os termos do `glossario_negocio` podem ser registrados como **Pages/Business Glossary** e as tags de Domain migradas para os **Domains** nativos do Unity Catalog, mantendo a mesma taxonomia.

---

## 5. Gabarito (respostas esperadas)

Valores aproximados da base sintética — para o instrutor conferir as respostas do Genie.

| Pergunta | Resposta esperada |
|----------|-------------------|
| Apólices ativas por linha de negócio | **Vida ≈ 2.801** e **Previdência ≈ 2.753** |
| Ticket médio de prêmio por linha | Vida ≈ R$ 1.368 · Previdência ≈ R$ 1.555 |
| Prêmio mensal total por região (ativas) | Sudeste ≈ R$ 2,51 mi · Sul ≈ R$ 1,92 mi · Nordeste ≈ R$ 1,43 mi · Norte ≈ R$ 1,24 mi · Centro-Oeste ≈ R$ 1,05 mi |
| Tempo médio de liquidação de sinistros | **≈ 67 dias** no geral |
| Sinistros com suspeita de fraude | **261 (≈ 10,4%)**, ~R$ 47,8 mi reclamados |
| Sinistros de alto risco de fraude | **≈ 196** com nível "Alto" |
| Taxa de inadimplência geral | **≈ 5,1%** (equilibrada entre canais e regiões) |
| Taxa de arrecadação (persistência) | **≈ 95%** do valor devido |

> **Nota didática:** a inadimplência foi desenhada equilibrada entre canais — um bom gancho para discutir *por que segmentar por outra dimensão* (região, produto, faixa de renda) revela mais insight. A **sinistralidade real (loss ratio)** cruza `mv_sinistralidade` (valor pago) com `mv_arrecadacao` (arrecadação) — ótimo exemplo de métrica multi-fonte que o Ontology ajuda a padronizar.

---

## 6. Encerramento e jornada de adoção

- **Do workshop à produção:** conectar os dados reais da MetLife no Unity Catalog, criar Metric Views por domínio e um Genie Space por área de negócio (sinistros, distribuição, atuarial...).
- **Confiança e governança:** curadoria de instruções e sinônimos, Domains e glossário, controle de acesso por Unity Catalog e certificação de perguntas/SQL — tudo alimentando o Genie Ontology.
- **Escala:** dashboards AI/BI publicados para as áreas e Genie como porta de entrada de autoatendimento analítico.
- **Próximo passo sugerido:** (1) habilitar o preview do Genie Ontology com o time de conta; (2) eleger 1 domínio piloto e 3–5 perguntas de alto valor para uma prova de conceito acompanhada.

*Base sintética criada exclusivamente para fins de treinamento, no formato MetLife (seguros de vida, previdência, sinistros e distribuição).*
