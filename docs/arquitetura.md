# Arquitetura do Workshop

Dois diagramas: (1) o **fluxo de arquitetura** — das tabelas à camada semântica, ao consumo (Genie/Dashboard) e ao Genie Ontology; (2) o **modelo de dados** (relacionamentos entre as 7 tabelas).

## 1. Fluxo de arquitetura

```mermaid
flowchart TB
  subgraph Fonte["Dados sinteticos · UC moi_ai_catalog.metlife_workshop"]
    direction LR
    T1[apolices]
    T2[clientes]
    T3[corretores]
    T4[produtos]
    T5[premios]
    T6[sinistros]
    T7[sinistros_fraude_score]
  end

  subgraph Sem["Camada semantica governada (gold)"]
    direction LR
    MV1[mv_carteira]
    MV2[mv_arrecadacao]
    MV3[mv_sinistralidade]
  end

  subgraph Gov["Governanca Unity Catalog"]
    direction LR
    DOM[Domain · tags]
    GLO[glossario_negocio]
  end

  subgraph Consumo["Consumo"]
    direction LR
    G1[Genie Space · tabelas]
    G2[Genie Space · camada semantica]
    DASH[Dashboard AI/BI]
  end

  ONT[["Genie Ontology<br/>Genie One · preview"]]
  USERS([Negocio e Dados])

  Fonte --> Sem
  Fonte --> G1
  Sem --> G2
  Sem --> DASH
  Gov -. governa .-> Fonte
  Gov -. governa .-> Sem
  Sem --> ONT
  Gov --> ONT
  G2 -. snippets inferidos .-> ONT
  DASH -. snippets inferidos .-> ONT
  ONT -. contexto .-> G1
  ONT -. contexto .-> G2
  G1 --> USERS
  G2 --> USERS
  DASH --> USERS
```

**Leitura.** As 7 tabelas alimentam tanto a exploração direta (Genie sobre tabelas) quanto a **camada semântica** (Metric Views), que por sua vez serve o Genie de métricas governadas e o dashboard. A **governança do Unity Catalog** (Domain via tags + glossário) e os Metric Views são a *fonte da verdade* do **Genie Ontology**; dashboards e queries geram *snippets inferidos* de alta autoridade; e o Ontology devolve contexto de negócio para os Genie Spaces.

## 2. Modelo de dados

```mermaid
erDiagram
  CLIENTES   ||--o{ APOLICES : cliente_id
  CORRETORES ||--o{ APOLICES : corretor_id
  PRODUTOS   ||--o{ APOLICES : produto_id
  APOLICES   ||--o{ PREMIOS : apolice_id
  APOLICES   ||--o{ SINISTROS : apolice_id
  SINISTROS  ||--|| SINISTROS_FRAUDE_SCORE : sinistro_id

  CLIENTES {
    int cliente_id PK
    string nome_cliente
    string segmento_cliente
    string uf
    double renda_mensal
  }
  CORRETORES {
    int corretor_id PK
    string nome_corretor
    string canal_distribuicao
    string regiao
    double meta_anual_producao
  }
  PRODUTOS {
    int produto_id PK
    string nome_produto
    string linha_negocio
    string tipo_produto
  }
  APOLICES {
    int apolice_id PK
    string numero_apolice
    string linha_negocio
    string status_apolice
    double capital_segurado
    double premio_mensal
    double reserva_acumulada
  }
  PREMIOS {
    string id_pagamento PK
    int apolice_id FK
    date competencia
    double valor_devido
    double valor_pago
    string status_pagamento
  }
  SINISTROS {
    int sinistro_id PK
    int apolice_id FK
    string tipo_sinistro
    string status_sinistro
    double valor_reclamado
    double valor_pago
    int dias_liquidacao
    boolean suspeita_fraude
  }
  SINISTROS_FRAUDE_SCORE {
    int sinistro_id PK
    int score_fraude
    string nivel_risco
    string motivo_alerta_principal
  }
```

**Metric Views** (camada gold, uma por fato): `mv_carteira` (apólices), `mv_arrecadacao` (prêmios), `mv_sinistralidade` (sinistros + score de fraude).
