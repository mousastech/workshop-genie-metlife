"""
MetLife Odonto — Cotação de Planos Odontológicos (Databricks App).
Coleta os dados do cliente passo a passo (simulador de WhatsApp), grava no Lakebase
e recomenda o melhor plano. /webhook pronto p/ WhatsApp Business API (fase 2).
Perfis: Individual e Família.
"""
import os, json, re, uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from databricks.sdk.core import Config

app = FastAPI(title="MetLife Odonto — Cotação")
cfg = Config()
INSTANCE = os.environ.get("LAKEBASE_INSTANCE", "metlife-omnipulse-db")
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "metlife-odonto-verify")

def pg():
    import psycopg, requests
    tok = requests.post(f"{cfg.host}/api/2.0/database/credentials", headers=cfg.authenticate(),
                        json={"request_id": str(uuid.uuid4()), "instance_names":[INSTANCE]}, timeout=30).json()["token"]
    return psycopg.connect(host=os.environ["PGHOST"], port=int(os.environ.get("PGPORT","5432")),
        dbname=os.environ.get("PGDATABASE","omnipulse"), user=os.environ["PGUSER"], password=tok, sslmode="require")

# ---------------- Motor de conversa (state machine) ----------------
def _num(t):
    m = re.findall(r"\d+", (t or "").replace(",", "."));  return int(m[0]) if m else None
def _dec(t):
    m = re.findall(r"\d+[.,]?\d*", (t or "").replace(",", "."));  return float(m[0]) if m else None

def recomendar(cur, cobertura, vidas, orc_vida):
    cur.execute("SELECT nome,cobertura,preco_por_vida,rede,carencia_meses,destaque FROM planos_odonto WHERE cobertura=%s", (cobertura,))
    r = cur.fetchone()
    nota = ""
    if r and orc_vida and float(r[2]) > orc_vida:
        cur.execute("SELECT nome,cobertura,preco_por_vida,rede,carencia_meses,destaque FROM planos_odonto WHERE preco_por_vida<=%s ORDER BY preco_por_vida DESC LIMIT 1",(orc_vida,))
        alt = cur.fetchone()
        if alt: nota = f"(Ajustamos ao seu orçamento: o {cobertura} custa R$ {float(r[2]):.2f}/vida.) "; r = alt
    if not r:
        cur.execute("SELECT nome,cobertura,preco_por_vida,rede,carencia_meses,destaque FROM planos_odonto ORDER BY preco_por_vida LIMIT 1"); r=cur.fetchone()
    total = float(r[2]) * max(vidas or 1, 1)
    return {"nome":r[0],"cobertura":r[1],"preco_por_vida":float(r[2]),"rede":r[3],"carencia":r[4],"destaque":r[5],
            "total":round(total,2),"vidas":vidas or 1,"nota":nota}

COBERTURAS = {"1":"Basico","2":"Ortodontia","3":"Completo","basico":"Basico","ortodontia":"Ortodontia","completo":"Completo"}

def avancar(row, msg):
    """row: dict do estado atual. Retorna (updates, reply, done, plano)."""
    st = row.get("estado","inicio"); u={}; plano=None; done=False; m=(msg or "").strip()
    if st=="inicio":
        u["estado"]="consent"
        reply=("🦷 *Olá! Sou a assistente de cotação MetLife Odonto.*\nPosso coletar alguns dados para te oferecer o melhor plano odontológico?\n\nResponda *sim* para começar. (Ao continuar, você concorda com o uso dos dados para a cotação — LGPD.)")
    elif st=="consent":
        if m.lower().startswith(("s","sim")):
            u["consentimento"]=True; u["estado"]="perfil"
            reply="Ótimo! A cotação é para *Individual* ou *Família*?"
        else:
            u["consentimento"]=False; u["estado"]="fim"; done=True
            reply="Sem problemas! Quando quiser cotar, é só chamar. 🦷"
    elif st=="perfil":
        if "fam" in m.lower():
            u["perfil"]="Família"; u["estado"]="vidas"; reply="Quantas *vidas* no plano (titular + dependentes)?"
        else:
            u["perfil"]="Individual"; u["vidas"]=1; u["estado"]="uf"; reply="Qual o seu *estado* (UF)? Ex.: SP, RJ, MG…"
    elif st=="vidas":
        n=_num(m) or 2; u["vidas"]=n; u["estado"]="uf"; reply=f"{n} vidas, anotado. Qual o *estado* (UF)?"
    elif st=="uf":
        u["uf"]=m.upper()[:2]; u["estado"]="idade"; reply="Qual a *idade do beneficiário mais velho*?"
    elif st=="idade":
        u["idade_max"]=_num(m) or 30; u["estado"]="cobertura"
        reply="Que *cobertura* você deseja?\n*1)* Básico  *2)* Ortodontia (aparelho)  *3)* Completo (ortodontia + prótese)"
    elif st=="cobertura":
        u["cobertura_desejada"]=COBERTURAS.get(m.lower().strip(),"Basico"); u["estado"]="orcamento"
        reply="Qual o *orçamento mensal por vida* (aprox., em R$)? Ex.: 50, 90, 130"
    elif st=="orcamento":
        u["orcamento"]=_dec(m); u["estado"]="nome"; reply="Por fim, qual o seu *nome*?"
    elif st=="nome":
        u["nome"]=m[:80]; u["estado"]="concluido"; done=True; plano="__RECO__"  # recomenda no handler (precisa do cursor)
        reply=None
    else:  # concluido/fim
        if m.lower().startswith("reinic"):
            u={"estado":"inicio","consentimento":None,"perfil":None,"vidas":None,"uf":None,"idade_max":None,"cobertura_desejada":None,"orcamento":None,"nome":None,"plano_recomendado":None,"preco_estimado":None}
            reply="Vamos recomeçar! Responda *sim* para iniciar uma nova cotação."
        else:
            reply="Sua cotação já foi concluída ✅. Digite *reiniciar* para uma nova."
    return u, reply, done, plano

