CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.clientes AS
WITH base AS (
  SELECT explode(sequence(1, 5000)) AS cliente_id
),
dim AS (
  SELECT array('Alexandre','Beatriz','Camila','Daniel','Elaine','Fabio','Giovana','Hugo','Ingrid','Jorge',
               'Kelly','Leandro','Marcia','Natalia','Otavio','Patricia','Rafael','Sabrina','Thiago','Vanessa',
               'William','Yara','Bruno','Carolina','Rodrigo') AS fn,
         array('Almeida','Barros','Cardoso','Duarte','Esteves','Freitas','Guimaraes','Henriques','Imperio','Junqueira',
               'Klein','Lopes','Machado','Nogueira','Pinto','Queiroz','Ramos','Teixeira','Vasconcelos','Xavier') AS ln,
         array('Sao Paulo','Rio de Janeiro','Belo Horizonte','Porto Alegre','Curitiba','Florianopolis','Salvador',
               'Recife','Fortaleza','Brasilia','Goiania','Vitoria','Belem','Manaus') AS cidades,
         array('SP','RJ','MG','RS','PR','SC','BA','PE','CE','DF','GO','ES','PA','AM') AS ufs
)
SELECT
  b.cliente_id,
  concat('CLI', lpad(cast(b.cliente_id AS string), 7, '0')) AS codigo_cliente,
  concat(element_at(d.fn, pmod(hash(b.cliente_id * 7), 25) + 1), ' ',
         element_at(d.ln, pmod(hash(b.cliente_id * 19), 20) + 1)) AS nome_cliente,
  CASE WHEN pmod(hash(b.cliente_id * 2), 2) = 0 THEN 'F' ELSE 'M' END AS sexo,
  (22 + pmod(hash(b.cliente_id * 23), 55)) AS idade,
  date_sub(DATE'2026-09-01', (22 + pmod(hash(b.cliente_id * 23), 55)) * 365) AS data_nascimento,
  element_at(d.cidades, pmod(hash(b.cliente_id * 5), 14) + 1) AS cidade,
  element_at(d.ufs, pmod(hash(b.cliente_id * 5), 14) + 1) AS uf,
  CASE element_at(d.ufs, pmod(hash(b.cliente_id * 5), 14) + 1)
    WHEN 'SP' THEN 'Sudeste' WHEN 'RJ' THEN 'Sudeste' WHEN 'MG' THEN 'Sudeste' WHEN 'ES' THEN 'Sudeste'
    WHEN 'RS' THEN 'Sul' WHEN 'PR' THEN 'Sul' WHEN 'SC' THEN 'Sul'
    WHEN 'BA' THEN 'Nordeste' WHEN 'PE' THEN 'Nordeste' WHEN 'CE' THEN 'Nordeste'
    WHEN 'DF' THEN 'Centro-Oeste' WHEN 'GO' THEN 'Centro-Oeste'
    WHEN 'PA' THEN 'Norte' WHEN 'AM' THEN 'Norte' ELSE 'Outros' END AS regiao,
  round(2500 + pmod(hash(b.cliente_id * 29), 100) * 480 + pmod(hash(b.cliente_id * 41), 1500), 2) AS renda_mensal,
  element_at(array('Massificado','Classico','Premier','Private'),
             CASE WHEN pmod(hash(b.cliente_id * 31), 100) < 60 THEN 1
                  WHEN pmod(hash(b.cliente_id * 31), 100) < 85 THEN 2
                  WHEN pmod(hash(b.cliente_id * 31), 100) < 97 THEN 3 ELSE 4 END) AS segmento_cliente,
  date_add(DATE'2016-01-01', pmod(hash(b.cliente_id * 37), 3400)) AS data_cadastro
FROM base b CROSS JOIN dim d;
