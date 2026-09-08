CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.produtos AS
SELECT * FROM VALUES
  (1,  'Vida Individual Premiado',      'Vida',        'Vida Individual',      0.030, 50000,  2000000),
  (2,  'Vida em Grupo Empresarial',     'Vida',        'Vida em Grupo',        0.025, 30000,  1000000),
  (3,  'Vida Mulher',                   'Vida',        'Vida Individual',      0.028, 40000,  1500000),
  (4,  'Seguro Prestamista',            'Vida',        'Prestamista',          0.020, 10000,  500000),
  (5,  'Vida Senior 60+',               'Vida',        'Vida Individual',      0.045, 20000,  800000),
  (6,  'Acidentes Pessoais',            'Vida',        'Acidentes Pessoais',   0.018, 15000,  600000),
  (7,  'PGBL Tradicional',              'Previdencia', 'PGBL',                 0.015, 0,       0),
  (8,  'PGBL Multimercado',             'Previdencia', 'PGBL',                 0.020, 0,       0),
  (9,  'VGBL Renda Fixa',               'Previdencia', 'VGBL',                 0.012, 0,       0),
  (10, 'VGBL Multimercado',             'Previdencia', 'VGBL',                 0.018, 0,       0),
  (11, 'VGBL Junior',                   'Previdencia', 'VGBL',                 0.015, 0,       0),
  (12, 'Previdencia Corporativa PJ',    'Previdencia', 'PGBL',                 0.010, 0,       0)
AS t(produto_id, nome_produto, linha_negocio, tipo_produto, taxa_carregamento, capital_min, capital_max);