def processar(session_id, msg, canal="simulador"):
    with pg() as conn, conn.cursor() as cur:
        cur.execute("SELECT session_id,estado,consentimento,perfil,vidas,uf,idade_max,cobertura_desejada,orcamento,nome FROM cotacoes_odonto WHERE session_id=%s",(session_id,))
        cols=["session_id","estado","consentimento","perfil","vidas","uf","idade_max","cobertura_desejada","orcamento","nome"]
        rowdb=cur.fetchone()
        if not rowdb:
            cur.execute("INSERT INTO cotacoes_odonto(session_id,canal,estado) VALUES(%s,%s,'inicio')",(session_id,canal))
            row={"session_id":session_id,"estado":"inicio"}
        else:
            row=dict(zip(cols,rowdb))
        cur.execute("INSERT INTO cotacao_mensagens(session_id,origem,texto) VALUES(%s,'cliente',%s)",(session_id,msg or ""))
        u,reply,done,plano = avancar(row, msg)
        planojson=None
        if plano=="__RECO__":
            merged={**row,**u}
            reco=recomendar(cur, merged.get("cobertura_desejada","Basico"), merged.get("vidas",1), merged.get("orcamento"))
            planojson=reco
            u["plano_recomendado"]=reco["nome"]; u["preco_estimado"]=reco["total"]
            reply=(f"✅ *Cotação pronta, {merged.get('nome','')}!*\nRecomendamos o *{reco['nome']}* ({reco['cobertura']}).\n"
                   f"💰 *R$ {reco['preco_por_vida']:.2f}/vida* × {reco['vidas']} = *R$ {reco['total']:.2f}/mês*\n"
                   f"🦷 {reco['rede']}\n⏳ Carência: {reco['carencia']} meses\n{reco['nota']}\nDigite *reiniciar* para uma nova cotação.")
        # persiste updates
        if u:
            sets=", ".join([f"{k}=%s" for k in u]); vals=list(u.values())+[session_id]
            cur.execute(f"UPDATE cotacoes_odonto SET {sets}, atualizado_em=now() WHERE session_id=%s", vals)
        cur.execute("INSERT INTO cotacao_mensagens(session_id,origem,texto) VALUES(%s,'bot',%s)",(session_id,reply or ""))
    return {"reply":reply,"done":done,"plano":planojson}

# ---------------- API do simulador ----------------
@app.post("/api/chat")
async def chat(req: Request):
    b=await req.json()
    sid=b.get("session_id") or str(uuid.uuid4())
    try:
        out=processar(sid, b.get("mensagem",""))
        out["session_id"]=sid; return out
    except Exception as e:
        return JSONResponse({"error":str(e)[:200],"session_id":sid}, status_code=500)

# ---------------- WhatsApp webhook (fase 2 — Meta Cloud API) ----------------
@app.get("/webhook")
async def verify(req: Request):
    p=req.query_params
    if p.get("hub.mode")=="subscribe" and p.get("hub.verify_token")==VERIFY_TOKEN:
        return PlainTextResponse(p.get("hub.challenge",""))
    return PlainTextResponse("forbidden", status_code=403)

@app.post("/webhook")
async def inbound(req: Request):
    """Recebe mensagem do WhatsApp (Meta), roda o motor e (fase 2) responde via API de envio."""
    body=await req.json()
    try:
        val=body["entry"][0]["changes"][0]["value"]
        msg=val["messages"][0]; frm=msg["from"]; texto=msg.get("text",{}).get("body","")
        out=processar(frm, texto, canal="whatsapp")
        # FASE 2: enviar out["reply"] via WhatsApp Cloud API (POST /{phone_number_id}/messages)
        return {"status":"ok","to":frm,"reply":out["reply"]}
    except Exception as e:
        return JSONResponse({"status":"ignored","erro":str(e)[:160]}, status_code=200)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
