# Databricks notebook source
# MAGIC %md
# MAGIC # 🎓 MetLife — AI/BI + Genie · Aula guiada (estilo Databricks Academy)
# MAGIC ### Sessão 2 · **Databricks para Usuário de Negócio** · 11h00–13h00 (BRA)
# MAGIC
# MAGIC Bem-vindo(a)! Este notebook **é a aula**: um passo a passo sequencial que acompanha a **agenda** e conduz você da plataforma ao **Genie** e ao **Genie Ontology**, usando dados de **seguros** (Vida & Previdência, Sinistros & Fraude, Distribuição).
# MAGIC
# MAGIC > 📅 **Contexto do dia:** Sessão 1 (09h–11h) — *Databricks para Usuário Técnico / Data Engineering*. **Sessão 2 (11h–13h) — esta aula, para Usuário de Negócio.** Foco em **autoatendimento sem código**: dashboards e perguntas em linguagem natural. Os trechos de SQL neste notebook são o **gabarito do instrutor** (bastidores) — como participante, você trabalha nas telas do **Dashboard** e do **Genie**.
# MAGIC
# MAGIC ## 🗓️ Agenda (2h)
# MAGIC
# MAGIC | Horário | Bloco | Nesta aula |
# MAGIC |---|---|---|
# MAGIC | 11h00–11h10 | **1 · Abertura e visão de AI/BI para seguros** | contexto + tour rápido |
# MAGIC | 11h10–11h40 | **2 · Dashboards AI/BI** (mão na massa) | Lab A — seu primeiro dashboard |
# MAGIC | 11h40–12h20 | **3 · Genie — conversa em linguagem natural** (mão na massa) | Lab B — perguntar e confiar |
# MAGIC | 12h20–12h45 | **4 · Genie confiável — curadoria e camada semântica** | Labs C e E |
# MAGIC | 12h45–12h55 | **5 · Casos de uso MetLife** | Lab D — fraude, distribuição, persistência |
# MAGIC | 12h55–13h00 | **6 · Encerramento e próximos passos** | jornada de adoção |
# MAGIC
# MAGIC ## 🎯 Objetivos de aprendizagem
# MAGIC Ao final você será capaz de: navegar a plataforma; **construir um dashboard AI/BI** sem código; **conversar com o Genie** e interpretar as respostas; e entender o que torna a resposta *confiável* (instruções, sinônimos, **Metric Views**, **Domain**, **glossário**) e como isso alimenta o **Genie Ontology**.
# MAGIC
# MAGIC ## 👥 Como usar
# MAGIC - **Instrutor(a):** execute a **Parte 0 (preparação)** *antes* da aula (ou reaproveite o ambiente da Sessão 1). Conduza bloco a bloco pelo relógio.
# MAGIC - **Participante (negócio):** você **não precisa escrever SQL**. Siga os laboratórios nas telas do Dashboard e do Genie. Ícones: 🧑‍🏫 explicação · ▶️ o instrutor executa (gabarito) · 🧪 laboratório (você faz) · ✅ checkpoint.
# MAGIC
# MAGIC > **Ambiente:** workspace `fevm-moi-ai` · catálogo `moi_ai_catalog.metlife_workshop`. Dados 100% sintéticos, só para treinamento.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # ⚙️ Parte 0 — Preparação do ambiente (pré-aula)
# MAGIC
# MAGIC > **Instrutor(a):** execute esta parte inteira **antes** da aula (leva ~1–2 min no serverless). Ela cria schema, 7 tabelas, 3 Metric Views, glossário e Domain. É idempotente (`CREATE OR REPLACE`). Durante a aula, esta parte pode ficar **recolhida**.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS moi_ai_catalog.metlife_workshop
# MAGIC COMMENT 'Workshop AI/BI + Genie MetLife - dados sinteticos de seguros';
# MAGIC USE CATALOG moi_ai_catalog;
# MAGIC USE SCHEMA metlife_workshop;

# COMMAND ----------

