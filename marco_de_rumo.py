import base64
import os

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="MARCO DE RUMO", page_icon="🏍️", layout="wide")

LOGO = "LOGOMARCA MARCO DE RUMO MODELADA.png"
SUBTITULO = "Estação de Planejamento de Expedições"
DESCRICAO = "Simulador didático de física aplicada ao mototurismo"  # ajuste o texto aqui

# ---------- ESTILO ----------
st.markdown("""
<style>
.stApp {background:#EEF2F5; color:#1B2A38;}
.block-container {padding-top:1rem; padding-left:1rem; padding-right:1rem;}
.logo {text-align:center; margin-bottom:.4rem;}
.logo img {max-width:min(70%,300px); height:auto; display:inline-block;}
.topo {background:#23364A; border-radius:10px; padding:.9rem .5rem; text-align:center; margin-bottom:.8rem;}
.topo .nome {color:#F5F1E8; font-weight:800; letter-spacing:.08em; font-size:clamp(1.5rem,7.5vw,2.4rem); white-space:nowrap;}
.topo .sub {color:#D6E2EC; font-size:clamp(.72rem,3.3vw,1.05rem); white-space:nowrap;}
.topo .desc {color:#9FB6C8; font-size:clamp(.66rem,3vw,.95rem); white-space:nowrap; margin-top:.15rem;}
.sec {color:#23364A; font-weight:700; font-size:clamp(.9rem,4vw,1.35rem); white-space:nowrap;
      border-bottom:2px solid #23364A33; padding:.2rem 0; margin:1rem 0 .5rem;}
.sub2 {color:#23364A; font-weight:600; font-size:clamp(.9rem,3.8vw,1.1rem); white-space:nowrap; margin:.8rem 0 .2rem;}
.cartao {background:#FFFFFF; border:1px solid #C9D4DE; border-radius:10px; padding:.6rem .7rem; margin-bottom:.5rem;}
.cartao .r {color:#4A5D6E; font-size:.8rem;}
.cartao .v {color:#14202C; font-weight:700; font-size:clamp(1.05rem,4.8vw,1.45rem); white-space:nowrap;}
.cartao .s {color:#4A5D6E; font-size:.75rem;}
.caixa {border-left:6px solid; border-radius:8px; padding:.65rem .8rem; margin:.5rem 0; font-size:.95rem;}
</style>
""", unsafe_allow_html=True)

CORES = {  # fundo, borda, texto
    "ok": ("#DDF0E2", "#2F7D4F", "#14391F"),
    "atencao": ("#FBEBC8", "#C98A0B", "#4A3300"),
    "perigo": ("#F8D9D5", "#B3261E", "#4A0F0B"),
    "info": ("#E3EBF3", "#23364A", "#14202C"),
}


def secao(icone, texto):
    st.markdown(f'<div class="sec">{icone} {texto}</div>', unsafe_allow_html=True)


def sub(icone, texto):
    st.markdown(f'<div class="sub2">{icone} {texto}</div>', unsafe_allow_html=True)


def cartao(rotulo, valor, detalhe=""):
    st.markdown(f'<div class="cartao"><div class="r">{rotulo}</div><div class="v">{valor}</div>'
                f'<div class="s">{detalhe}</div></div>', unsafe_allow_html=True)


def caixa(texto, nivel):
    bg, borda, fg = CORES[nivel]
    st.markdown(f'<div class="caixa" style="background:{bg};border-color:{borda};color:{fg}">{texto}</div>',
                unsafe_allow_html=True)


# ---------- CABEÇALHO ----------
if os.path.exists(LOGO):
    with open(LOGO, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="logo"><img src="data:image/png;base64,{b64}"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="topo"><div class="nome">MARCO DE RUMO</div><div class="sub">{SUBTITULO}</div>'
            f'<div class="desc">{DESCRICAO}</div></div>', unsafe_allow_html=True)
caixa("Estimativa DIDÁTICA: números ilustrativos para treinar raciocínio. "
      "Não use para planejar uma viagem real.", "info")

