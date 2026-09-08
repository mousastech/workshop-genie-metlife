CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.glossario_negocio
COMMENT 'Glossario de negocio certificado do dominio Seguros MetLife - termos canonicos, definicoes, sinonimos e metrica/tabela de referencia. Alimenta o Genie Ontology.'
AS SELECT * FROM VALUES
  ('Premio', 'Valor pago periodicamente pelo segurado para manter a cobertura vigente.', 'premio mensal, mensalidade', 'mv_carteira.Premio Mensal Total'),
  ('Capital Segurado', 'Importancia segurada: valor de cobertura pago em caso de sinistro (apenas Vida).', 'importancia segurada, cobertura', 'mv_carteira.Capital Segurado Total'),
  ('Reserva Acumulada', 'Saldo acumulado do participante em produtos de Previdencia (PGBL/VGBL).', 'saldo, provisao', 'mv_carteira.Reserva Acumulada Total'),
  ('Ticket Medio', 'Premio mensal medio por apolice.', 'premio medio', 'mv_carteira.Ticket Medio de Premio'),
  ('Taxa de Cancelamento', 'Percentual de apolices canceladas sobre o total (churn de carteira).', 'churn, cancelamento', 'mv_carteira.Taxa de Cancelamento'),
  ('Inadimplencia', 'Percentual de premios com status Inadimplente sobre o total de cobrancas.', 'default, atraso', 'mv_arrecadacao.Taxa de Inadimplencia'),
  ('Persistencia', 'Taxa de arrecadacao: valor efetivamente pago dividido pelo valor devido.', 'taxa de arrecadacao, retencao de premio', 'mv_arrecadacao.Taxa de Arrecadacao'),
  ('Sinistralidade', 'Relacao entre valor pago em sinistros e premios ganhos no periodo (loss ratio). Cruza mv_sinistralidade x mv_arrecadacao.', 'loss ratio, indice de sinistralidade', 'mv_sinistralidade.Valor Pago em Sinistros / mv_arrecadacao.Valor Arrecadado'),
  ('Tempo de Liquidacao', 'Numero de dias entre o aviso e a liquidacao (regulacao) de um sinistro.', 'prazo de regulacao, tempo de regulacao', 'mv_sinistralidade.Tempo Medio de Liquidacao'),
  ('Suspeita de Fraude', 'Sinistro sinalizado como potencial fraude por regras/score (ex.: ocorrencia < 180 dias da emissao).', 'fraude, alerta', 'mv_sinistralidade.Taxa de Fraude'),
  ('Nivel de Risco de Fraude', 'Classificacao do score de fraude do sinistro em Baixo, Medio ou Alto.', 'risco de fraude', 'sinistros_fraude_score.nivel_risco'),
  ('Canal de Distribuicao', 'Meio pelo qual a apolice foi comercializada: Corretor Independente, Bancassurance, Canal Digital ou Corporate Beneficios.', 'canal', 'mv_carteira.Canal de Distribuicao'),
  ('Segmento do Cliente', 'Segmentacao do segurado: Massificado, Classico, Premier ou Private.', 'segmento', 'mv_carteira.Segmento do Cliente')
AS t(termo, definicao, sinonimos, metrica_ou_coluna_referencia);