# MAGIC %md
# MAGIC **0.1 · Dados** — 7 tabelas geradas 100% em SQL determinístico.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.produtos AS
# MAGIC SELECT * FROM VALUES
# MAGIC   (1,  'Vida Individual Premiado',      'Vida',        'Vida Individual',      0.030, 50000,  2000000),
# MAGIC   (2,  'Vida em Grupo Empresarial',     'Vida',        'Vida em Grupo',        0.025, 30000,  1000000),
# MAGIC   (3,  'Vida Mulher',                   'Vida',        'Vida Individual',      0.028, 40000,  1500000),
# MAGIC   (4,  'Seguro Prestamista',            'Vida',        'Prestamista',          0.020, 10000,  500000),
# MAGIC   (5,  'Vida Senior 60+',               'Vida',        'Vida Individual',      0.045, 20000,  800000),
# MAGIC   (6,  'Acidentes Pessoais',            'Vida',        'Acidentes Pessoais',   0.018, 15000,  600000),
# MAGIC   (7,  'PGBL Tradicional',              'Previdencia', 'PGBL',                 0.015, 0,       0),
# MAGIC   (8,  'PGBL Multimercado',             'Previdencia', 'PGBL',                 0.020, 0,       0),
# MAGIC   (9,  'VGBL Renda Fixa',               'Previdencia', 'VGBL',                 0.012, 0,       0),
# MAGIC   (10, 'VGBL Multimercado',             'Previdencia', 'VGBL',                 0.018, 0,       0),
# MAGIC   (11, 'VGBL Junior',                   'Previdencia', 'VGBL',                 0.015, 0,       0),
# MAGIC   (12, 'Previdencia Corporativa PJ',    'Previdencia', 'PGBL',                 0.010, 0,       0)
# MAGIC AS t(produto_id, nome_produto, linha_negocio, tipo_produto, taxa_carregamento, capital_min, capital_max);

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.corretores AS
# MAGIC WITH base AS (
# MAGIC   SELECT explode(sequence(1, 150)) AS corretor_id
# MAGIC ),
# MAGIC nomes AS (
# MAGIC   SELECT array('Ana','Bruno','Carla','Diego','Eduarda','Felipe','Gabriela','Henrique','Isabela','Joao',
# MAGIC                'Karina','Lucas','Mariana','Nelson','Olivia','Paulo','Renata','Sergio','Tatiana','Vinicius') AS fn,
# MAGIC          array('Silva','Souza','Oliveira','Santos','Pereira','Costa','Rodrigues','Almeida','Nascimento','Lima',
# MAGIC                'Araujo','Ferreira','Carvalho','Gomes','Martins','Ribeiro','Barbosa','Rocha','Dias','Moraes') AS ln,
# MAGIC          array('SP','RJ','MG','RS','PR','SC','BA','PE','CE','DF','GO','ES','PA','AM') AS ufs
# MAGIC )
# MAGIC SELECT
# MAGIC   b.corretor_id,
# MAGIC   concat('COR', lpad(cast(b.corretor_id AS string), 5, '0')) AS codigo_corretor,
# MAGIC   concat(element_at(n.fn, pmod(hash(b.corretor_id * 7), 20) + 1), ' ',
# MAGIC          element_at(n.ln, pmod(hash(b.corretor_id * 13), 20) + 1)) AS nome_corretor,
# MAGIC   element_at(array('Corretor Independente','Bancassurance','Canal Digital','Corporate Beneficios'),
# MAGIC              pmod(hash(b.corretor_id * 3), 4) + 1) AS canal_distribuicao,
# MAGIC   element_at(n.ufs, pmod(hash(b.corretor_id * 5), 14) + 1) AS uf,
# MAGIC   CASE element_at(n.ufs, pmod(hash(b.corretor_id * 5), 14) + 1)
# MAGIC     WHEN 'SP' THEN 'Sudeste' WHEN 'RJ' THEN 'Sudeste' WHEN 'MG' THEN 'Sudeste' WHEN 'ES' THEN 'Sudeste'
# MAGIC     WHEN 'RS' THEN 'Sul' WHEN 'PR' THEN 'Sul' WHEN 'SC' THEN 'Sul'
# MAGIC     WHEN 'BA' THEN 'Nordeste' WHEN 'PE' THEN 'Nordeste' WHEN 'CE' THEN 'Nordeste'
# MAGIC     WHEN 'DF' THEN 'Centro-Oeste' WHEN 'GO' THEN 'Centro-Oeste'
# MAGIC     WHEN 'PA' THEN 'Norte' WHEN 'AM' THEN 'Norte' ELSE 'Outros' END AS regiao,
# MAGIC   date_add(DATE'2015-01-01', pmod(hash(b.corretor_id * 17), 3650)) AS data_admissao,
# MAGIC   (500000 + pmod(hash(b.corretor_id * 11), 20) * 150000) AS meta_anual_producao
# MAGIC FROM base b CROSS JOIN nomes n;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.clientes AS
# MAGIC WITH base AS (
# MAGIC   SELECT explode(sequence(1, 5000)) AS cliente_id
# MAGIC ),
# MAGIC dim AS (
# MAGIC   SELECT array('Alexandre','Beatriz','Camila','Daniel','Elaine','Fabio','Giovana','Hugo','Ingrid','Jorge',
# MAGIC                'Kelly','Leandro','Marcia','Natalia','Otavio','Patricia','Rafael','Sabrina','Thiago','Vanessa',
# MAGIC                'William','Yara','Bruno','Carolina','Rodrigo') AS fn,
# MAGIC          array('Almeida','Barros','Cardoso','Duarte','Esteves','Freitas','Guimaraes','Henriques','Imperio','Junqueira',
# MAGIC                'Klein','Lopes','Machado','Nogueira','Pinto','Queiroz','Ramos','Teixeira','Vasconcelos','Xavier') AS ln,
# MAGIC          array('Sao Paulo','Rio de Janeiro','Belo Horizonte','Porto Alegre','Curitiba','Florianopolis','Salvador',
# MAGIC                'Recife','Fortaleza','Brasilia','Goiania','Vitoria','Belem','Manaus') AS cidades,
# MAGIC          array('SP','RJ','MG','RS','PR','SC','BA','PE','CE','DF','GO','ES','PA','AM') AS ufs
# MAGIC )
# MAGIC SELECT
# MAGIC   b.cliente_id,
# MAGIC   concat('CLI', lpad(cast(b.cliente_id AS string), 7, '0')) AS codigo_cliente,
# MAGIC   concat(element_at(d.fn, pmod(hash(b.cliente_id * 7), 25) + 1), ' ',
# MAGIC          element_at(d.ln, pmod(hash(b.cliente_id * 19), 20) + 1)) AS nome_cliente,
# MAGIC   CASE WHEN pmod(hash(b.cliente_id * 2), 2) = 0 THEN 'F' ELSE 'M' END AS sexo,
# MAGIC   (22 + pmod(hash(b.cliente_id * 23), 55)) AS idade,
# MAGIC   date_sub(DATE'2026-09-01', (22 + pmod(hash(b.cliente_id * 23), 55)) * 365) AS data_nascimento,
# MAGIC   element_at(d.cidades, pmod(hash(b.cliente_id * 5), 14) + 1) AS cidade,
# MAGIC   element_at(d.ufs, pmod(hash(b.cliente_id * 5), 14) + 1) AS uf,
# MAGIC   CASE element_at(d.ufs, pmod(hash(b.cliente_id * 5), 14) + 1)
# MAGIC     WHEN 'SP' THEN 'Sudeste' WHEN 'RJ' THEN 'Sudeste' WHEN 'MG' THEN 'Sudeste' WHEN 'ES' THEN 'Sudeste'
# MAGIC     WHEN 'RS' THEN 'Sul' WHEN 'PR' THEN 'Sul' WHEN 'SC' THEN 'Sul'
# MAGIC     WHEN 'BA' THEN 'Nordeste' WHEN 'PE' THEN 'Nordeste' WHEN 'CE' THEN 'Nordeste'
# MAGIC     WHEN 'DF' THEN 'Centro-Oeste' WHEN 'GO' THEN 'Centro-Oeste'
# MAGIC     WHEN 'PA' THEN 'Norte' WHEN 'AM' THEN 'Norte' ELSE 'Outros' END AS regiao,
# MAGIC   round(2500 + pmod(hash(b.cliente_id * 29), 100) * 480 + pmod(hash(b.cliente_id * 41), 1500), 2) AS renda_mensal,
# MAGIC   element_at(array('Massificado','Classico','Premier','Private'),
# MAGIC              CASE WHEN pmod(hash(b.cliente_id * 31), 100) < 60 THEN 1
# MAGIC                   WHEN pmod(hash(b.cliente_id * 31), 100) < 85 THEN 2
# MAGIC                   WHEN pmod(hash(b.cliente_id * 31), 100) < 97 THEN 3 ELSE 4 END) AS segmento_cliente,
# MAGIC   date_add(DATE'2016-01-01', pmod(hash(b.cliente_id * 37), 3400)) AS data_cadastro
# MAGIC FROM base b CROSS JOIN dim d;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.apolices AS
# MAGIC WITH base AS (
# MAGIC   SELECT explode(sequence(1, 8000)) AS apolice_id
# MAGIC ),
# MAGIC j AS (
# MAGIC   SELECT
# MAGIC     b.apolice_id,
# MAGIC     pmod(hash(b.apolice_id * 3), 5000) + 1 AS cliente_id,
# MAGIC     pmod(hash(b.apolice_id * 7), 150) + 1  AS corretor_id,
# MAGIC     pmod(hash(b.apolice_id * 11), 12) + 1  AS produto_id,
# MAGIC     date_add(DATE'2018-01-01', pmod(hash(b.apolice_id * 13), 2800)) AS data_emissao
# MAGIC   FROM base b
# MAGIC ),
# MAGIC enr AS (
# MAGIC   SELECT
# MAGIC     j.apolice_id,
# MAGIC     concat('APL', lpad(cast(j.apolice_id AS string), 8, '0')) AS numero_apolice,
# MAGIC     j.cliente_id, j.corretor_id, j.produto_id,
# MAGIC     p.nome_produto, p.linha_negocio, p.tipo_produto,
# MAGIC     c.canal_distribuicao, c.regiao, c.uf,
# MAGIC     j.data_emissao,
# MAGIC     date_add(j.data_emissao, (5 + pmod(hash(j.apolice_id * 29), 25)) * 365) AS data_fim_vigencia,
# MAGIC     CASE
# MAGIC       WHEN pmod(hash(j.apolice_id * 23), 100) < 70 THEN 'Ativa'
# MAGIC       WHEN pmod(hash(j.apolice_id * 23), 100) < 88 THEN 'Cancelada'
# MAGIC       WHEN pmod(hash(j.apolice_id * 23), 100) < 95 THEN 'Suspensa'
# MAGIC       ELSE 'Quitada' END AS status_apolice,
# MAGIC     CASE WHEN p.linha_negocio = 'Vida'
# MAGIC          THEN p.capital_min + pmod(hash(j.apolice_id * 17), greatest(p.capital_max - p.capital_min, 1))
# MAGIC          ELSE 0 END AS capital_segurado,
# MAGIC     p.taxa_carregamento,
# MAGIC     element_at(array('Debito Automatico','Boleto','Cartao de Credito','Consignado'),
# MAGIC                pmod(hash(j.apolice_id * 31), 4) + 1) AS forma_pagamento
# MAGIC   FROM j
# MAGIC   JOIN moi_ai_catalog.metlife_workshop.produtos p   ON j.produto_id = p.produto_id
# MAGIC   JOIN moi_ai_catalog.metlife_workshop.corretores c ON j.corretor_id = c.corretor_id
# MAGIC )
# MAGIC SELECT
# MAGIC   e.*,
# MAGIC   CASE WHEN e.linha_negocio = 'Vida'
# MAGIC        THEN round(e.capital_segurado * e.taxa_carregamento / 12 + pmod(hash(e.apolice_id * 43), 150), 2)
# MAGIC        ELSE round(100 + pmod(hash(e.apolice_id * 47), 2900), 2) END AS premio_mensal,
# MAGIC   CASE WHEN e.linha_negocio = 'Previdencia'
# MAGIC        THEN round((100 + pmod(hash(e.apolice_id * 47), 2900))
# MAGIC                   * greatest(months_between(least(DATE'2026-09-01', e.data_fim_vigencia), e.data_emissao), 1)
# MAGIC                   * 1.06, 2)
# MAGIC        ELSE 0 END AS reserva_acumulada
# MAGIC FROM enr e;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.premios AS
# MAGIC WITH meses AS (
# MAGIC   SELECT explode(sequence(0, 23)) AS m
# MAGIC ),
# MAGIC comp AS (
# MAGIC   SELECT m, add_months(DATE'2024-09-01', m) AS competencia FROM meses
# MAGIC ),
# MAGIC gen AS (
# MAGIC   SELECT
# MAGIC     a.apolice_id,
# MAGIC     a.cliente_id,
# MAGIC     a.linha_negocio,
# MAGIC     a.canal_distribuicao,
# MAGIC     a.regiao,
# MAGIC     c.competencia,
# MAGIC     c.m,
# MAGIC     a.premio_mensal,
# MAGIC     a.status_apolice
# MAGIC   FROM moi_ai_catalog.metlife_workshop.apolices a
# MAGIC   CROSS JOIN comp c
# MAGIC   WHERE c.competencia >= trunc(a.data_emissao, 'MM')
# MAGIC     AND NOT (a.status_apolice = 'Cancelada' AND c.m >= 18)
# MAGIC     AND a.premio_mensal > 0
# MAGIC )
# MAGIC SELECT
# MAGIC   concat('PRM', lpad(cast(g.apolice_id AS string), 8, '0'), '-', date_format(g.competencia, 'yyyyMM')) AS id_pagamento,
# MAGIC   g.apolice_id,
# MAGIC   g.cliente_id,
# MAGIC   g.linha_negocio,
# MAGIC   g.canal_distribuicao,
# MAGIC   g.regiao,
# MAGIC   g.competencia,
# MAGIC   g.premio_mensal AS valor_devido,
# MAGIC   date_add(g.competencia, 9) AS data_vencimento,
# MAGIC   CASE
# MAGIC     WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 85 THEN 'Pago'
# MAGIC     WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 95 THEN 'Pago em Atraso'
# MAGIC     ELSE 'Inadimplente' END AS status_pagamento,
# MAGIC   CASE
# MAGIC     WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 85
# MAGIC       THEN date_add(g.competencia, 9 - pmod(hash(g.apolice_id * 100 + g.m), 5))
# MAGIC     WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 95
# MAGIC       THEN date_add(g.competencia, 9 + 5 + pmod(hash(g.apolice_id * 100 + g.m), 25))
# MAGIC     ELSE NULL END AS data_pagamento,
# MAGIC   CASE
# MAGIC     WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 85 THEN g.premio_mensal
# MAGIC     WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 95 THEN g.premio_mensal
# MAGIC     ELSE 0 END AS valor_pago
# MAGIC FROM gen g;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.sinistros AS
# MAGIC WITH base AS (
# MAGIC   SELECT explode(sequence(1, 2500)) AS sinistro_id
# MAGIC ),
# MAGIC j AS (
# MAGIC   SELECT
# MAGIC     s.sinistro_id,
# MAGIC     pmod(hash(s.sinistro_id * 3), 8000) + 1 AS apolice_id
# MAGIC   FROM base s
# MAGIC ),
# MAGIC enr AS (
# MAGIC   SELECT
# MAGIC     j.sinistro_id,
# MAGIC     j.apolice_id,
# MAGIC     a.cliente_id, a.produto_id, a.nome_produto, a.linha_negocio,
# MAGIC     a.canal_distribuicao, a.regiao, a.uf, a.capital_segurado, a.reserva_acumulada, a.data_emissao,
# MAGIC     date_add(a.data_emissao, 30 + pmod(hash(j.sinistro_id * 13),
# MAGIC              greatest(datediff(DATE'2026-08-31', a.data_emissao) - 30, 60))) AS data_ocorrencia
# MAGIC   FROM j
# MAGIC   JOIN moi_ai_catalog.metlife_workshop.apolices a ON j.apolice_id = a.apolice_id
# MAGIC ),
# MAGIC sin AS (
# MAGIC   SELECT
# MAGIC     e.*,
# MAGIC     CASE WHEN e.linha_negocio = 'Vida'
# MAGIC          THEN element_at(array('Morte Natural','Morte Acidental','Invalidez Permanente','Doenca Grave'),
# MAGIC                          pmod(hash(e.sinistro_id * 7), 4) + 1)
# MAGIC          ELSE element_at(array('Resgate Total','Resgate Parcial','Portabilidade','Pensao por Morte'),
# MAGIC                          pmod(hash(e.sinistro_id * 7), 4) + 1) END AS tipo_sinistro,
# MAGIC     datediff(e.data_ocorrencia, e.data_emissao) AS dias_desde_emissao,
# MAGIC     CASE
# MAGIC       WHEN pmod(hash(e.sinistro_id * 23), 100) < 65 THEN 'Pago'
# MAGIC       WHEN pmod(hash(e.sinistro_id * 23), 100) < 80 THEN 'Em Analise'
# MAGIC       WHEN pmod(hash(e.sinistro_id * 23), 100) < 92 THEN 'Negado'
# MAGIC       ELSE 'Aprovado' END AS status_sinistro,
# MAGIC     (10 + pmod(hash(e.sinistro_id * 29), 110)) AS dias_liquidacao_base
# MAGIC   FROM enr e
# MAGIC )
# MAGIC SELECT
# MAGIC   concat('SIN', lpad(cast(sinistro_id AS string), 8, '0')) AS numero_sinistro,
# MAGIC   sinistro_id, apolice_id, cliente_id, produto_id, nome_produto, linha_negocio,
# MAGIC   canal_distribuicao, regiao, uf,
# MAGIC   tipo_sinistro,
# MAGIC   data_ocorrencia,
# MAGIC   date_add(data_ocorrencia, pmod(hash(sinistro_id * 17), 20)) AS data_aviso,
# MAGIC   CASE WHEN status_sinistro IN ('Pago','Negado','Aprovado')
# MAGIC        THEN date_add(date_add(data_ocorrencia, pmod(hash(sinistro_id * 17), 20)), dias_liquidacao_base)
# MAGIC        ELSE NULL END AS data_liquidacao,
# MAGIC   CASE WHEN status_sinistro IN ('Pago','Negado','Aprovado') THEN dias_liquidacao_base ELSE NULL END AS dias_liquidacao,
# MAGIC   status_sinistro,
# MAGIC   round(CASE WHEN linha_negocio = 'Vida'
# MAGIC              THEN greatest(capital_segurado * (0.3 + pmod(hash(sinistro_id * 19), 70) / 100.0), 5000)
# MAGIC              ELSE greatest(reserva_acumulada * (0.2 + pmod(hash(sinistro_id * 19), 80) / 100.0), 3000) END, 2) AS valor_reclamado,
# MAGIC   round(CASE WHEN status_sinistro IN ('Pago','Aprovado')
# MAGIC              THEN CASE WHEN linha_negocio = 'Vida'
# MAGIC                        THEN greatest(capital_segurado * (0.3 + pmod(hash(sinistro_id * 19), 70) / 100.0), 5000)
# MAGIC                        ELSE greatest(reserva_acumulada * (0.2 + pmod(hash(sinistro_id * 19), 80) / 100.0), 3000) END
# MAGIC              ELSE 0 END, 2) AS valor_pago,
# MAGIC   CASE WHEN (dias_desde_emissao < 180 AND pmod(hash(sinistro_id * 37), 100) < 45)
# MAGIC             OR pmod(hash(sinistro_id * 41), 100) < 5
# MAGIC        THEN true ELSE false END AS suspeita_fraude,
# MAGIC   dias_desde_emissao
# MAGIC FROM sin;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.sinistros_fraude_score AS
# MAGIC SELECT
# MAGIC   s.numero_sinistro,
# MAGIC   s.sinistro_id,
# MAGIC   s.apolice_id,
# MAGIC   s.tipo_sinistro,
# MAGIC   s.valor_reclamado,
# MAGIC   s.dias_desde_emissao,
# MAGIC   s.suspeita_fraude,
# MAGIC   CASE WHEN s.suspeita_fraude
# MAGIC        THEN 60 + pmod(hash(s.sinistro_id * 53), 40)
# MAGIC        ELSE pmod(hash(s.sinistro_id * 59), 56) END AS score_fraude,
# MAGIC   CASE
# MAGIC     WHEN (CASE WHEN s.suspeita_fraude THEN 60 + pmod(hash(s.sinistro_id * 53), 40)
# MAGIC                ELSE pmod(hash(s.sinistro_id * 59), 56) END) >= 70 THEN 'Alto'
# MAGIC     WHEN (CASE WHEN s.suspeita_fraude THEN 60 + pmod(hash(s.sinistro_id * 53), 40)
# MAGIC                ELSE pmod(hash(s.sinistro_id * 59), 56) END) >= 40 THEN 'Medio'
# MAGIC     ELSE 'Baixo' END AS nivel_risco,
# MAGIC   CASE
# MAGIC     WHEN s.dias_desde_emissao < 180 THEN 'Sinistro logo apos emissao da apolice'
# MAGIC     WHEN s.valor_reclamado > 500000 THEN 'Valor reclamado acima do padrao'
# MAGIC     WHEN s.suspeita_fraude THEN 'Padrao atipico de sinistralidade'
# MAGIC     ELSE 'Sem alerta relevante' END AS motivo_alerta_principal
# MAGIC FROM moi_ai_catalog.metlife_workshop.sinistros s;

