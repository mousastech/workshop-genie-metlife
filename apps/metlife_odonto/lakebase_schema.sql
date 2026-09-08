-- Lakebase (db omnipulse) — esquema da cotação odontológica
CREATE TABLE IF NOT EXISTS planos_odonto(
  id serial PRIMARY KEY, nome text, cobertura text, preco_por_vida numeric,
  vidas_min int DEFAULT 1, rede text, carencia_meses int, destaque text);
CREATE TABLE IF NOT EXISTS cotacoes_odonto(
  session_id text PRIMARY KEY, canal text DEFAULT 'simulador', consentimento boolean,
  perfil text, vidas int, uf text, idade_max int, cobertura_desejada text, orcamento numeric,
  nome text, estado text DEFAULT 'inicio', plano_recomendado text, preco_estimado numeric,
  criado_em timestamptz DEFAULT now(), atualizado_em timestamptz DEFAULT now());
CREATE TABLE IF NOT EXISTS cotacao_mensagens(
  id serial PRIMARY KEY, session_id text, origem text, texto text, criado_em timestamptz DEFAULT now());

INSERT INTO planos_odonto(nome,cobertura,preco_por_vida,vidas_min,rede,carencia_meses,destaque) VALUES
 ('Odonto Essencial','Basico',39.90,1,'Rede nacional (consultas, limpeza, urgência 24h)',0,'Melhor preço'),
 ('Odonto Família','Intermediario',59.90,2,'Rede ampliada (+ canal, extração, restauração)',3,'Ideal p/ famílias'),
 ('Odonto Ortho','Ortodontia',89.90,1,'Rede + ortodontia (aparelho e manutenção)',6,'Inclui aparelho'),
 ('Odonto Completo','Completo',129.90,1,'Rede premium (ortodontia + prótese + estética)',6,'Cobertura total');
