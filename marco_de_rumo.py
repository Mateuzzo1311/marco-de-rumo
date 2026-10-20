import streamlit as st

# Configuração da página para formato de celular
st.set_page_config(page_title="MARCO DE RUMO", layout="centered")

# Inserindo a Logomarca
st.image("LOGOMARCA MARCO DE RUMO MODELADA.png", use_container_width=True)

st.title("🏍️ MARCO DE RUMO")
st.write("Previsão preditiva de consumo para mototurismo.")

st.divider()

# 1. DADOS DA BOMBA E PESO
st.subheader("1. Dados Atuais")
col1, col2 = st.columns(2)
with col1:
    capacidade_tanque = st.number_input("Tanque (Litros)", value=22.0, step=1.0)
with col2:
    consumo_bomba = st.number_input("Consumo Base (km/l)", value=20.0, step=0.5)

peso_extra = st.number_input("Peso Adicional: Bagagem + Garupa (kg)", value=0, step=5)

st.divider()

# 2. FATORES DE ARRASTO E ATRITO
st.subheader("2. Equipamento e Clima")
baus_laterais = st.checkbox("Baús Laterais de Alumínio (-10%)")
pneus_mistos = st.checkbox("Pneus de Uso Misto/Off-road (-5%)")
frio_extremo = st.checkbox("❄️ Frio Extremo: Abaixo de 10°C (-4%)")

vento_frontal = st.slider("Vento Frontal Estimado (km/h)", 0, 80, 0, step=5)

st.divider()

# 3. TOPOGRAFIA (Multiplicador de Gravidade)
st.subheader("3. Topografia do Trecho")
terreno = st.selectbox(
    "Selecione a inclinação predominante:",
    ("Plano / Descida", "Subida Leve", "Subida Moderada", "Subida Extrema (Cordilheira)")
)

# --- MOTOR DE CÁLCULO FÍSICO ---

# Base do cálculo
consumo_real = consumo_bomba
penalidade_total = 0.0

# Aplicação dos percentuais de arrasto e clima
if baus_laterais:
    penalidade_total += 0.10
if pneus_mistos:
    penalidade_total += 0.05
if frio_extremo:
    penalidade_total += 0.04

# Penalidade aerodinâmica do vento (Simplificada: ~1% a cada 5km/h de vento contra)
penalidade_vento = (vento_frontal / 5) * 0.01
penalidade_total += penalidade_vento

# Multiplicador de Gravidade (Cruza o peso extra com a inclinação)
# Se estiver no plano, o peso afeta pouco. Na subida, afeta muito.
fator_peso = peso_extra / 100  # Ex: 40kg vira 0.4 de multiplicador

if terreno == "Subida Leve":
    penalidade_total += 0.10 + (0.05 * fator_peso)
elif terreno == "Subida Moderada":
    penalidade_total += 0.20 + (0.10 * fator_peso)
elif terreno == "Subida Extrema (Cordilheira)":
    penalidade_total += 0.35 + (0.20 * fator_peso)

# Desconto final no consumo
consumo_real = consumo_real * (1 - penalidade_total)
autonomia_real = consumo_real * capacidade_tanque

st.divider()

# 4. PAINEL DE RESULTADOS
st.subheader("📊 Resultado Preditivo")

# Formatação visual com cores de alerta
if autonomia_real < 200:
    st.error(f"⚠️ ALERTA: Autonomia Crítica!")
    st.metric(label="Autonomia Máxima Segura", value=f"{autonomia_real:.0f} km")
    st.metric(label="Consumo Corrigido", value=f"{consumo_real:.1f} km/l")
else:
    st.success(f"✅ Rota Segura")
    st.metric(label="Autonomia Máxima Segura", value=f"{autonomia_real:.0f} km")
    st.metric(label="Consumo Corrigido", value=f"{consumo_real:.1f} km/l")

st.info("Dica: Se a distância até o próximo posto for maior que a autonomia máxima, providencie um galão extra agora.")