# COMMAND ----------

# MAGIC %md
# MAGIC **0.2 · Camada semântica** — 3 Metric Views governados (carteira, arrecadação, sinistralidade).

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW moi_ai_catalog.metlife_workshop.mv_carteira
# MAGIC WITH METRICS
# MAGIC LANGUAGE YAML
# MAGIC AS $$
# MAGIC version: 1.1
# MAGIC comment: "Metricas governadas de carteira e producao de apolices (Vida e Previdencia) - MetLife"
# MAGIC source: "(SELECT a.apolice_id, a.linha_negocio, a.nome_produto, a.tipo_produto, a.status_apolice, a.forma_pagamento, a.canal_distribuicao, a.regiao, a.uf, a.data_emissao, a.premio_mensal, a.capital_segurado, a.reserva_acumulada, c.segmento_cliente, c.renda_mensal, co.nome_corretor FROM moi_ai_catalog.metlife_workshop.apolices a JOIN moi_ai_catalog.metlife_workshop.clientes c ON a.cliente_id = c.cliente_id JOIN moi_ai_catalog.metlife_workshop.corretores co ON a.corretor_id = co.corretor_id)"
# MAGIC dimensions: [{name: Linha de Negocio, expr: "linha_negocio", synonyms: ["ramo", "linha"]}, {name: Produto, expr: "nome_produto"}, {name: Tipo de Produto, expr: "tipo_produto"}, {name: Status da Apolice, expr: "status_apolice", synonyms: ["situacao"]}, {name: Forma de Pagamento, expr: "forma_pagamento"}, {name: Canal de Distribuicao, expr: "canal_distribuicao", synonyms: ["canal"]}, {name: Regiao, expr: "regiao"}, {name: UF, expr: "uf", synonyms: ["estado"]}, {name: Mes de Emissao, expr: "DATE_TRUNC('MONTH', data_emissao)"}, {name: Segmento do Cliente, expr: "segmento_cliente", synonyms: ["segmento"]}, {name: Corretor, expr: "nome_corretor"}]
# MAGIC measures: [{name: Apolices, expr: "COUNT(1)", synonyms: ["numero de apolices"]}, {name: Apolices Ativas, expr: "COUNT(1) FILTER (WHERE status_apolice = 'Ativa')"}, {name: Premio Mensal Total, expr: "SUM(premio_mensal)", synonyms: ["premio", "arrecadacao potencial"]}, {name: Capital Segurado Total, expr: "SUM(capital_segurado)", synonyms: ["capital", "importancia segurada"]}, {name: Reserva Acumulada Total, expr: "SUM(reserva_acumulada)", synonyms: ["reserva", "saldo"]}, {name: Ticket Medio de Premio, expr: "MEASURE(`Premio Mensal Total`) / MEASURE(`Apolices`)"}, {name: Taxa de Cancelamento, expr: "COUNT(1) FILTER (WHERE status_apolice = 'Cancelada') * 1.0 / COUNT(1)", synonyms: ["cancelamento", "churn"]}]
# MAGIC $$

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW moi_ai_catalog.metlife_workshop.mv_arrecadacao
# MAGIC WITH METRICS
# MAGIC LANGUAGE YAML
# MAGIC AS $$
# MAGIC version: 1.1
# MAGIC comment: "Metricas governadas de arrecadacao, inadimplencia e persistencia de premios - MetLife"
# MAGIC source: moi_ai_catalog.metlife_workshop.premios
# MAGIC dimensions: [{name: Competencia, expr: "competencia", synonyms: ["mes", "periodo"]}, {name: Linha de Negocio, expr: "linha_negocio", synonyms: ["ramo"]}, {name: Canal de Distribuicao, expr: "canal_distribuicao", synonyms: ["canal"]}, {name: Regiao, expr: "regiao"}, {name: Status do Pagamento, expr: "status_pagamento", synonyms: ["situacao do pagamento"]}]
# MAGIC measures: [{name: Premios Emitidos, expr: "COUNT(1)", synonyms: ["quantidade de premios", "cobrancas"]}, {name: Valor Devido, expr: "SUM(valor_devido)"}, {name: Valor Arrecadado, expr: "SUM(valor_pago)", synonyms: ["arrecadacao", "premio pago"]}, {name: Pagamentos Inadimplentes, expr: "COUNT(1) FILTER (WHERE status_pagamento = 'Inadimplente')", synonyms: ["inadimplentes"]}, {name: Taxa de Inadimplencia, expr: "COUNT(1) FILTER (WHERE status_pagamento = 'Inadimplente') * 1.0 / COUNT(1)", synonyms: ["inadimplencia"]}, {name: Taxa de Arrecadacao, expr: "SUM(valor_pago) / SUM(valor_devido)", synonyms: ["persistencia", "taxa de pagamento"]}]
# MAGIC $$

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW moi_ai_catalog.metlife_workshop.mv_sinistralidade
# MAGIC WITH METRICS
# MAGIC LANGUAGE YAML
# MAGIC AS $$
# MAGIC version: 1.1
# MAGIC comment: "Metricas governadas de sinistros, tempo de liquidacao e fraude - MetLife"
# MAGIC source: "(SELECT s.sinistro_id, s.tipo_sinistro, s.linha_negocio, s.nome_produto, s.status_sinistro, s.regiao, s.uf, s.data_ocorrencia, s.valor_reclamado, s.valor_pago, s.dias_liquidacao, s.suspeita_fraude, f.nivel_risco, f.score_fraude FROM moi_ai_catalog.metlife_workshop.sinistros s JOIN moi_ai_catalog.metlife_workshop.sinistros_fraude_score f ON s.sinistro_id = f.sinistro_id)"
# MAGIC dimensions: [{name: Tipo de Sinistro, expr: "tipo_sinistro", synonyms: ["causa"]}, {name: Linha de Negocio, expr: "linha_negocio", synonyms: ["ramo"]}, {name: Produto, expr: "nome_produto"}, {name: Status do Sinistro, expr: "status_sinistro", synonyms: ["situacao"]}, {name: Regiao, expr: "regiao"}, {name: UF, expr: "uf", synonyms: ["estado"]}, {name: Mes de Ocorrencia, expr: "DATE_TRUNC('MONTH', data_ocorrencia)"}, {name: Nivel de Risco de Fraude, expr: "nivel_risco", synonyms: ["risco de fraude", "risco"]}]
# MAGIC measures: [{name: Sinistros, expr: "COUNT(1)", synonyms: ["numero de sinistros", "quantidade de sinistros"]}, {name: Valor Reclamado, expr: "SUM(valor_reclamado)"}, {name: Valor Pago em Sinistros, expr: "SUM(valor_pago)", synonyms: ["indenizacao", "valor pago"]}, {name: Tempo Medio de Liquidacao, expr: "AVG(dias_liquidacao)", synonyms: ["prazo de liquidacao", "tempo de regulacao"]}, {name: Sinistros Suspeitos, expr: "COUNT(1) FILTER (WHERE suspeita_fraude = true)", synonyms: ["sinistros com suspeita de fraude"]}, {name: Taxa de Fraude, expr: "COUNT(1) FILTER (WHERE suspeita_fraude = true) * 1.0 / COUNT(1)", synonyms: ["percentual de fraude"]}, {name: Sinistros de Alto Risco, expr: "COUNT(1) FILTER (WHERE nivel_risco = 'Alto')"}]
# MAGIC $$

