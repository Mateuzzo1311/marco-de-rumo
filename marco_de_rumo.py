import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MARCO DE RUMO", layout="centered")

LOGO = "LOGOMARCA MARCO DE RUMO MODELADA.png"
if os.path.exists(LOGO):
    st.image(LOGO, use_container_width=True)

st.title("🏍️ MARCO DE RUMO")
st.info(
    "Estimativa DIDÁTICA. Os números são ilustrativos e servem para treinar raciocínio. "
    "Não use este resultado para planejar uma viagem real."
)

# ---------- TABELAS DE REFERÊNCIA (valores ilustrativos) ----------
FAIXAS = {
    "baixa": dict(nome="Baixa (até 400 cc)", tanque=12.0, kml=28.0, folego=1.45, f_peso=1.5),
    "media": dict(nome="Média (401 a 800 cc)", tanque=18.0, kml=22.0, folego=1.90, f_peso=1.0),
    "alta": dict(nome="Alta (acima de 800 cc)", tanque=22.0, kml=17.0, folego=2.60, f_peso=0.5),
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
ITENS = {
    "Ferramentas pesadas": 4, "Barraca de emergência": 5, "Kit médico": 3,
    "Drone": 4, "Compressor e kit de remendo": 2, "Galão de combustível (5 L cheio)": 6,
    "Água de reserva": 6, "Comida de reserva": 3, "Saco térmico de emergência": 3,
}
GALAO = "Galão de combustível (5 L cheio)"
PAISES = {"Brasil (gasolina com ~32% de etanol)": 1.00,
          "Argentina (gasolina com ~12 a 15% de etanol)": 1.05}
PESO_GARUPA = 65  # peso-padrão do roteiro; ninguém informa o próprio peso

# ---------- 1. MOTO ----------
st.subheader("1. Sua moto")
cc = st.number_input("Cilindrada (cc)", min_value=50, max_value=2500, value=650, step=50)
faixa = FAIXAS["baixa" if cc <= 400 else "media" if cc <= 800 else "alta"]
st.caption(f"Faixa de referência: {faixa['nome']}. Tanque e consumo vêm de uma tabela didática.")
perfil = st.selectbox("Perfil aerodinâmico (o tamanho da frente que pega o vento)", list(PERFIS))
with st.expander("Conheço os dados da minha moto (opcional)"):
    tanque_info = st.number_input("Tanque (litros)", 0.0, 40.0, 0.0, step=1.0)
    kml_info = st.number_input("Quantos km por litro você faz na estrada?", 0.0, 60.0, 0.0, step=0.5)
tanque = tanque_info or faixa["tanque"]
kml_base = kml_info or faixa["kml"]

# ---------- 2. CARGA ----------
st.subheader("2. Carga")
garupa = st.checkbox(f"Vou com garupa ({PESO_GARUPA} kg, peso-padrão)")
baus = st.checkbox("Baús laterais")
baus_kg = st.number_input("Peso dos baús vazios (kg)", 0, 30, 8, step=1) if baus else 0
bagagem = st.number_input("Bagagem pessoal (kg)", 0, 80, 25, step=5)
itens = st.multiselect("Itens coletivos que eu levo", list(ITENS))
peso = (PESO_GARUPA if garupa else 0) + baus_kg + bagagem + sum(ITENS[i] for i in itens)
galao = GALAO in itens
st.caption(f"Peso adicional total: {peso} kg" + (" · galão: +5 L de combustível" if galao else ""))

# ---------- 3. CONDIÇÕES ----------
st.subheader("3. Condições do trecho")
pneus = st.checkbox("Pneus de uso misto ou off-road")
frio = st.checkbox("❄️ Frio extremo (abaixo de 10 °C)")
pais = st.selectbox("Combustível do país", list(PAISES))
vel = st.slider("Velocidade de cruzeiro (km/h)", 60, 130, 100, step=5)
vento = st.slider("Vento frontal (km/h)", 0, 80, 0, step=5)
terreno = st.selectbox("Terreno predominante", list(TERRENOS))
dist = st.number_input("Distância até o próximo posto (km)", 10, 1000, 200, step=10)
pct = st.slider("Tanque ao sair (%)", 10, 100, 100, step=10)
palpite = st.number_input("Seu palpite de autonomia (km). Anote ANTES de ver o resultado", 0, 1500, 0, step=10)

# ---------- MOTOR DE CÁLCULO ----------
# m = quanto o consumo por km sobe em relação à moto "ideal" (m = 1,0).
V_REF = 90
a = 0.30 * PERFIS[perfil] + (0.05 if baus else 0)          # parte do consumo que é arrasto
pen_arrasto = a * (((vel + vento) / V_REF) ** 2 - 1)         # arrasto cresce com o quadrado da velocidade
custo_terreno, mult_terreno = TERRENOS[terreno]
pen_peso = (peso / 10) * 0.005 * faixa["f_peso"] * mult_terreno  # peso pesa sempre; mais na subida
pen_pneus = 0.05 if pneus else 0.0
pen_frio = 0.04 if frio else 0.0
m = 1 + pen_arrasto + pen_peso + custo_terreno + pen_pneus + pen_frio

limitado = m > faixa["folego"]  # motor sem fôlego para manter a velocidade
pen_motor = 0.10 * m if limitado else 0.0
m += pen_motor
vel_real = max(40, vel * faixa["folego"] / (m - pen_motor)) if limitado else vel

kml = kml_base / m * PAISES[pais]
litros = tanque * pct / 100 + (5 if galao else 0)
ref_util = litros * kml_base * PAISES[pais] * 0.90   # moto ideal, com 10% de reserva
util = ref_util / m
baixo, alto = util * 0.90, util * 1.10                # incerteza do modelo
horas = dist / vel_real
fadiga = min(100, int((m - 1) * 45 + horas * 7 + (8 if frio else 0)))

# ---------- RESULTADO ----------
st.divider()
st.subheader("📊 Resultado estimado")
st.metric("Quilometragem possível (com 10% de reserva)", f"{baixo:.0f} a {alto:.0f} km")
c1, c2 = st.columns(2)
c1.metric("Consumo estimado", f"{kml:.1f} km/l")
c2.metric("Moto ideal, sem carga nem vento", f"{ref_util:.0f} km")

if baixo >= dist:
    st.success(f"✅ Chega ao posto a {dist} km, mesmo no cenário pessimista.")
elif alto >= dist:
    st.warning(f"⚠️ No limite: chegar ao posto a {dist} km depende de margem que a estimativa não garante.")
else:
    st.error(f"🚨 Não chega ao posto a {dist} km. Decida agora: galão, dividir combustível ou mudar de rota.")

if limitado:
    st.warning(
        f"O motor não sustenta {vel} km/h nestas condições. Velocidade realista: cerca de "
        f"{vel_real:.0f} km/h, e o trecho leva mais tempo. Forçar o motor também aumenta o consumo."
    )

nivel = "baixo" if fadiga < 35 else "moderado" if fadiga < 65 else "alto"
st.metric("Esforço de pilotagem", f"{nivel} ({fadiga}/100)")
st.caption(f"Cerca de {horas:.1f} h de pilotagem neste trecho. Esforço alto pede paradas e o olhar do bem-estar do grupo.")

if palpite > 0:
    st.write(f"Seu palpite: **{palpite} km**. Estimativa central: **{util:.0f} km**. Diferença: **{palpite - util:+.0f} km**.")

# O que pesou
st.subheader("O que pesou na sua decisão")
fatores = {
    "Arrasto (velocidade, vento, frente da moto, baús)": pen_arrasto,
    "Peso da carga": pen_peso,
    "Terreno": custo_terreno,
    "Pneus mistos": pen_pneus,
    "Frio": pen_frio,
    "Motor forçado": pen_motor,
}
fatores = {k: v for k, v in fatores.items() if abs(v) > 1e-9}
if m > 1.001:
    perda = ref_util - util
    linhas = [{"Fator": k, "Consumo extra": f"{v * 100:+.0f}%",
               "Km perdidos (aprox.)": f"{perda * v / (m - 1):.0f}"} for k, v in fatores.items()]
    st.table(pd.DataFrame(linhas))
else:
    st.write("Nenhum fator pesou contra você neste cenário.")

st.caption(
    "Estimativa didática: percentuais ilustrativos, sem medição real. "
    "A mistura de etanol da gasolina muda por decreto em cada país."
)