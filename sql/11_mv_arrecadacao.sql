CREATE OR REPLACE VIEW moi_ai_catalog.metlife_workshop.mv_arrecadacao
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Metricas governadas de arrecadacao, inadimplencia e persistencia de premios - MetLife"
source: moi_ai_catalog.metlife_workshop.premios
dimensions: [{name: Competencia, expr: "competencia", synonyms: ["mes", "periodo"]}, {name: Linha de Negocio, expr: "linha_negocio", synonyms: ["ramo"]}, {name: Canal de Distribuicao, expr: "canal_distribuicao", synonyms: ["canal"]}, {name: Regiao, expr: "regiao"}, {name: Status do Pagamento, expr: "status_pagamento", synonyms: ["situacao do pagamento"]}]
measures: [{name: Premios Emitidos, expr: "COUNT(1)", synonyms: ["quantidade de premios", "cobrancas"]}, {name: Valor Devido, expr: "SUM(valor_devido)"}, {name: Valor Arrecadado, expr: "SUM(valor_pago)", synonyms: ["arrecadacao", "premio pago"]}, {name: Pagamentos Inadimplentes, expr: "COUNT(1) FILTER (WHERE status_pagamento = 'Inadimplente')", synonyms: ["inadimplentes"]}, {name: Taxa de Inadimplencia, expr: "COUNT(1) FILTER (WHERE status_pagamento = 'Inadimplente') * 1.0 / COUNT(1)", synonyms: ["inadimplencia"]}, {name: Taxa de Arrecadacao, expr: "SUM(valor_pago) / SUM(valor_devido)", synonyms: ["persistencia", "taxa de pagamento"]}]
$$
