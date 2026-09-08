CREATE OR REPLACE VIEW moi_ai_catalog.metlife_workshop.mv_sinistralidade
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Metricas governadas de sinistros, tempo de liquidacao e fraude - MetLife"
source: "(SELECT s.sinistro_id, s.tipo_sinistro, s.linha_negocio, s.nome_produto, s.status_sinistro, s.regiao, s.uf, s.data_ocorrencia, s.valor_reclamado, s.valor_pago, s.dias_liquidacao, s.suspeita_fraude, f.nivel_risco, f.score_fraude FROM moi_ai_catalog.metlife_workshop.sinistros s JOIN moi_ai_catalog.metlife_workshop.sinistros_fraude_score f ON s.sinistro_id = f.sinistro_id)"
dimensions: [{name: Tipo de Sinistro, expr: "tipo_sinistro", synonyms: ["causa"]}, {name: Linha de Negocio, expr: "linha_negocio", synonyms: ["ramo"]}, {name: Produto, expr: "nome_produto"}, {name: Status do Sinistro, expr: "status_sinistro", synonyms: ["situacao"]}, {name: Regiao, expr: "regiao"}, {name: UF, expr: "uf", synonyms: ["estado"]}, {name: Mes de Ocorrencia, expr: "DATE_TRUNC('MONTH', data_ocorrencia)"}, {name: Nivel de Risco de Fraude, expr: "nivel_risco", synonyms: ["risco de fraude", "risco"]}]
measures: [{name: Sinistros, expr: "COUNT(1)", synonyms: ["numero de sinistros", "quantidade de sinistros"]}, {name: Valor Reclamado, expr: "SUM(valor_reclamado)"}, {name: Valor Pago em Sinistros, expr: "SUM(valor_pago)", synonyms: ["indenizacao", "valor pago"]}, {name: Tempo Medio de Liquidacao, expr: "AVG(dias_liquidacao)", synonyms: ["prazo de liquidacao", "tempo de regulacao"]}, {name: Sinistros Suspeitos, expr: "COUNT(1) FILTER (WHERE suspeita_fraude = true)", synonyms: ["sinistros com suspeita de fraude"]}, {name: Taxa de Fraude, expr: "COUNT(1) FILTER (WHERE suspeita_fraude = true) * 1.0 / COUNT(1)", synonyms: ["percentual de fraude"]}, {name: Sinistros de Alto Risco, expr: "COUNT(1) FILTER (WHERE nivel_risco = 'Alto')"}]
$$
