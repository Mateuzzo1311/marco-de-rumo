import os
import streamlit as st
import pandas as pd

# Configuração da página para TELA INTEIRA (Desktop / Oficina)
st.set_page_config(
    page_title="MARCO DE RUMO - Estação de Planejamento",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para visual de painel de oficina
st.markdown("""
    <style>
    .main { padding: 1rem 2rem; }
    .stMetric { background-color: #1e222a; padding: 12px; border-radius: 8px; border: 1px solid #333; }
    .workshop-header { font-size: 2.2rem; font-weight: 800; color: #ff6b00; margin-bottom: 0px; }
    .workshop-sub { font-size: 1.1rem; color: #a0a0a0; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

LOGO = "LOGOMARCA MARCO DE RUMO MODELADA.png"

# Header da Oficina
head_col1, head_col2 = st.columns([1, 4])
with head_col1:
    if os.path.exists(LOGO):
        st.image(LOGO, width=180)
    else:
        st.title("🏍️ MR")
with head_col2:
    st.markdown('<p class="workshop-header">MARCO DE RUMO — Estação de Planejamento de Expedições</p>', unsafe_allow_html=True)
    st.markdown('<p class="workshop-sub">Simulador didático de física de consumo, aerodinâmica e fadiga para viagens de motocicleta.</p>', unsafe_allow_html=True)

st.divider()

# ---------- TABELAS DE REFERÊNCIA ----------
FAIXAS = {
    "baixa": dict(nome="Baixa (até 400 cc)", tanque=12.0, kml=28.0, folego=1.45, f_peso=1.5),
    "media": dict(nome="Média (401 a 800 cc)", tanque=18.0, kml=22.0, folego=1.90, f_peso=1.0),
    "alta": dict(nome="Alta (acima de 800 cc)", tanque=22.0, kml=17.0, folego=2.60, f_peso=0.5),
}

PERFIS = {
    "Naked / Trail Pequena (Frente Baixa)": 0.8,
    "Big Trail com Para-brisa": 1.0,
    "Touring / Custom Carenada (Ex: Electra, GoldWing)": 1.3,
}

TERRENOS = {
    "Plano": (0.00, 1),
    "Descida Suave": (-0.05, 1),
    "Subida Leve (reduz 1 marcha)": (0.10, 2),
    "Subida Moderada (reduz 2 marchas)": (0.20, 3),
    "Subida Extrema (Cordilheira / Giro Alto)": (0.35, 4),
}

ITENS = {
    "Ferramentas pesadas": 4, "Barraca de emergência": 5, "Kit médico": 3,
    "Drone": 4, "Compressor e kit de remendo": 2, "Galão de combustível (5 L cheio)": 6,
    "Água de reserva": 6, "Comida de reserva": 3, "Saco térmico de emergência": 3,
}
GALAO = "Galão de combustível (5 L cheio)"

PAISES = {
    "Brasil (gasolina com ~32% de etanol)": 1.00,
    "Argentina / Chile (gasolina com ~12-15% de etanol)": 1.05
}

PESO_GARUPA = 65

# ---------- LAYOUT DE TELA INTEIRA (2 COLUNAS PRINCIPAIS) ----------
col_inputs, col_results = st.columns([1, 1], gap="large")

with col_inputs:
    st.header("⚙️ 1. Parâmetros da Expedição")
    
    tab_moto, tab_carga, tab_trecho = st.tabs(["🏍️ Motocicleta", "🧳 Carga e Itens", "🗺️ Trecho e Clima"])
    
    with tab_moto:
        cc = st.number_input("Cilindrada da Moto (cc)", min_value=50, max_value=2500, value=650, step=50)
        faixa = FAIXAS["baixa" if cc <= 400 else "media" if cc <= 800 else "alta"]
        st.info(f"**Classificação Automática:** {faixa['nome']}")
        
        perfil = st.selectbox("Perfil Aerodinâmico", list(PERFIS))
        
        with st.expander("🛠️ Ajustar dados reais de fábrica (Opcional)"):
            tanque_info = st.number_input("Capacidade do Tanque Real (L)", 0.0, 40.0, 0.0, step=1.0)
            kml_info = st.number_input("Consumo Nominal de Estrada (km/l)", 0.0, 60.0, 0.0, step=0.5)
            
        tanque = tanque_info or faixa["tanque"]
        kml_base = kml_info or faixa["kml"]

    with tab_carga:
        c_c1, c_c2 = st.columns(2)
        with c_c1:
            garupa = st.checkbox(f"Garupa ({PESO_GARUPA} kg padrão)")
            baus = st.checkbox("Baús Laterais de Alumínio")
        with c_c2:
            baus_kg = st.number_input("Peso dos Baús Vazios (kg)", 0, 30, 8, step=1) if baus else 0
            bagagem = st.number_input("Bagagem Pessoal (kg)", 0, 80, 25, step=5)
            
        itens = st.multiselect("Itens Coletivos da Expedição", list(ITENS))
        peso = (PESO_GARUPA if garupa else 0) + baus_kg + bagagem + sum(ITENS[i] for i in itens)
        galao = GALAO in itens
        st.success(f"**Peso Adicional Total:** {peso} kg " + ("(+5L Galão Extra)" if galao else ""))

    with tab_trecho:
        t_c1, t_c2 = st.columns(2)
        with t_c1:
            pneus = st.checkbox("Pneus Misto / Off-road")
            frio = st.checkbox("❄️ Frio Extremo (< 10°C)")
        with t_c2:
            pais = st.selectbox("Mistura de Combustível", list(PAISES))
            
        vel = st.slider("Velocidade Alvo de Cruzeiro (km/h)", 60, 130, 100, step=5)
        vento = st.slider("Vento Frontal Estimado (km/h)", 0, 80, 0, step=5)
        terreno = st.selectbox("Topografia Dominante", list(TERRENOS))
        
        st.divider()
        dist = st.number_input("Distância Prevista até o Próximo Abastecimento (km)", 10, 1000, 220, step=10)
        pct = st.slider("Nível do Tanque na Saída (%)", 10, 100, 100, step=10)
        palpite = st.number_input("🎯 Seu Palpite de Autonomia (km) - Desafio do Piloto", 0, 1500, 0, step=10)

# ---------- MOTOR DE CÁLCULO ----------
V_REF = 90
a = 0.30 * PERFIS[perfil] + (0.05 if baus else 0)
pen_arrasto = a * (((vel + vento) / V_REF) ** 2 - 1)
custo_terreno, mult_terreno = TERRENOS[terreno]
pen_peso = (peso / 10) * 0.005 * faixa["f_peso"] * mult_terreno
pen_pneus = 0.05 if pneus else 0.0
pen_frio = 0.04 if frio else 0.0
m = 1 + pen_arrasto + pen_peso + custo_terreno + pen_pneus + pen_frio

limitado = m > faixa["folego"]
pen_motor = 0.10 * m if limitado else 0.0
m += pen_motor
vel_real = max(40, vel * faixa["folego"] / (m - pen_motor)) if limitado else vel

kml = kml_base / m * PAISES[pais]
litros = tanque * pct / 100 + (5 if galao else 0)
ref_util = litros * kml_base * PAISES[pais] * 0.90
util = ref_util / m
baixo, alto = util * 0.90, util * 1.10
horas = dist / vel_real
fadiga = min(100, int((m - 1) * 45 + horas * 7 + (8 if frio else 0)))

# ---------- RESULTADOS NA COLUNA DA DIREITA ----------
with col_results:
    st.header("📊 2. Diagnóstico Didático do Trecho")
    
    # Cartões Principais
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Autonomia Máxima Segura", f"{util:.0f} km", delta=f"{util - ref_util:.0f} km vs Ideal")
    m_col2.metric("Consumo Real Estimado", f"{kml:.1f} km/l", delta=f"{kml - kml_base:.1f} km/l")
    m_col3.metric("Tempo Estimado de Trecho", f"{horas:.1f} h", f"{vel_real:.0f} km/h Média")

    st.divider()

    # Status da Rota
    if baixo >= dist:
        st.success(f"✅ **ROTA SEGURA:** Margem suficiente para alcançar o posto a {dist} km, mesmo no pior cenário ({baixo:.0f} a {alto:.0f} km).")
    elif alto >= dist:
        st.warning(f"⚠️ **ZONA DE RISCO:** Você chegará a {dist} km dependendo da reserva. Condições adversas podem fazer a moto parar antes.")
    else:
        st.error(f"🚨 **PANE SECA PREVISTA:** A autonomia de {util:.0f} km é menor que a distância de {dist} km. Ação necessária: Levar galão extra ou refazer rota.")

    if limitado:
        st.warning(f"🐢 **SOBRECARGA DE MOTOR:** O motor não conseguirá manter {vel} km/h. Velocidade real reduzida para ~{vel_real:.0f} km/h devido ao esforço excessivo.")

    st.divider()

    # Gráfico e Tabela de Perdas
    st.subheader("📉 Onde a sua autonomia foi consumida?")
    
    fatores_dict = {
        "Arrasto Aerodinâmico": max(0, pen_arrasto),
        "Peso de Carga / Garupa": max(0, pen_peso),
        "Topografia / Inclinacao": max(0, custo_terreno),
        "Pneus Misto/Off-road": pen_pneus,
        "Frio Extremo": pen_frio,
        "Esforço Extremo do Motor": pen_motor
    }
    
    df_fatores = pd.DataFrame([
        {"Fator": k, "Impacto (%)": round(v * 100, 1)} for k, v in fatores_dict.items() if v > 0
    ])

    if not df_fatores.empty:
        st.bar_chart(df_fatores.set_index("Fator"))
    else:
        st.info("Sua configuração atual está operando em modo de eficiência ideal (sem penalidades severas).")

    # Análise de Fadiga do Piloto
    st.divider()
    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        nivel_fadiga = "BAIXO" if fadiga < 35 else "MODERADO" if fadiga < 65 else "CRÍTICO"
        st.metric("Índice de Esforço / Fadiga", f"{fadiga}/100", f"Nível: {nivel_fadiga}")
    with f_col2:
        st.caption("💡 **Análise Humana:** O estresse aerodinâmico, frio e tempo de guiada geram desgaste mental e físico. Níveis acima de 65 exigem paradas obrigatórias a cada 1,5h para hidratação e descanso da coluna/punhos.")

    if palpite > 0:
        diff = palpite - util
        st.info(f"🎯 **Desafio do Piloto:** Seu palpite foi de **{palpite} km**. O cálculo científico apontou **{util:.0f} km** (Diferença: **{diff:+.0f} km**). " + 
                ("Você subestimou as perdas aerodinâmicas/topográficas!" if diff > 0 else "Você foi mais cauteloso que a física!"))