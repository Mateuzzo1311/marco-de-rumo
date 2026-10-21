import streamlit as st

# Configuração da página para formato de celular
st.set_page_config(page_title="MARCO DE RUMO", layout="centered")

# Inserindo a Logomarca
st.image("LOGOMARCA MARCO DE RUMO MODELADA.png", use_container_width=True)

st.title("🏍️ MARCO DE RUMO")
st.write("Previsão preditiva de consumo para mototurismo.")

st.divider()

# 1. DADOS DA MOTO E PESO
st.subheader("1. Dados da Motocicleta")
col1, col2 = st.columns(2)
with col1:
    capacidade_tanque = st.number_input("Tanque (Litros)", value=22.0, step=1.0)
with col2:
    consumo_bomba = st.number_input("Consumo Base (km/l)", value=20.0, step=0.5)

categoria_motor = st.selectbox(
    "Categoria do Motor (Torque e Fôlego):",
    ("Média Cilindrada (400 a 800cc)", "Baixa Cilindrada (Até 400cc)", "Alta Cilindrada (Acima de 800cc)")
)

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

consumo_real = consumo_bomba
penalidade_total = 0.0

# Aplicação dos percentuais estáticos
if baus_laterais:
    penalidade_total += 0.10
if pneus_mistos:
    penalidade_total += 0.05
if frio_extremo:
    penalidade_total += 0.04

# Penalidade aerodinâmica do vento
penalidade_vento = (vento_frontal / 5) * 0.01

# Ajuste fino: Motores menores sofrem muito mais com a parede de vento
if categoria_motor == "Baixa Cilindrada (Até 400cc)":
    penalidade_vento *= 1.5  # Vento castiga 50% mais o motor pequeno
elif categoria_motor == "Alta Cilindrada (Acima de 800cc)":
    penalidade_vento *= 0.7  # Vento afeta 30% menos o motor grande

penalidade_total += penalidade_vento

# Multiplicador de Gravidade e Peso
fator_peso = peso_extra / 100  # Base: 40kg = 0.4

# Ajuste fino: Como cada motor lida com o peso na subida
if categoria_motor == "Baixa Cilindrada (Até 400cc)":
    fator_peso *= 1.5  # O peso na subida é devastador para o motor pequeno
elif categoria_motor == "Alta Cilindrada (Acima de 800cc)":
    fator_peso *= 0.4  # O torque do motor grande anula boa parte da penalidade do peso

if terreno == "Subida Leve":
    penalidade_total += 0.10 + (0.05 * fator_peso)
elif terreno == "Subida Moderada":
    penalidade_total += 0.20 + (0.10 * fator_peso)
elif terreno == "Subida Extrema (Cordilheira)":
    penalidade_total += 0.35 + (0.20 * fator_peso)

# Aplica o limite lógico (evita que o consumo zere ou fique negativo em cenários extremos)
if penalidade_total > 0.85:
    penalidade_total = 0.85

# Desconto final no consumo
consumo_real = consumo_real * (1 - penalidade_total)
autonomia_real = consumo_real * capacidade_tanque

st.divider()

# 4. PAINEL DE RESULTADOS
st.subheader("📊 Resultado Preditivo")

# Formatação visual com cores de alerta
if autonomia_real < 200:
    st.error(f"⚠️ ALERTA: Autonomia Crítica!")
else:
    st.success(f"✅ Rota Segura")

st.metric(label="Autonomia Máxima Segura", value=f"{autonomia_real:.0f} km")
st.metric(label="Consumo Corrigido", value=f"{consumo_real:.1f} km/l")

# Alerta inteligente para baixa cilindrada
if categoria_motor == "Baixa Cilindrada (Até 400cc)" and (terreno in ["Subida Moderada", "Subida Extrema (Cordilheira)"] or vento_frontal > 30):
    st.warning("⚠️ Atenção: Sob estas condições pesadas, o motor não conseguirá manter a velocidade de cruzeiro. Aumente sua estimativa de TEMPO para concluir este trecho.")

st.info("Dica: Se a distância até o próximo posto for maior que a autonomia máxima, providencie um galão extra agora.")