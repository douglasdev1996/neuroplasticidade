import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import config as cfg
from engine import AnalysisEngine
from auto_feedback import AutoFeedbackEngine, ContinuousLearningEngine

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AVIATOR AI BINARY PRO", page_icon="📈", layout="wide")
HISTORY_FILE = "data/history_v5.csv"
os.makedirs("data", exist_ok=True)

# --- CSS CUSTOMIZADO ---
st.markdown(
    """
    <style>
    .main { background-color: #050505; color: #ffffff; }
    .metric-card { background: #111; border-radius: 8px; padding: 15px; border: 1px solid #333; margin-bottom: 10px; text-align: center; }
    .signal-box { padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 20px; border: 2px solid #444; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #ff00ff, #00ffff) !important; }
    .ai-metrics { background: #0a0a0a; border: 1px solid #00ff00; border-radius: 8px; padding: 12px; margin: 10px 0; }
    .db-status { background: #0a0a0a; border: 1px solid #ffaa00; border-radius: 8px; padding: 12px; margin: 10px 0; font-family: monospace; }
    .feedback-positive { background: #1a3a1a; border: 2px solid #00ff00; border-radius: 8px; padding: 12px; margin: 10px 0; }
    .feedback-negative { background: #3a1a1a; border: 2px solid #ff4444; border-radius: 8px; padding: 12px; margin: 10px 0; }
    .auto-feedback { background: #1a2a3a; border: 2px solid #00aaff; border-radius: 8px; padding: 12px; margin: 10px 0; }
    .status-stable { background: #1a3a1a; border: 2px solid #00ff00; border-radius: 8px; padding: 12px; margin: 10px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "engine" not in st.session_state:
    st.session_state.engine = AnalysisEngine(cfg)
    st.session_state.auto_feedback = AutoFeedbackEngine(st.session_state.engine, cfg)
    st.session_state.continuous_learning = ContinuousLearningEngine(st.session_state.engine, cfg)
    st.session_state.current_alert = None
    st.session_state.current_predictions = None
    st.session_state.df_cache = None
    st.session_state.last_update_time = None

engine = st.session_state.engine
auto_feedback = st.session_state.auto_feedback
continuous_learning = st.session_state.continuous_learning


def load_data_stable():
    """
    Carrega dados do histórico SEM gerar novos dados aleatórios.
    Apenas lê dados existentes.
    """
    if not os.path.exists(HISTORY_FILE):
        # Criar arquivo vazio se não existir
        df = pd.DataFrame(columns=["multiplier", "time"])
        df.to_csv(HISTORY_FILE, index=False)
        return df
    
    # Apenas ler dados existentes - NÃO gerar novos!
    df = pd.read_csv(HISTORY_FILE)
    
    if df.empty:
        st.warning("⏳ Aguardando dados da plataforma Spribe...")
        return df
    
    return df.tail(100)


# --- CARREGAMENTO DE DADOS (SEM GERAR NOVOS) ---
df = load_data_stable()

# Se não há dados, mostrar mensagem e parar
if df.empty:
    st.title("🚀 AVIATOR AI - BINARY SNIPER MODE v2.3 (ESTÁVEL)")
    st.error("❌ Nenhum dado disponível")
    st.info("""
    ⏳ A app está aguardando dados da plataforma Spribe.
    
    **Como funciona:**
    1. Você abre a plataforma Spribe em outro navegador
    2. A IA monitora os multiplicadores em tempo real
    3. Quando novos dados chegam, a app atualiza automaticamente
    4. As previsões ficam FIXAS durante toda a rodada
    
    **Status:** Aguardando primeira rodada...
    """)
    st.stop()

# Processar dados APENAS UMA VEZ (armazenar em cache)
if st.session_state.df_cache is None or len(df) != len(st.session_state.df_cache):
    # Novos dados detectados
    st.session_state.df_cache = df.copy()
    st.session_state.last_update_time = datetime.now()
    
    processed_df = engine.process_data(df)
    engine.update_ai_model(df)
    alerts = engine.detect_patterns(processed_df)
    
    # Obter previsões
    predictions, train_info = engine.get_ai_predictions()
    last_prediction = predictions.iloc[0].to_dict() if not predictions.empty else None
    
    # Auto-feedback
    if last_prediction is not None:
        auto_result = auto_feedback.process_new_rounds(df, last_prediction)
    
    # Armazenar
    st.session_state.current_alert = alerts[0] if alerts else None
    st.session_state.current_predictions = predictions
else:
    # Usar dados armazenados (SEM reprocessar)
    processed_df = engine.process_data(df)
    alerts = [st.session_state.current_alert] if st.session_state.current_alert else []
    predictions = st.session_state.current_predictions if st.session_state.current_predictions is not None else pd.DataFrame()

# Calcular vácuo de rosa
last_pink_idx = df[df["multiplier"] >= cfg.ROSA_THRESHOLD].index
if not last_pink_idx.empty:
    rounds_since_pink = len(df) - 1 - last_pink_idx[-1]
else:
    rounds_since_pink = len(df)

# --- UI PRINCIPAL ---
st.title("🚀 AVIATOR AI - BINARY SNIPER MODE v2.3 (ESTÁVEL)")

# Status de estabilidade
st.markdown(
    f'''
    <div class="status-stable">
    ✅ STATUS: ESTÁVEL<br>
    📊 Rodadas carregadas: <b>{len(df)}</b><br>
    ⏰ Última atualização: <b>{st.session_state.last_update_time.strftime("%H:%M:%S") if st.session_state.last_update_time else "N/A"}</b><br>
    🔒 Previsão FIXA durante a rodada<br>
    🚫 Sem recarregamentos aleatórios
    </div>
    ''',
    unsafe_allow_html=True,
)

st.progress(engine.calibration_progress / 100, text=f"Calibração de Mercado: {engine.calibration_progress}%")

# MÉTRICAS
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f'<div class="metric-card">Último Resultado<br><b style="font-size:24px; color:#00ffff;">{df["multiplier"].iloc[-1]}x</b></div>',
        unsafe_allow_html=True,
    )
with c2:
    trend = processed_df["trend"].iloc[-1]
    color = "#00ff00" if trend == "ALTA" else "#ff0000"
    st.markdown(
        f'<div class="metric-card">Tendência Atual<br><b style="font-size:24px; color:{color};">{trend}</b></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="metric-card">Vácuo de Rosa<br><b style="font-size:24px; color:#ff00ff;">{rounds_since_pink} Rds</b></div>',
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f'<div class="metric-card">Precisão IA<br><b style="font-size:24px; color:#7000ff;">{engine.accuracy*100:.1f}%</b></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- SEÇÃO DE AUTO-FEEDBACK ---
auto_stats = auto_feedback.get_auto_feedback_stats()
if auto_stats["total_rounds_processed"] > 0:
    st.subheader("🤖 AUTO-FEEDBACK — Aprendizado Contínuo em Tempo Real")
    
    col_af1, col_af2, col_af3, col_af4 = st.columns(4)
    
    with col_af1:
        st.markdown(
            f'<div class="metric-card">Rodadas Processadas<br><b style="font-size:20px; color:#00ff00;">{auto_stats["total_rounds_processed"]}</b></div>',
            unsafe_allow_html=True,
        )
    
    with col_af2:
        st.markdown(
            f'<div class="metric-card">Acurácia Auto<br><b style="font-size:20px; color:#00ff00;">{auto_stats["accuracy"]:.1f}%</b></div>',
            unsafe_allow_html=True,
        )
    
    with col_af3:
        st.markdown(
            f'<div class="metric-card">Acertos<br><b style="font-size:20px; color:#00ff00;">✅ {auto_stats["correct_predictions"]}</b></div>',
            unsafe_allow_html=True,
        )
    
    with col_af4:
        st.markdown(
            f'<div class="metric-card">Erros<br><b style="font-size:20px; color:#ff4444;">❌ {auto_stats["incorrect_predictions"]}</b></div>',
            unsafe_allow_html=True,
        )
    
    if auto_stats["last_feedback"]:
        last_fb = auto_stats["last_feedback"]
        fb_type = "✅ POSITIVO" if last_fb["is_correct"] else "❌ NEGATIVO"
        fb_color = "#00ff00" if last_fb["is_correct"] else "#ff4444"
        
        st.markdown(
            f'''
            <div class="auto-feedback">
            <h3 style="color:{fb_color};">Último Auto-Feedback: {fb_type}</h3>
            <p>Previsto: <b>{last_fb["predicted_label"].upper()}</b> | Obtido: <b>{last_fb["actual_label"].upper()} ({last_fb["actual_multiplier"]}x)</b></p>
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    st.markdown("---")

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📊 Gráfico de Fluxo de Velas")
    st.line_chart(processed_df.tail(30).set_index("time")[["multiplier", "ma3", "ma10"]])
    target_url = st.text_input("🔗 LINK DA PLATAFORMA", value="https://spribe.co/games/aviator")
    st.iframe(target_url, height=500)

with col_right:
    st.subheader("🎯 SINAL DE OPERAÇÃO")
    if alerts:
        a = alerts[0]
        color = "#ff4b4b" if a["color"] == "error" else ("#ffaa00" if a["color"] == "warning" else "#3498db")
        st.markdown(
            f'<div class="signal-box" style="border-color:{color}; background:rgba(255,255,255,0.05);"><h1 style="color:{color};">{a["type"]}</h1><h3>{a["message"]}</h3><p>Confiança: {a["confidence"]}</p></div>',
            unsafe_allow_html=True,
        )
        if a["target"] > 0:
            engine.log_prediction(a["type"], a["target"], df["multiplier"].iloc[-1])
    else:
        st.markdown("<div class=\"signal-box\"><h2>ANALISANDO FLUXO...</h2></div>", unsafe_allow_html=True)

    st.subheader("🛡️ AUDITORIA DE PRECISÃO")
    if engine.audit_log:
        st.dataframe(pd.DataFrame(engine.audit_log), use_container_width=False, hide_index=True)

st.markdown("---")

# --- SEÇÃO DE FEEDBACK MANUAL ---
st.subheader("🔧 CALIBRAÇÃO MANUAL COM FEEDBACK (RLHF)")

col_fb1, col_fb2 = st.columns([1.5, 1])

with col_fb1:
    st.markdown("**📍 Último Sinal Gerado:**")
    if alerts:
        st.info(f"{alerts[0]['type']}\n\n{alerts[0]['message']}")
    else:
        st.info("Nenhum sinal gerado ainda")
    
    st.markdown("**📊 Resultado Real Obtido:**")
    real_result = st.number_input("Multiplicador Real Obtido:", min_value=1.0, max_value=500.0, value=df["multiplier"].iloc[-1], step=0.1)

with col_fb2:
    st.markdown("**⚙️ Calibração Manual:**")
    
    if st.button("✅ FEEDBACK POSITIVO", key="positive_feedback", use_container_width=True):
        if alerts:
            engine.add_positive_feedback(alerts[0]["type"], real_result)
            st.markdown(
                '<div class="feedback-positive"><h3>🎉 FEEDBACK POSITIVO!</h3></div>',
                unsafe_allow_html=True
            )
            st.success(f"✅ sync_factor: {engine.sync_factor:.2f}")
            st.balloons()
        else:
            st.warning("⚠️ Nenhum sinal para feedback")
    
    st.markdown("")
    
    if st.button("❌ FEEDBACK NEGATIVO", key="negative_feedback", use_container_width=True):
        if alerts:
            engine.add_negative_feedback(alerts[0]["type"], real_result)
            st.markdown(
                '<div class="feedback-negative"><h3>⚠️ FEEDBACK NEGATIVO!</h3></div>',
                unsafe_allow_html=True
            )
            st.error(f"❌ sync_factor: {engine.sync_factor:.2f}")
        else:
            st.warning("⚠️ Nenhum sinal para feedback")

st.markdown("---")

# --- SEÇÃO DE IA INTEGRADA ---
st.subheader("🤖 INTELIGÊNCIA INTEGRADA")

col_ai_1, col_ai_2 = st.columns([1, 1])

with col_ai_1:
    st.markdown("**Previsões das próximas 10 rodadas**")
    if predictions.empty:
        st.info("⏳ Coletando dados...")
    else:
        st.success(f"✅ Modelo treinado | Amostras: {len(df)}")
        display_pred = predictions.copy()
        display_pred["confiança"] = (display_pred["confidence"] * 100).round(1).astype(str) + "%"
        display_pred = display_pred[["horizon", "predicted_label", "confiança"]]
        st.dataframe(display_pred, use_container_width=False, hide_index=True)

with col_ai_2:
    st.markdown("**Backtesting Temporal**")
    backtest = engine.get_backtest_metrics()
    
    if backtest.get("status") != "ok":
        st.info(f"⏳ {backtest.get('message', 'Coletando...')}")
    else:
        b1, b2 = st.columns(2)
        b1.metric("Acurácia", f"{backtest['accuracy']*100:.1f}%")
        b2.metric("Balanceada", f"{backtest['balanced_accuracy']*100:.1f}%")

st.markdown("---")

# --- STATUS DO BANCO DE DADOS ---
st.subheader("💾 STATUS DO BANCO DE DADOS")
db_status = engine.get_database_status()
st.markdown(
    f"""
    <div class="db-status">
    📊 Total de rodadas: <b>{db_status['total_rounds']}</b><br>
    🌹 Rosas (≥{cfg.ROSA_THRESHOLD}x): <b>{db_status['rosa_count']}</b><br>
    🔵 Boas ({cfg.ENTRADA_MIN}x-{cfg.ENTRADA_MAX}x): <b>{db_status['boa_count']}</b><br>
    🔴 Baixas (<{cfg.BAIXA_THRESHOLD}x): <b>{db_status['baixa_count']}</b>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# --- ANÁLISE DE PADRÕES ---
st.subheader("🌸 ANÁLISE DE PADRÕES")

df_copy = df.copy()
df_copy["tipo"] = df_copy["multiplier"].apply(
    lambda x: f"🌹 Rosa (≥{cfg.ROSA_THRESHOLD}x)" if x >= cfg.ROSA_THRESHOLD 
    else (f"🔵 Boa ({cfg.ENTRADA_MIN}x-{cfg.ENTRADA_MAX}x)" if x >= cfg.ENTRADA_MIN 
    else f"🔴 Baixa (<{cfg.BAIXA_THRESHOLD}x)")
)

tipo_counts = df_copy["tipo"].value_counts()
col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    count_rosa = tipo_counts.get(f"🌹 Rosa (≥{cfg.ROSA_THRESHOLD}x)", 0)
    st.metric("🌹 Rosas", count_rosa)

with col_p2:
    count_boa = tipo_counts.get(f"🔵 Boa ({cfg.ENTRADA_MIN}x-{cfg.ENTRADA_MAX}x)", 0)
    st.metric("🔵 Boas", count_boa)

with col_p3:
    count_baixa = tipo_counts.get(f"🔴 Baixa (<{cfg.BAIXA_THRESHOLD}x)", 0)
    st.metric("🔴 Baixas", count_baixa)

st.markdown("---")

st.subheader("📋 Histórico")
if not df.empty:
    display = df.tail(50).copy()
    display["tipo"] = display["multiplier"].apply(
        lambda x: f"🌹 Rosa" if x >= cfg.ROSA_THRESHOLD 
        else (f"🔵 Boa" if x >= cfg.ENTRADA_MIN else "🔴 Baixa")
    )
    st.dataframe(display, use_container_width=False, hide_index=True)

st.markdown("---")

if auto_stats["total_rounds_processed"] > 0:
    st.subheader("📝 HISTÓRICO DE AUTO-FEEDBACK")
    recent_auto_fb = auto_feedback.get_recent_auto_feedback(limit=20)
    if not recent_auto_fb.empty:
        st.dataframe(recent_auto_fb, use_container_width=False, hide_index=True)

if engine.feedback_log:
    st.subheader("📝 HISTÓRICO DE FEEDBACK MANUAL")
    feedback_df = pd.DataFrame(engine.feedback_log)
    feedback_df = feedback_df[["timestamp", "feedback_type", "predicted_signal", "actual_result"]]
    feedback_df.columns = ["Hora", "Tipo", "Sinal", "Resultado"]
    st.dataframe(feedback_df.tail(20), use_container_width=False, hide_index=True)

st.caption(
    f"✅ VERSÃO v2.3 ESTÁVEL — SEM RECARREGAMENTOS ALEATÓRIOS!\n"
    f"🔒 Previsões FIXAS durante a rodada | 🚫 Sem dados simulados aleatórios\n"
    f"📊 Entrada: 5x-9.9x | Não entrar: <3x | Objetivo: ≥10x"
)

# ⚠️ IMPORTANTE: NÃO USAR st.rerun() ou time.sleep()
# A app agora é ESTÁVEL e mantém previsões FIXAS