# ---------- TABELAS DE REFERÊNCIA (valores ilustrativos) ----------
FAIXAS = {
    "baixa": dict(tanque=12.0, kml=28.0, folego=1.45, f_peso=1.5),
    "media": dict(tanque=18.0, kml=22.0, folego=1.90, f_peso=1.0),
    "alta": dict(tanque=22.0, kml=17.0, folego=2.60, f_peso=0.5),
}
PERFIS = {
    "Naked ou trail pequena (frente baixa)": 0.8,
    "Trail com para-brisa": 1.0,
    "Touring ou custom com carenagem grande (ex.: Harley)": 1.3,
}
TERRENOS = {  # (custo fixo no consumo, multiplicador do peso)
    "Plano": (0.00, 1),
    "Descida suave": (-0.05, 1),
    "Subida leve (reduzo uma marcha)": (0.10, 2),
    "Subida moderada (reduzo duas marchas)": (0.20, 3),
    "Subida extrema (cordilheira, motor em regime alto)": (0.35, 4),
}
GALAO = "Galão de combustível (5 L cheio)"
ITENS = {
    "Ferramentas pesadas": 4, "Barraca de emergência": 5, "Kit médico": 3, "Drone": 4,
    "Compressor e kit de remendo": 2, GALAO: 6, "Água de reserva": 6,
    "Comida de reserva": 3, "Saco térmico de emergência": 3,
}
PAISES = {"Brasil (gasolina com ~32% de etanol)": 1.00,
          "Argentina (gasolina com ~12 a 15% de etanol)": 1.05}
PESO_GARUPA = 65  # peso-padrão do roteiro; ninguém informa o próprio peso

esq, dir_ = st.columns(2, gap="large")

# ---------- 1. PARÂMETROS ----------
with esq:
    secao("⚙️", "1. Parâmetros da expedição")
    sub("🏍️", "Moto")
    cc = st.number_input("Cilindrada (cc)", 50, 2500, 650, step=50)
    chave = "baixa" if cc <= 400 else "media" if cc <= 800 else "alta"
    faixa = FAIXAS[chave]
    perfil = st.selectbox("Perfil aerodinâmico (tamanho da frente que pega o vento)", list(PERFIS))
    tanque = st.number_input("Capacidade do tanque, incluindo reserva (litros)", 3.0, 40.0,
                             faixa["tanque"], step=0.5, key=f"tanque_{chave}")

    sub("🧳", "Carga")
    garupa = st.checkbox(f"Vou com garupa ({PESO_GARUPA} kg, peso-padrão)")
    baus = st.checkbox("Baús laterais")
    baus_kg = st.number_input("Peso dos baús vazios (kg)", 0, 30, 8, step=1) if baus else 0
    bagagem = st.number_input("Bagagem pessoal (kg)", 0, 80, 25, step=5)
    itens = st.multiselect("Itens coletivos que eu levo", list(ITENS))
    peso = (PESO_GARUPA if garupa else 0) + baus_kg + bagagem + sum(ITENS[i] for i in itens)
    galao = GALAO in itens
    st.caption(f"Peso adicional total: {peso} kg" + (" · galão: +5 L de combustível" if galao else ""))

    sub("🛣️", "Trecho")
    pneus = st.checkbox("Pneus de uso misto ou off-road")
    frio = st.checkbox("❄️ Frio extremo (abaixo de 10 °C)")
    pais = st.selectbox("Combustível do país", list(PAISES))
    vel = st.slider("Velocidade de cruzeiro (km/h)", 60, 130, 100, step=5)
    vento = st.slider("Vento frontal (km/h)", 0, 80, 0, step=5)
    terreno = st.selectbox("Terreno predominante", list(TERRENOS))
    dist = st.number_input("Distância até o próximo posto (km)", 10, 1000, 200, step=10)
    pct = st.slider("Tanque ao sair (%)", 10, 100, 100, step=10)
    palpite = st.number_input("Seu palpite de autonomia (km). Anote ANTES de ver o resultado",
                              0, 1500, 0, step=10)

# ---------- MOTOR DE CÁLCULO ----------
# m = quanto o consumo por km sobe em relação à moto "ideal" (m = 1,0).
V_REF = 90
a = 0.30 * PERFIS[perfil] + (0.05 if baus else 0)              # parte do consumo que é arrasto
pen_arrasto = a * (((vel + vento) / V_REF) ** 2 - 1)             # arrasto cresce com o quadrado da velocidade
custo_terreno, mult_terreno = TERRENOS[terreno]
pen_peso = (peso / 10) * 0.005 * faixa["f_peso"] * mult_terreno  # peso pesa sempre; mais na subida
pen_pneus = 0.05 if pneus else 0.0
pen_frio = 0.04 if frio else 0.0
m = 1 + pen_arrasto + pen_peso + custo_terreno + pen_pneus + pen_frio

limitado = m > faixa["folego"]                                   # motor sem fôlego para a velocidade
pen_motor = 0.10 * m if limitado else 0.0
vel_real = max(40, vel * faixa["folego"] / m) if limitado else vel
m += pen_motor

kml_ideal = faixa["kml"] * PAISES[pais]
kml = kml_ideal / m
litros = tanque * pct / 100 + (5 if galao else 0)
ref_util = litros * kml_ideal * 0.90                              # moto ideal, com 10% de margem
util = ref_util / m
baixo, alto = util * 0.90, util * 1.10                            # incerteza do modelo
horas = dist / vel_real
fadiga = min(100, int((m - 1) * 45 + horas * 7 + (8 if frio else 0)))

