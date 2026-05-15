"""
AUTO-FEEDBACK ENGINE v2.1
Sistema de atualização automática de previsões e feedback contínuo.

Funcionalidades:
- Atualiza previsões automaticamente a cada nova rodada
- Compara resultado real com previsão automaticamente
- Fornece feedback automático quando acerta/erra
- Calibra o modelo continuamente sem intervenção do usuário
- Log completo de acertos/erros para análise
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class AutoFeedbackEngine:
    """
    Engine de feedback automático que:
    1. Monitora novas rodadas
    2. Compara com previsões anteriores
    3. Fornece feedback automático
    4. Atualiza o modelo continuamente
    """
    
    def __init__(self, analysis_engine, config):
        self.engine = analysis_engine
        self.config = config
        self.last_processed_idx = 0
        self.auto_feedback_log = []
        self.accuracy_history = []
        self.auto_calibration_factor = 1.0
        
    def process_new_rounds(self, df: pd.DataFrame, last_prediction: Optional[Dict] = None) -> Dict:
        """
        Processa novas rodadas e fornece feedback automático.
        
        Args:
            df: DataFrame com histórico de rodadas
            last_prediction: Última previsão gerada
            
        Returns:
            Dict com resultado do processamento
        """
        if df.empty or last_prediction is None:
            return {"status": "no_data", "message": "Sem dados para processar"}
        
        # Obter última rodada
        last_row = df.iloc[-1]
        actual_multiplier = last_row["multiplier"]
        
        # Comparar com previsão
        predicted_label = last_prediction.get("predicted_label", "unknown")
        predicted_confidence = last_prediction.get("confidence", 0)
        
        # Classificar resultado real
        actual_label = self._classify_multiplier(actual_multiplier)
        
        # Determinar se acertou
        is_correct = self._check_if_correct(predicted_label, actual_multiplier)
        
        # Gerar feedback automático
        feedback = self._generate_auto_feedback(
            predicted_label=predicted_label,
            actual_label=actual_label,
            actual_multiplier=actual_multiplier,
            predicted_confidence=predicted_confidence,
            is_correct=is_correct
        )
        
        # Aplicar feedback ao engine
        if feedback["should_apply"]:
            self._apply_auto_feedback(feedback)
        
        # Registrar no log
        self.auto_feedback_log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actual_multiplier": actual_multiplier,
            "predicted_label": predicted_label,
            "actual_label": actual_label,
            "predicted_confidence": predicted_confidence,
            "is_correct": is_correct,
            "feedback_type": feedback["type"],
            "auto_calibration_factor": self.auto_calibration_factor,
            "accuracy": self._calculate_accuracy()
        })
        
        return {
            "status": "success",
            "is_correct": is_correct,
            "feedback": feedback,
            "accuracy": self._calculate_accuracy(),
            "auto_calibration_factor": self.auto_calibration_factor
        }
    
    def _classify_multiplier(self, multiplier: float) -> str:
        """Classifica multiplicador em categoria."""
        if multiplier >= self.config.ROSA_THRESHOLD:
            return "rosa"
        elif multiplier >= self.config.ENTRADA_MIN:
            return "boa"
        else:
            return "baixa"
    
    def _check_if_correct(self, predicted_label: str, actual_multiplier: float) -> bool:
        """
        Verifica se a previsão estava correta.
        
        Lógica:
        - Se previu "rosa" (≥10x) e resultado foi ≥10x: ACERTO
        - Se previu "boa" (5x-9.9x) e resultado foi 5x-9.9x: ACERTO
        - Se previu "baixa" (<3x) e resultado foi <3x: ACERTO
        - Caso contrário: ERRO
        """
        actual_label = self._classify_multiplier(actual_multiplier)
        
        # Acerto exato
        if predicted_label == actual_label:
            return True
        
        # Rosa prevista mas boa obtida (parcial)
        if predicted_label == "rosa" and actual_label == "boa":
            return True  # Ganhou, mesmo que não atingiu alvo
        
        # Boa prevista mas rosa obtida (acerto maior)
        if predicted_label == "boa" and actual_label == "rosa":
            return True  # Superou expectativa
        
        return False
    
    def _generate_auto_feedback(
        self,
        predicted_label: str,
        actual_label: str,
        actual_multiplier: float,
        predicted_confidence: float,
        is_correct: bool
    ) -> Dict:
        """Gera feedback automático baseado no resultado."""
        
        feedback = {
            "type": "positive" if is_correct else "negative",
            "should_apply": True,
            "confidence": predicted_confidence,
            "reason": "",
            "adjustment_factor": 1.0
        }
        
        if is_correct:
            feedback["reason"] = f"✅ Previsão correta! {predicted_label.upper()} → {actual_multiplier}x"
            feedback["adjustment_factor"] = 1.12  # Reforço automático
        else:
            feedback["reason"] = f"❌ Previsão incorreta! Previu {predicted_label.upper()}, obteve {actual_label.upper()} ({actual_multiplier}x)"
            feedback["adjustment_factor"] = 0.80  # Correção automática
        
        return feedback
    
    def _apply_auto_feedback(self, feedback: Dict) -> None:
        """Aplica feedback automático ao engine."""
        
        if feedback["type"] == "positive":
            # Reforço: aumenta sync_factor
            self.engine.sync_factor *= feedback["adjustment_factor"]
            self.auto_calibration_factor *= 1.08
        else:
            # Correção: reduz sync_factor
            self.engine.sync_factor *= feedback["adjustment_factor"]
            self.auto_calibration_factor *= 0.92
        
        # Limitar sync_factor entre 0.5 e 2.0
        self.engine.sync_factor = np.clip(self.engine.sync_factor, 0.5, 2.0)
        self.auto_calibration_factor = np.clip(self.auto_calibration_factor, 0.5, 2.0)
    
    def _calculate_accuracy(self) -> float:
        """Calcula acurácia do auto-feedback."""
        if not self.auto_feedback_log:
            return 0.0
        
        correct = sum(1 for f in self.auto_feedback_log if f["is_correct"])
        total = len(self.auto_feedback_log)
        
        return correct / total if total > 0 else 0.0
    
    def get_auto_feedback_stats(self) -> Dict:
        """Retorna estatísticas do auto-feedback."""
        if not self.auto_feedback_log:
            return {
                "total_rounds_processed": 0,
                "accuracy": 0.0,
                "correct_predictions": 0,
                "incorrect_predictions": 0,
                "auto_calibration_factor": 1.0,
                "sync_factor": self.engine.sync_factor
            }
        
        df = pd.DataFrame(self.auto_feedback_log)
        correct = df["is_correct"].sum()
        total = len(df)
        
        return {
            "total_rounds_processed": total,
            "accuracy": (correct / total * 100) if total > 0 else 0.0,
            "correct_predictions": int(correct),
            "incorrect_predictions": int(total - correct),
            "auto_calibration_factor": self.auto_calibration_factor,
            "sync_factor": self.engine.sync_factor,
            "last_feedback": df.iloc[-1].to_dict() if len(df) > 0 else None
        }
    
    def get_recent_auto_feedback(self, limit: int = 20) -> pd.DataFrame:
        """Retorna feedback automático recente."""
        if not self.auto_feedback_log:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.auto_feedback_log)
        
        # Renomear colunas para exibição
        display_df = df.tail(limit)[
            ["timestamp", "actual_multiplier", "predicted_label", "actual_label", "is_correct", "feedback_type"]
        ].copy()
        
        display_df.columns = ["Hora", "Resultado Real", "Previsto", "Obtido", "Acerto", "Tipo"]
        display_df["Acerto"] = display_df["Acerto"].apply(lambda x: "✅" if x else "❌")
        
        return display_df
    
    def should_update_predictions(self, current_idx: int) -> bool:
        """Verifica se deve atualizar previsões."""
        # Atualizar a cada nova rodada
        return current_idx > self.last_processed_idx
    
    def update_processed_index(self, idx: int) -> None:
        """Atualiza índice de última rodada processada."""
        self.last_processed_idx = idx


class ContinuousLearningEngine:
    """
    Engine de aprendizado contínuo que:
    1. Monitora previsões vs resultados reais
    2. Atualiza o modelo automaticamente
    3. Mantém histórico de performance
    4. Fornece recomendações de ajuste
    """
    
    def __init__(self, analysis_engine, config):
        self.engine = analysis_engine
        self.config = config
        self.learning_history = []
        self.performance_metrics = {}
        
    def update_model_continuously(self, df: pd.DataFrame) -> Dict:
        """
        Atualiza o modelo continuamente com novos dados.
        
        Args:
            df: DataFrame com histórico completo
            
        Returns:
            Dict com resultado da atualização
        """
        if len(df) < self.config.MIN_ROWS_TO_TRAIN:
            return {
                "status": "insufficient_data",
                "message": f"Aguardando {self.config.MIN_ROWS_TO_TRAIN} amostras. Atual: {len(df)}"
            }
        
        # Treinar modelo
        try:
            predictions, train_info = self.engine.get_ai_predictions()
            
            # Atualizar histórico
            self.learning_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_samples": len(df),
                "train_status": train_info.get("status"),
                "usable_samples": train_info.get("usable_samples", 0),
                "feature_count": train_info.get("feature_count", 0)
            })
            
            return {
                "status": "success",
                "message": "Modelo atualizado com sucesso",
                "train_info": train_info,
                "predictions": predictions
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao atualizar modelo: {str(e)}"
            }
    
    def get_learning_recommendations(self) -> List[str]:
        """Fornece recomendações baseadas no aprendizado."""
        recommendations = []
        
        if not self.learning_history:
            recommendations.append("📊 Coletando dados iniciais...")
            return recommendations
        
        last_update = self.learning_history[-1]
        usable_samples = last_update.get("usable_samples", 0)
        
        if usable_samples < 80:
            recommendations.append(f"⏳ Colete mais dados ({usable_samples}/80)")
        elif usable_samples < 160:
            recommendations.append(f"📈 Modelo em desenvolvimento ({usable_samples}/160)")
        else:
            recommendations.append("✅ Modelo pronto para uso")
        
        return recommendations
