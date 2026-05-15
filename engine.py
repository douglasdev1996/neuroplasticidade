"""
Motor de análise integrado com aprendizado incremental.

Versão otimizada com lógica ajustada:
- Baixa (Recolhimento): < 3x
- Boa (Entrada): 5x - 9.9x
- Rosa (Objetivo): >= 10x

Mantém compatibilidade com a interface original enquanto adiciona
capacidades de aprendizado supervisionado, validação temporal e previsões
probabilísticas via aviator_ai_core.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from aviator_ai_core import (
    AviatorStore,
    PredictionConfig,
    backtest_walk_forward,
    classify_multiplier,
    train_and_predict,
)
# from neuroplasticity import NeuroplaticityEngine  # Comentado para evitar erro


class AnalysisEngine:
    def __init__(self, config):
        self.config = config
        self.sync_factor = 1.0
        self.accuracy = 0.0
        self.calibration_progress = 0
        self.audit_log = []
        self.rounds_observed = 0
        
        # Feedback loop para calibração
        self.feedback_log = []

        # Integração com IA
        self.ai_store = AviatorStore("data/aviator_ai.sqlite")
        self.ai_config = PredictionConfig(
            min_rows_to_train=80,
            min_rows_for_backtest=160,
            horizon=10,
            min_confidence_to_signal=0.58,
        )
        self.last_predictions = pd.DataFrame()
        self.backtest_results = {}
        
        # Rastreamento de padrões de rosas
        self.rosa_history = []
        self.last_rosa_index = -1
        
        # 🧠 NEUROPLASTICIDADE INTEGRADA (desativada por enquanto)
        # self.neuroplasticity = NeuroplaticityEngine(config)  # Será ativada depois
        self.neuroplasticity = None

    def adjust_sync(self, real_data, simulated_data):
        if not real_data or not simulated_data:
            return
        real_mean = np.mean(real_data[-10:]) if len(real_data) >= 10 else np.mean(real_data)
        sim_mean = np.mean(simulated_data[-10:]) if len(simulated_data) >= 10 else np.mean(simulated_data)
        diff = abs(real_mean - sim_mean)
        self.accuracy = max(0.0, 1.0 - (diff / (real_mean + 0.001)))
        self.rounds_observed += 1
        self.calibration_progress = min(100, int((self.rounds_observed / 30) * 100))

    def log_prediction(self, predicted_type, target_mult, actual_multiplier):
        """Registra previsão e ajusta modelo baseado em resultado real."""
        status = "✅ ACERTO" if actual_multiplier >= target_mult else "❌ AJUSTANDO"
        new_entry = {
            "Hora": pd.Timestamp.now().strftime("%H:%M:%S"),
            "Alvo": f"{target_mult}x",
            "Resultado": f"{actual_multiplier}x",
            "Status": status,
        }
        if not self.audit_log or (self.audit_log[0]["Resultado"] != new_entry["Resultado"]):
            self.audit_log.insert(0, new_entry)
        if status == "❌ AJUSTANDO":
            self.sync_factor *= 0.8
        else:
            self.sync_factor *= 1.05
        self.audit_log = self.audit_log[:15]

    def add_negative_feedback(self, predicted_signal, actual_result):
        """
        Registra feedback negativo do usuário para calibração.
        Usado quando o sinal falha e o usuário quer ajustar a IA.
        """
        feedback_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_signal": predicted_signal,
            "actual_result": actual_result,
            "feedback_type": "negative",
            "user_adjustment": True
        }
        self.feedback_log.append(feedback_entry)
        
        # Ajustar fator de sincronização para baixo
        self.sync_factor *= 0.75
        
        # 🧠 NEUROPLASTICIDADE: Aplicar inibição (desativada por enquanto)
        # winner_id = list(self.neuroplasticity.neurons.keys())[0] if self.neuroplasticity and self.neuroplasticity.neurons else None
        # if winner_id:
        #     self.neuroplasticity.synaptic_plasticity(winner_id, "negative", learning_rate=0.15)
        
        # Log para auditoria
        self.audit_log.insert(0, {
            "Hora": pd.Timestamp.now().strftime("%H:%M:%S"),
            "Alvo": f"{predicted_signal}x",
            "Resultado": f"{actual_result}x",
            "Status": "🔧 FEEDBACK NEGATIVO",
        })
        
        return feedback_entry

    def add_positive_feedback(self, predicted_signal, actual_result):
        """
        Registra feedback positivo do usuário para calibração.
        Usado quando o sinal acerta e o usuário quer reforçar a IA.
        """
        feedback_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_signal": predicted_signal,
            "actual_result": actual_result,
            "feedback_type": "positive",
            "user_adjustment": True
        }
        self.feedback_log.append(feedback_entry)
        
        # Ajustar fator de sincronização para cima (reforço)
        self.sync_factor *= 1.15
        
        # 🧠 NEUROPLASTICIDADE: Aplicar reforço (desativada por enquanto)
        # winner_id = list(self.neuroplasticity.neurons.keys())[0] if self.neuroplasticity and self.neuroplasticity.neurons else None
        # if winner_id:
        #     self.neuroplasticity.synaptic_plasticity(winner_id, "positive", learning_rate=0.15)
        
        # Log para auditoria
        self.audit_log.insert(0, {
            "Hora": pd.Timestamp.now().strftime("%H:%M:%S"),
            "Alvo": f"{predicted_signal}x",
            "Resultado": f"{actual_result}x",
            "Status": "✅ FEEDBACK POSITIVO",
        })
        
        return feedback_entry

    def process_data(self, df):
        if df.empty:
            return df
        df = df.tail(100).copy()
        df["ma10"] = df["multiplier"].rolling(window=10).mean()
        df["ma3"] = df["multiplier"].rolling(window=3).mean()
        df["trend"] = np.where(df["ma3"] > df["ma10"], "ALTA", "QUEDA")
        return df

    def update_ai_model(self, df):
        """Atualiza o modelo de IA com novos dados e rastreia padrões de rosas."""
        if df.empty:
            return
        
        for idx, row in df.iterrows():
            multiplier = float(row["multiplier"])
            self.ai_store.add_round(multiplier=multiplier, source="app")
            
            # Rastrear rosas para análise de padrão
            if multiplier >= self.config.ROSA_THRESHOLD:
                self.rosa_history.append({
                    "index": idx,
                    "multiplier": multiplier,
                    "time": row.get("time", "")
                })
                self.last_rosa_index = idx

    def get_ai_predictions(self):
        """Obtém previsões do modelo de IA."""
        rounds = self.ai_store.get_rounds()
        if rounds.empty:
            return pd.DataFrame(), {"status": "sem_dados", "message": "Nenhum dado coletado ainda"}
        predictions, train_info = train_and_predict(rounds, self.ai_config)
        self.last_predictions = predictions
        return predictions, train_info

    def get_backtest_metrics(self):
        """Obtém métricas de backtesting temporal."""
        rounds = self.ai_store.get_rounds()
        if rounds.empty:
            return {"status": "sem_dados", "message": "Nenhum dado coletado ainda"}
        self.backtest_results = backtest_walk_forward(rounds, self.ai_config)
        return self.backtest_results

    def get_database_status(self):
        """Retorna o status atual do banco de dados de IA."""
        rounds = self.ai_store.get_rounds()
        
        if rounds.empty:
            return {
                "total_rounds": 0,
                "rosa_count": 0,
                "boa_count": 0,
                "baixa_count": 0,
                "last_update": "Nunca",
                "learning_status": "⏳ Aguardando dados..."
            }
        
        # Contar por tipo (AJUSTADO PARA 5x/10x)
        rosa_count = len(rounds[rounds["multiplier"] >= self.config.ROSA_THRESHOLD])
        boa_count = len(rounds[(rounds["multiplier"] >= self.config.ENTRADA_MIN) & 
                               (rounds["multiplier"] < self.config.ROSA_THRESHOLD)])
        baixa_count = len(rounds[rounds["multiplier"] < self.config.BAIXA_THRESHOLD])
        
        # Determinar status do aprendizado
        total = len(rounds)
        if total < 80:
            learning_status = f"🔴 Coleta inicial ({total}/80)"
        elif total < 160:
            learning_status = f"🟡 Treinamento básico ({total}/160)"
        else:
            learning_status = f"🟢 Aprendizado ativo ({total} rodadas)"
        
        return {
            "total_rounds": total,
            "rosa_count": rosa_count,
            "boa_count": boa_count,
            "baixa_count": baixa_count,
            "last_update": datetime.now().strftime("%H:%M:%S"),
            "learning_status": learning_status
        }

    def get_rosa_pattern_analysis(self, df):
        """Analisa o padrão de rosas para detectar ciclos."""
        if df.empty or len(df) < 2:
            return None
        
        rosa_indices = df[df["multiplier"] >= self.config.ROSA_THRESHOLD].index.tolist()
        if len(rosa_indices) < 2:
            return None
        
        # Calcular intervalos entre rosas
        intervals = [rosa_indices[i+1] - rosa_indices[i] for i in range(len(rosa_indices)-1)]
        
        if not intervals:
            return None
        
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals) if len(intervals) > 1 else 0
        last_interval = intervals[-1] if intervals else 0
        
        return {
            "total_rosas": len(rosa_indices),
            "avg_interval": avg_interval,
            "std_interval": std_interval,
            "last_interval": last_interval,
            "next_expected": rosa_indices[-1] + avg_interval if rosa_indices else None,
        }

    def detect_patterns(self, df):
        """
        Detecta padrões usando lógica otimizada:
        - Baixa (Recolhimento): < 3x → Não entrar
        - Boa (Entrada): 5x - 9.9x → Entrar
        - Rosa (Objetivo): >= 10x → Alvo
        """
        if df.empty or len(df) < 5:
            return []

        alerts = []
        multipliers = df.tail(15)["multiplier"].tolist()
        last_m = multipliers[-1]

        # Calcular vácuo de rosa
        last_pink_idx = df[df["multiplier"] >= self.config.ROSA_THRESHOLD].index
        rounds_since_pink = len(df) - 1 - last_pink_idx[-1] if not last_pink_idx.empty else len(df)

        # Tendência
        trend = df["trend"].iloc[-1]

        # ===== LÓGICA DE SINAIS OTIMIZADA =====
        
        # 1. VELA ROSA (>= 10x) - FIM DE CICLO
        if last_m >= self.config.ROSA_THRESHOLD:
            alerts.append({
                "type": "🌹 ROSA DETECTADA",
                "message": f"VELA ALTA DETECTADA: {last_m}x. Aguarde o fim do ciclo.",
                "target": 0,
                "confidence": "SEGURANÇA",
                "color": "warning",
            })
            return alerts

        # 2. VELA BAIXA (< 3x) - RECOLHIMENTO
        if last_m < self.config.BAIXA_THRESHOLD:
            if trend == "QUEDA":
                alerts.append({
                    "type": "🔴 RECOLHIMENTO",
                    "message": f"VELA BAIXA ({last_m}x) EM QUEDA: Risco de loss. NÃO ENTRAR.",
                    "target": 1.0,
                    "confidence": "99%",
                    "color": "info",
                })
            else:
                alerts.append({
                    "type": "📊 ACUMULAÇÃO",
                    "message": f"VELA BAIXA ({last_m}x) MAS EM ALTA: Aguarde confirmação.",
                    "target": 0,
                    "confidence": "MÉDIA",
                    "color": "success",
                })
            return alerts

        # 3. VELA BOA (5x - 9.9x) - ENTRADA
        if self.config.ENTRADA_MIN <= last_m < self.config.ROSA_THRESHOLD:
            if trend == "ALTA":
                alerts.append({
                    "type": "🚀 BOA ENTRADA",
                    "message": f"VELA EM ASCENSÃO: {last_m}x. Alvo Rosa ({self.config.ROSA_THRESHOLD}x)!",
                    "target": self.config.ROSA_THRESHOLD,
                    "confidence": "ALTA",
                    "color": "error",
                })
            else:
                alerts.append({
                    "type": "⚠️ VELA BOA MAS CAINDO",
                    "message": f"VELA {last_m}x MAS TENDÊNCIA BAIXISTA: Aguarde reversão.",
                    "target": 0,
                    "confidence": "MÉDIA",
                    "color": "warning",
                })
            return alerts

        # 4. ZONA INTERMEDIÁRIA (3x - 4.99x) - AGUARDAR
        if self.config.BAIXA_THRESHOLD <= last_m < self.config.ENTRADA_MIN:
            if rounds_since_pink >= 15:
                alerts.append({
                    "type": "⏳ ZONA NEUTRA",
                    "message": f"VELA {last_m}x: Aguarde 5x para entrada. Ciclo: {rounds_since_pink} rounds.",
                    "target": self.config.ENTRADA_MIN,
                    "confidence": "MÉDIA",
                    "color": "success",
                })
            else:
                alerts.append({
                    "type": "📈 ACUMULAÇÃO",
                    "message": f"VELA {last_m}x: Aguarde consolidação para entrada.",
                    "target": 0,
                    "confidence": "BAIXA",
                    "color": "success",
                })
            return alerts

        return alerts

    def get_ai_signal_summary(self):
        """Retorna um resumo do sinal de IA para exibição."""
        if self.last_predictions.empty:
            return None

        first_pred = self.last_predictions.iloc[0]
        confidence_pct = first_pred["confidence"] * 100
        predicted_class = first_pred["predicted_label"]
        action = first_pred.get("action", "OBSERVAR")

        color_map = {"baixa": "info", "boa": "success", "rosa": "error"}
        color = color_map.get(predicted_class, "warning")

        return {
            "type": f"🤖 SINAL IA (H1)",
            "message": f"Próxima vela: {predicted_class.upper()} | Confiança: {confidence_pct:.1f}% | Ação: {action}",
            "target": 0,
            "confidence": f"{confidence_pct:.1f}%",
            "color": color,
        }