# ---------- 2. DIAGNÓSTICO ----------
with dir_:
    secao("📊", "2. Diagnóstico Didático do Trecho")
    c1, c2, c3 = st.columns(3)
    with c1:
        cartao("Autonomia possível", f"{baixo:.0f} a {alto:.0f} km", "com 10% de margem")
    with c2:
        cartao("Consumo estimado", f"{kml:.1f} km/l", f"moto ideal: {kml_ideal:.1f} km/l")
    with c3:
        cartao("Moto ideal", f"{ref_util:.0f} km", "sem carga, vento nem relevo")

    if baixo >= dist:
        caixa(f"✅ <b>Rota segura:</b> chega ao posto a {dist} km, mesmo no cenário pessimista.", "ok")
    elif alto >= dist:
        caixa(f"⚠️ <b>No limite:</b> chegar ao posto a {dist} km depende de uma margem que a estimativa não garante.", "atencao")
    else:
        caixa(f"🚨 <b>Não chega</b> ao posto a {dist} km. Decida agora: galão, dividir combustível ou mudar de rota.", "perigo")

    if limitado:
        caixa(f"O motor não sustenta {vel} km/h nestas condições. Velocidade realista: cerca de "
              f"{vel_real:.0f} km/h, e o trecho leva mais tempo. Forçar o motor também aumenta o consumo.", "atencao")

    nivel = "baixo" if fadiga < 35 else "moderado" if fadiga < 65 else "alto"
    cor = {"baixo": "ok", "moderado": "atencao", "alto": "perigo"}[nivel]
    caixa(f"🧍 <b>Esforço de pilotagem: {nivel} ({fadiga}/100).</b> Cerca de {horas:.1f} h de pilotagem neste trecho. "
          "Esforço alto pede paradas e o olhar do bem-estar do grupo.", cor)

    if palpite > 0:
        caixa(f"Seu palpite: <b>{palpite} km</b>. Estimativa central: <b>{util:.0f} km</b>. "
              f"Diferença: <b>{palpite - util:+.0f} km</b>.", "info")

    # comparação entre cenários
    if st.button("📌 Fixar este cenário para comparar"):
        st.session_state["fixo"] = (baixo, alto)
    fixo = st.session_state.get("fixo")
    if fixo:
        dif = (baixo + alto) / 2 - (fixo[0] + fixo[1]) / 2
        caixa(f"Cenário fixado: {fixo[0]:.0f} a {fixo[1]:.0f} km. Agora: {baixo:.0f} a {alto:.0f} km. "
              f"Diferença: <b>{dif:+.0f} km</b>.", "info")

    # ---------- GRÁFICO ----------
    secao("🍩", "Onde sua autonomia foi consumida?")
    fatores = [("Arrasto (velocidade, vento, frente, baús)", pen_arrasto, "#2E6F95"),
               ("Peso da carga", pen_peso, "#8E5BA8"),
               ("Terreno", custo_terreno, "#C98A0B"),
               ("Pneus mistos", pen_pneus, "#6B7B4B"),
               ("Frio", pen_frio, "#5BA3C7"),
               ("Motor forçado", pen_motor, "#B3261E")]
    fatores = [f for f in fatores if f[1] > 1e-9]
    soma = sum(f[1] for f in fatores)
    if m > 1.001 and soma > 0:
        perda = ref_util - util
        fatias = [("Autonomia que resta", util, "#2F7D4F")] + [(n, perda * v / soma, c) for n, v, c in fatores]
        df = pd.DataFrame({"Fator": [f"{n} ({k:.0f} km)" for n, k, _ in fatias],
                           "Km": [k for _, k, _ in fatias], "Ordem": range(len(fatias))})
        graf = (alt.Chart(df).mark_arc(innerRadius=60, outerRadius=110)
                .encode(theta=alt.Theta("Km:Q"), order=alt.Order("Ordem:Q"),
                        color=alt.Color("Fator:N", sort=list(df["Fator"]),
                                        scale=alt.Scale(domain=list(df["Fator"]), range=[c for _, _, c in fatias]),
                                        legend=alt.Legend(orient="bottom", columns=1, title=None,
                                                          labelLimit=420, labelFontSize=13)))
                .properties(height=400).configure_view(strokeWidth=0))
        st.altair_chart(graf, use_container_width=True)
        if custo_terreno < 0:
            st.caption("A descida ajudou, e esse ganho já está descontado nas perdas.")
    else:
        caixa("Nenhum fator pesou contra você neste cenário: a moto rende o máximo da tabela.", "ok")

    st.caption("Estimativa didática: percentuais ilustrativos, sem medição real. "
               "A mistura de etanol da gasolina muda por decreto em cada país.")
