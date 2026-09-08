CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.corretores AS
WITH base AS (
  SELECT explode(sequence(1, 150)) AS corretor_id
),
nomes AS (
  SELECT array('Ana','Bruno','Carla','Diego','Eduarda','Felipe','Gabriela','Henrique','Isabela','Joao',
               'Karina','Lucas','Mariana','Nelson','Olivia','Paulo','Renata','Sergio','Tatiana','Vinicius') AS fn,
         array('Silva','Souza','Oliveira','Santos','Pereira','Costa','Rodrigues','Almeida','Nascimento','Lima',
               'Araujo','Ferreira','Carvalho','Gomes','Martins','Ribeiro','Barbosa','Rocha','Dias','Moraes') AS ln,
         array('SP','RJ','MG','RS','PR','SC','BA','PE','CE','DF','GO','ES','PA','AM') AS ufs
)
SELECT
  b.corretor_id,
  concat('COR', lpad(cast(b.corretor_id AS string), 5, '0')) AS codigo_corretor,
  concat(element_at(n.fn, pmod(hash(b.corretor_id * 7), 20) + 1), ' ',
         element_at(n.ln, pmod(hash(b.corretor_id * 13), 20) + 1)) AS nome_corretor,
  element_at(array('Corretor Independente','Bancassurance','Canal Digital','Corporate Beneficios'),
             pmod(hash(b.corretor_id * 3), 4) + 1) AS canal_distribuicao,
  element_at(n.ufs, pmod(hash(b.corretor_id * 5), 14) + 1) AS uf,
  CASE element_at(n.ufs, pmod(hash(b.corretor_id * 5), 14) + 1)
    WHEN 'SP' THEN 'Sudeste' WHEN 'RJ' THEN 'Sudeste' WHEN 'MG' THEN 'Sudeste' WHEN 'ES' THEN 'Sudeste'
    WHEN 'RS' THEN 'Sul' WHEN 'PR' THEN 'Sul' WHEN 'SC' THEN 'Sul'
    WHEN 'BA' THEN 'Nordeste' WHEN 'PE' THEN 'Nordeste' WHEN 'CE' THEN 'Nordeste'
    WHEN 'DF' THEN 'Centro-Oeste' WHEN 'GO' THEN 'Centro-Oeste'
    WHEN 'PA' THEN 'Norte' WHEN 'AM' THEN 'Norte' ELSE 'Outros' END AS regiao,
  date_add(DATE'2015-01-01', pmod(hash(b.corretor_id * 17), 3650)) AS data_admissao,
  (500000 + pmod(hash(b.corretor_id * 11), 20) * 150000) AS meta_anual_producao
FROM base b CROSS JOIN nomes n;