# COMMAND ----------

# MAGIC %md
# MAGIC **0.3 · Domain + Glossário** — blocos governados do Genie Ontology.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.glossario_negocio
# MAGIC COMMENT 'Glossario de negocio certificado do dominio Seguros MetLife - termos canonicos, definicoes, sinonimos e metrica/tabela de referencia. Alimenta o Genie Ontology.'
# MAGIC AS SELECT * FROM VALUES
# MAGIC   ('Premio', 'Valor pago periodicamente pelo segurado para manter a cobertura vigente.', 'premio mensal, mensalidade', 'mv_carteira.Premio Mensal Total'),
# MAGIC   ('Capital Segurado', 'Importancia segurada: valor de cobertura pago em caso de sinistro (apenas Vida).', 'importancia segurada, cobertura', 'mv_carteira.Capital Segurado Total'),
# MAGIC   ('Reserva Acumulada', 'Saldo acumulado do participante em produtos de Previdencia (PGBL/VGBL).', 'saldo, provisao', 'mv_carteira.Reserva Acumulada Total'),
# MAGIC   ('Ticket Medio', 'Premio mensal medio por apolice.', 'premio medio', 'mv_carteira.Ticket Medio de Premio'),
# MAGIC   ('Taxa de Cancelamento', 'Percentual de apolices canceladas sobre o total (churn de carteira).', 'churn, cancelamento', 'mv_carteira.Taxa de Cancelamento'),
# MAGIC   ('Inadimplencia', 'Percentual de premios com status Inadimplente sobre o total de cobrancas.', 'default, atraso', 'mv_arrecadacao.Taxa de Inadimplencia'),
# MAGIC   ('Persistencia', 'Taxa de arrecadacao: valor efetivamente pago dividido pelo valor devido.', 'taxa de arrecadacao, retencao de premio', 'mv_arrecadacao.Taxa de Arrecadacao'),
# MAGIC   ('Sinistralidade', 'Relacao entre valor pago em sinistros e premios ganhos no periodo (loss ratio). Cruza mv_sinistralidade x mv_arrecadacao.', 'loss ratio, indice de sinistralidade', 'mv_sinistralidade.Valor Pago em Sinistros / mv_arrecadacao.Valor Arrecadado'),
# MAGIC   ('Tempo de Liquidacao', 'Numero de dias entre o aviso e a liquidacao (regulacao) de um sinistro.', 'prazo de regulacao, tempo de regulacao', 'mv_sinistralidade.Tempo Medio de Liquidacao'),
# MAGIC   ('Suspeita de Fraude', 'Sinistro sinalizado como potencial fraude por regras/score (ex.: ocorrencia < 180 dias da emissao).', 'fraude, alerta', 'mv_sinistralidade.Taxa de Fraude'),
# MAGIC   ('Nivel de Risco de Fraude', 'Classificacao do score de fraude do sinistro em Baixo, Medio ou Alto.', 'risco de fraude', 'sinistros_fraude_score.nivel_risco'),
# MAGIC   ('Canal de Distribuicao', 'Meio pelo qual a apolice foi comercializada: Corretor Independente, Bancassurance, Canal Digital ou Corporate Beneficios.', 'canal', 'mv_carteira.Canal de Distribuicao'),
# MAGIC   ('Segmento do Cliente', 'Segmentacao do segurado: Massificado, Classico, Premier ou Private.', 'segmento', 'mv_carteira.Segmento do Cliente')
# MAGIC AS t(termo, definicao, sinonimos, metrica_ou_coluna_referencia);

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 14_domain_tags.sql
# MAGIC -- Aplica o "Domain" do Genie Ontology via tags de Unity Catalog.
# MAGIC -- Observacao: neste ambiente ha tag policies governadas — a chave `camada`
# MAGIC -- so aceita bronze/silver/gold. Ajuste as chaves/valores conforme as
# MAGIC -- politicas de tags do seu metastore.
# MAGIC
# MAGIC -- Schema (dominio de negocio)
# MAGIC ALTER SCHEMA moi_ai_catalog.metlife_workshop
# MAGIC   SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'certificado' = 'workshop');
# MAGIC
# MAGIC -- Metric Views (camada semantica gold, certificada)
# MAGIC ALTER VIEW moi_ai_catalog.metlife_workshop.mv_carteira
# MAGIC   SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'camada' = 'gold', 'certificado' = 'sim');
# MAGIC ALTER VIEW moi_ai_catalog.metlife_workshop.mv_arrecadacao
# MAGIC   SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'camada' = 'gold', 'certificado' = 'sim');
# MAGIC ALTER VIEW moi_ai_catalog.metlife_workshop.mv_sinistralidade
# MAGIC   SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'camada' = 'gold', 'certificado' = 'sim');
# MAGIC
# MAGIC -- Tabelas-fato (subdominios / areas de negocio)
# MAGIC ALTER TABLE moi_ai_catalog.metlife_workshop.apolices
# MAGIC   SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'area_negocio' = 'Carteira e Distribuicao');
# MAGIC ALTER TABLE moi_ai_catalog.metlife_workshop.premios
# MAGIC   SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'area_negocio' = 'Arrecadacao');
# MAGIC ALTER TABLE moi_ai_catalog.metlife_workshop.sinistros
# MAGIC   SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'area_negocio' = 'Sinistros e Fraude');
# MAGIC
# MAGIC -- Glossario certificado
# MAGIC ALTER TABLE moi_ai_catalog.metlife_workshop.glossario_negocio
# MAGIC   SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'certificado' = 'sim', 'tipo' = 'glossario');

# COMMAND ----------

# MAGIC %md
# MAGIC **0.4 · ✅ Checkpoint de preparação** — confira volumes e o gabarito.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'apolices' t, count(*) n FROM apolices
# MAGIC UNION ALL SELECT 'premios', count(*) FROM premios
# MAGIC UNION ALL SELECT 'sinistros', count(*) FROM sinistros
# MAGIC UNION ALL SELECT 'clientes', count(*) FROM clientes ORDER BY t;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 1 · Abertura e a visão de AI/BI para seguros
# MAGIC **11h00–11h10**
# MAGIC
# MAGIC 🧑‍🏫 **A ideia central.** Áreas de negócio vivem esperando relatórios. **AI/BI + Genie** invertem isso: qualquer pessoa faz perguntas em **linguagem natural** sobre dados **governados** e recebe tabelas, gráficos e o **SQL** por trás — com a segurança do Unity Catalog.
# MAGIC
# MAGIC Nesta aula usamos uma seguradora fictícia (formato MetLife) com três domínios: **Carteira/Distribuição**, **Arrecadação** e **Sinistros/Fraude**.
# MAGIC
# MAGIC ▶️ **Tour do catálogo** — veja as tabelas e a cara dos dados.

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG moi_ai_catalog; USE SCHEMA metlife_workshop;
# MAGIC SHOW TABLES;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Uma espiada nas apólices (Vida e Previdência)
# MAGIC SELECT numero_apolice, linha_negocio, nome_produto, status_apolice,
# MAGIC        capital_segurado, premio_mensal, canal_distribuicao, regiao
# MAGIC FROM apolices LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ **Checkpoint.** Você deve ver 7 tabelas + 3 `mv_*` (Metric Views) + `glossario_negocio`. Repare que apólices misturam **Vida** (têm capital segurado) e **Previdência** (têm reserva).

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 2 · Dashboards AI/BI — mão na massa
# MAGIC **11h10–11h40**
# MAGIC
# MAGIC 🧑‍🏫 Um dashboard **AI/BI** é montado sobre datasets do Unity Catalog, com KPIs, gráficos e filtros — **sem código**. Vamos primeiro ver um pronto e depois construir o seu.
# MAGIC
# MAGIC ▶️ **Referência:** abra o **[Dashboard AI/BI de referência](https://fevm-moi-ai.cloud.databricks.com/sql/dashboardsv3/01f1ab91baf51017b6a24adc9a23888e/published?o=7474658545709121)** — KPIs, prêmio por região, arrecadação mensal, sinistros/fraude e top corretores, com botão *Ask Genie*.
# MAGIC
# MAGIC ## 🧪 Lab A — Seu primeiro dashboard
# MAGIC 1. Menu lateral → **Dashboards** → **Create dashboard**.
# MAGIC 2. Aba **Data** → **Add data** → tabela `moi_ai_catalog.metlife_workshop.apolices`.
# MAGIC 3. Aba **Canvas** → **Add visualization**:
# MAGIC    - **Contador (KPI):** apólices ativas → filtro `status_apolice = 'Ativa'`, *Count*.
# MAGIC    - **Barras:** `SUM(premio_mensal)` por `regiao`.
# MAGIC    - **Pizza:** apólices por `linha_negocio`.
# MAGIC 4. Adicione um **filtro** de `linha_negocio` e veja tudo reagir.
# MAGIC 5. **Publish** → explore **Share**.
# MAGIC
# MAGIC ▶️ **Prévia dos números** que vão aparecer nos widgets:

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT regiao, ROUND(SUM(premio_mensal),0) AS premio_mensal_total,
# MAGIC        COUNT(*) AS apolices, SUM(CASE WHEN status_apolice='Ativa' THEN 1 ELSE 0 END) AS ativas
# MAGIC FROM apolices GROUP BY regiao ORDER BY premio_mensal_total DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ **Checkpoint.** Seu dashboard tem ao menos 1 KPI + 1 gráfico e um filtro funcionando. Sudeste deve liderar o prêmio.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 3 · Genie — primeira conversa
# MAGIC **11h40–12h20**
# MAGIC
# MAGIC 🧑‍🏫 O **Genie** traduz perguntas em **linguagem natural** para **SQL governado**. Você lê a resposta, o gráfico e — importante — **o SQL gerado**.
# MAGIC
# MAGIC ▶️ Abra o **[Genie Space · tabelas](https://fevm-moi-ai.cloud.databricks.com/genie/rooms/01f1ab8ced4b1c7d88c2984cedb40565?o=7474658545709121)**.
# MAGIC
# MAGIC ## 🧪 Lab B — Perguntar e ler o SQL
# MAGIC Digite, uma a uma, e depois clique em **"Show generated code / SQL"**:
# MAGIC - *"Quantas apólices ativas temos por linha de negócio?"*
# MAGIC - *"Qual o prêmio mensal total por região?"*
# MAGIC - *"Quais os 10 corretores com maior produção de prêmio?"*
# MAGIC
# MAGIC Depois, uma **pergunta de acompanhamento** (sem repetir o contexto):
# MAGIC - *"E somente na região Sudeste?"* · *"Mostre em um gráfico de barras."*
# MAGIC
# MAGIC 🧑‍🏫 **Leitura crítica:** confira `WHERE` e `GROUP BY` do SQL. Foi isso que você perguntou?
# MAGIC
# MAGIC ▶️ **Confira o "gabarito"** das duas primeiras perguntas:

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT linha_negocio, COUNT(*) AS ativas
# MAGIC FROM apolices WHERE status_apolice='Ativa' GROUP BY linha_negocio ORDER BY ativas DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT c.nome_corretor, ROUND(SUM(a.premio_mensal),2) AS producao
# MAGIC FROM apolices a JOIN corretores c ON a.corretor_id=c.corretor_id
# MAGIC WHERE a.status_apolice='Ativa'
# MAGIC GROUP BY c.nome_corretor ORDER BY producao DESC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ **Checkpoint.** O SQL do Genie bate com estas consultas? Perguntas claras + termos de negócio → o Genie acerta; ambíguas → ele pede esclarecimento (isso é esperado).

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # ☕ Intervalo · 11h30–12h30
# MAGIC Retornamos às 12h30 com **curadoria, camada semântica e Genie Ontology**.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 4 · Genie a fundo — curadoria, camada semântica e Ontology
# MAGIC **12h20–12h45**
# MAGIC
# MAGIC 🧑‍🏫 Por que o Genie responde bem aqui? Por causa da **curadoria** e da **camada semântica governada**. Este é o coração do **Genie Ontology**.
# MAGIC
# MAGIC ## 🧪 Lab C — Curadoria (no Genie Space · tabelas)
# MAGIC 1. Abra **Instructions** e leia as regras de negócio (ex.: *"prêmio" = valor pago pelo segurado*; *capital só existe para Vida*).
# MAGIC 2. Veja **descrições de colunas** e **sinônimos**.
# MAGIC 3. Pergunte com o jargão do negócio e veja o Genie entender:
# MAGIC    - *"Qual a **mensalidade** média das apólices de Vida ativas?"* (mensalidade = prêmio)
# MAGIC    - *"Quantos segurados temos no segmento **Premier**?"*
# MAGIC
# MAGIC ## 🧪 Lab E — Camada semântica (Metric Views) e Ontology
# MAGIC 🧑‍🏫 Em vez de recalcular métricas toda hora, definimos **métricas canônicas** uma vez, em **Metric Views** governados. O Genie passa a **reutilizá-las** via `MEASURE()`.
# MAGIC
# MAGIC ▶️ Abra o **[Genie Space · camada semântica](https://fevm-moi-ai.cloud.databricks.com/genie/rooms/01f1ab9021281c98a4a183c6b5f80067?o=7474658545709121)** (aponta só para os 3 Metric Views) e pergunte:
# MAGIC - *"Qual a taxa de arrecadação (persistência) por região?"*
# MAGIC - *"Qual o tempo médio de liquidação e a taxa de fraude por tipo de sinistro?"*
# MAGIC
# MAGIC Repare no SQL: ele usa `MEASURE(...)` — **não reinventa o cálculo**.
# MAGIC
# MAGIC ▶️ Rode as mesmas métricas aqui e compare com o que o Genie devolve:

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Métricas governadas (mv_carteira) — o Genie usa exatamente estas definições
# MAGIC SELECT `Linha de Negocio`,
# MAGIC        MEASURE(`Apolices Ativas`) AS ativas,
# MAGIC        ROUND(MEASURE(`Premio Mensal Total`),2) AS premio,
# MAGIC        ROUND(MEASURE(`Ticket Medio de Premio`),2) AS ticket_medio
# MAGIC FROM mv_carteira GROUP BY `Linha de Negocio`;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Inadimplência e persistência por região (mv_arrecadacao)
# MAGIC SELECT `Regiao`,
# MAGIC        ROUND(MEASURE(`Taxa de Inadimplencia`)*100,2) AS inadimplencia_pct,
# MAGIC        ROUND(MEASURE(`Taxa de Arrecadacao`)*100,1)   AS persistencia_pct
# MAGIC FROM mv_arrecadacao GROUP BY `Regiao` ORDER BY inadimplencia_pct DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC 🧑‍🏫 **O que é o Genie Ontology.** É a camada de *contexto unificado* (nível de conta, Genie One) que combina:
# MAGIC 1. **Semânticas governadas do UC** que *você define* — **Metric Views**, **Domains** e **Pages/glossário** (a fonte da verdade); e
# MAGIC 2. **Contexto inferido** — *snippets* extraídos automaticamente de dashboards, queries e Genie Agents, com *authority scoring*.
# MAGIC
# MAGIC Já deixamos prontos os blocos governados: os **3 Metric Views**, o **Domain** (tags de UC) e o **glossário**. Veja-os:

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Glossário de negócio certificado (alimenta o Ontology)
# MAGIC SELECT termo, definicao, metrica_ou_coluna_referencia FROM glossario_negocio ORDER BY termo;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Domain aplicado via tags de Unity Catalog
# MAGIC SELECT table_name, tag_name, tag_value
# MAGIC FROM system.information_schema.table_tags
# MAGIC WHERE catalog_name='moi_ai_catalog' AND schema_name='metlife_workshop'
# MAGIC ORDER BY table_name, tag_name;

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ **Checkpoint.** O SQL do Genie no 2º espaço usa `MEASURE(...)`? Você localizou os Metric Views, o glossário e as tags de Domain no Catalog Explorer?
# MAGIC
# MAGIC > **Habilitação do Ontology (preview):** o Genie Ontology (Genie One) está em **Public Preview** — peça ao **time de conta Databricks** para habilitar no workspace. Depois disso ele consome automaticamente Metric Views, Domain e glossário e infere *snippets* das queries/dashboards desta aula.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 5 · Casos de uso MetLife
# MAGIC **12h45–12h55**
# MAGIC
# MAGIC ## 🧪 Lab D — Escolha um trilho e pergunte no Genie
# MAGIC **D1 · Sinistros e fraude** — *"Qual o tempo médio de liquidação por tipo?"* · *"Quantos sinistros com suspeita de fraude e qual o valor reclamado?"*
# MAGIC **D2 · Distribuição** — *"Prêmio total por canal de distribuição?"* · *"Qual canal tem o maior ticket médio?"*
# MAGIC **D3 · Persistência** — *"Taxa de inadimplência por região?"* · *"Evolução mensal dos prêmios pagos em 2025?"*
# MAGIC
# MAGIC ▶️ **Gabarito** dos casos (para conferência):

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT `Tipo de Sinistro`,
# MAGIC        MEASURE(`Sinistros`) AS sinistros,
# MAGIC        ROUND(MEASURE(`Tempo Medio de Liquidacao`),1) AS dias,
# MAGIC        ROUND(MEASURE(`Taxa de Fraude`)*100,1) AS fraude_pct,
# MAGIC        MEASURE(`Sinistros de Alto Risco`) AS alto_risco
# MAGIC FROM mv_sinistralidade GROUP BY `Tipo de Sinistro` ORDER BY fraude_pct DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ **Checkpoint.** ~261 sinistros suspeitos (≈10,4%), ~196 de alto risco, liquidação média ≈ 67 dias.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 6 · Encerramento e jornada de adoção
# MAGIC **12h55–13h00**
# MAGIC
# MAGIC 🧑‍🏫 **Do workshop à produção:**
# MAGIC 1. Conectar os dados reais da MetLife no Unity Catalog.
# MAGIC 2. Criar **Metric Views por domínio** e um **Genie Space por área** (sinistros, distribuição, atuarial...).
# MAGIC 3. **Governança:** instruções, sinônimos, Domain, glossário e certificação — tudo alimentando o **Genie Ontology**.
# MAGIC 4. **Habilitar o preview do Ontology** com o time de conta.
# MAGIC 5. Eleger **1 domínio piloto** e **3–5 perguntas de alto valor** para uma prova de conceito acompanhada.
# MAGIC
# MAGIC ## 📌 Recapitulando
# MAGIC - **[Dashboard AI/BI](https://fevm-moi-ai.cloud.databricks.com/sql/dashboardsv3/01f1ab91baf51017b6a24adc9a23888e/published?o=7474658545709121)**
# MAGIC - **[Genie · tabelas](https://fevm-moi-ai.cloud.databricks.com/genie/rooms/01f1ab8ced4b1c7d88c2984cedb40565?o=7474658545709121)** · **[Genie · camada semântica](https://fevm-moi-ai.cloud.databricks.com/genie/rooms/01f1ab9021281c98a4a183c6b5f80067?o=7474658545709121)**
# MAGIC - Repositório com todo o material: `github.com/mousastech/workshop-genie-metlife`
# MAGIC
# MAGIC **Números de bolso:** Vida ≈ 2.801 / Previdência ≈ 2.753 ativas · inadimplência ≈ 5,1% · persistência ≈ 95% · fraude ≈ 10,4% · liquidação ≈ 67 dias.
# MAGIC
# MAGIC ### 🎉 Obrigado! Dúvidas?
