"""
🧠 NEUROPLASTICIDADE EM IA — Sistema de Aprendizado Adaptativo
Implementa 5 mecanismos biológicos de neuroplasticidade:
1. Plasticidade Sináptica (ajuste dinâmico de pesos)
2. Neurogênese (criação de novos neurônios)
3. Consolidação de Memória (curto/longo prazo)
4. Inibição Lateral (competição entre neurônios)
5. Reconsolidação (reaprendizado)
"""

import numpy as np
import pandas as pd
from datetime import datetime
from collections import deque
import json
import os


class Neuron:
    """Representa um neurônio artificial com plasticidade"""
    
    def __init__(self, neuron_id, pattern_type, initial_weight=0.5):
        self.id = neuron_id
        self.pattern_type = pattern_type  # "rosa", "boa", "baixa"
        self.weight = initial_weight
        self.activation_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_activation = None
        self.connections = {}  # Conexões com outros neurônios
        self.age = 0  # Idade do neurônio (para poda)
        
    def activate(self, input_strength=1.0):
        """Ativa o neurônio e retorna força de saída"""
        self.activation_count += 1
        self.last_activation = datetime.now()
        return self.weight * input_strength
    
    def reinforce(self, learning_rate=0.1):
        """Reforço positivo — aumenta peso (acerto)"""
        self.success_count += 1
        self.weight = min(1.0, self.weight + learning_rate)
        
    def inhibit(self, learning_rate=0.1):
        """Inibição — reduz peso (erro)"""
        self.failure_count += 1
        self.weight = max(0.0, self.weight - learning_rate)
    
    def get_fitness(self):
        """Calcula fitness do neurônio (para poda)"""
        if self.activation_count == 0:
            return 0
        success_rate = self.success_count / self.activation_count
        return success_rate * self.weight
    
    def get_state(self):
        """Retorna estado do neurônio"""
        return {
            "id": self.id,
            "pattern_type": self.pattern_type,
            "weight": round(self.weight, 4),
            "activation_count": self.activation_count,
            "success_rate": round(self.success_count / max(1, self.activation_count), 4),
            "fitness": round(self.get_fitness(), 4),
            "age": self.age
        }


class NeuroplaticityEngine:
    """Motor de neuroplasticidade com 5 mecanismos biológicos"""
    
    def __init__(self, config):
        self.config = config
        
        # Neurônios (camada oculta)
        self.neurons = {}
        self.neuron_counter = 0
        
        # Memória de curto prazo (últimas 100 rodadas)
        self.short_term_memory = deque(maxlen=100)
        
        # Memória de longo prazo (histórico completo)
        self.long_term_memory = []
        
        # Histórico de consolidação
        self.consolidation_history = []
        
        # Neurônios podados (para rastreamento)
        self.pruned_neurons = []
        
        # Inicializar neurônios para cada padrão
        self._initialize_neurons()
        
    def _initialize_neurons(self):
        """Inicializa neurônios para cada padrão"""
        patterns = ["rosa", "boa", "baixa"]
        for pattern in patterns:
            for i in range(3):  # 3 neurônios por padrão
                neuron_id = f"{pattern}_{i}"
                self.neurons[neuron_id] = Neuron(neuron_id, pattern)
                self.neuron_counter += 1
    
    # ============================================================
    # 1. PLASTICIDADE SINÁPTICA — Ajuste Dinâmico de Pesos
    # ============================================================
    
    def synaptic_plasticity(self, neuron_id, feedback_type, learning_rate=0.1):
        """
        Ajusta pesos sinápticos baseado em feedback
        Simula LTP (Long-Term Potentiation) e LTD (Long-Term Depression)
        """
        if neuron_id not in self.neurons:
            return None
        
        neuron = self.neurons[neuron_id]
        
        if feedback_type == "positive":
            # LTP: Reforço — aumenta peso
            neuron.reinforce(learning_rate)
            return {"type": "LTP", "new_weight": neuron.weight}
        else:
            # LTD: Inibição — reduz peso
            neuron.inhibit(learning_rate)
            return {"type": "LTD", "new_weight": neuron.weight}
    
    # ============================================================
    # 2. NEUROGÊNESE — Criação de Novos Neurônios
    # ============================================================
    
    def neurogenesis(self, pattern_type, trigger_reason="new_pattern"):
        """
        Cria novo neurônio quando detecta novo padrão
        Simula neurogênese do hipocampo
        """
        new_neuron_id = f"{pattern_type}_new_{self.neuron_counter}"
        new_neuron = Neuron(new_neuron_id, pattern_type, initial_weight=0.3)
        
        self.neurons[new_neuron_id] = new_neuron
        self.neuron_counter += 1
        
        return {
            "neuron_id": new_neuron_id,
            "pattern_type": pattern_type,
            "reason": trigger_reason,
            "initial_weight": 0.3,
            "timestamp": datetime.now().isoformat()
        }
    
    # ============================================================
    # 3. CONSOLIDAÇÃO DE MEMÓRIA — Curto/Longo Prazo
    # ============================================================
    
    def consolidate_memory(self, experience):
        """
        Consolida experiência em memória de curto/longo prazo
        Simula consolidação hipocampal
        """
        # Adicionar à memória de curto prazo
        self.short_term_memory.append(experience)
        
        # A cada 10 experiências, consolidar para longo prazo
        if len(self.short_term_memory) % 10 == 0:
            consolidated = {
                "timestamp": datetime.now().isoformat(),
                "short_term_batch": list(self.short_term_memory)[-10:],
                "consolidation_strength": self._calculate_consolidation_strength()
            }
            self.long_term_memory.append(consolidated)
            self.consolidation_history.append(consolidated)
            
            return {
                "status": "consolidated",
                "short_term_size": len(self.short_term_memory),
                "long_term_size": len(self.long_term_memory),
                "consolidation_strength": consolidated["consolidation_strength"]
            }
        
        return {
            "status": "in_short_term",
            "short_term_size": len(self.short_term_memory)
        }
    
    def _calculate_consolidation_strength(self):
        """Calcula força de consolidação baseada em recência"""
        if not self.short_term_memory:
            return 0
        
        # Experiências recentes têm mais força
        total_strength = 0
        for i, exp in enumerate(self.short_term_memory):
            recency_weight = (i + 1) / len(self.short_term_memory)
            total_strength += exp.get("confidence", 0.5) * recency_weight
        
        return min(1.0, total_strength / len(self.short_term_memory))
    
    # ============================================================
    # 4. INIBIÇÃO LATERAL — Competição entre Neurônios
    # ============================================================
    
    def lateral_inhibition(self, pattern_type):
        """
        Neurônios competem para fazer previsão
        Neurônios fracos são inibidos
        Simula inibição lateral do córtex
        """
        # Encontrar neurônios do padrão
        pattern_neurons = {
            nid: n for nid, n in self.neurons.items() 
            if n.pattern_type == pattern_type and n.weight > 0
        }
        
        if not pattern_neurons:
            return None
        
        # Calcular fitness de cada neurônio
        fitness_scores = {
            nid: neuron.get_fitness() 
            for nid, neuron in pattern_neurons.items()
        }
        
        # Neurônio vencedor (maior fitness)
        winner_id = max(fitness_scores, key=fitness_scores.get)
        winner_fitness = fitness_scores[winner_id]
        
        # Inibir neurônios perdedores
        inhibition_results = []
        for nid, neuron in pattern_neurons.items():
            if nid != winner_id:
                # Inibição proporcional à diferença de fitness
                inhibition_strength = (winner_fitness - fitness_scores[nid]) * 0.05
                neuron.weight = max(0.0, neuron.weight - inhibition_strength)
                inhibition_results.append({
                    "neuron_id": nid,
                    "inhibited": True,
                    "new_weight": neuron.weight
                })
        
        return {
            "winner_id": winner_id,
            "winner_fitness": round(winner_fitness, 4),
            "inhibited_neurons": inhibition_results,
            "total_neurons": len(pattern_neurons)
        }
    
    # ============================================================
    # 5. RECONSOLIDAÇÃO — Reaprendizado
    # ============================================================
    
    def reconsolidation(self, neuron_id, new_feedback, strength=0.15):
        """
        Reconsidera memória anterior quando feedback contradiz
        Simula reconsolidação de memória do cérebro
        """
        if neuron_id not in self.neurons:
            return None
        
        neuron = self.neurons[neuron_id]
        old_weight = neuron.weight
        
        # Aplicar novo feedback com força de reconsolidação
        if new_feedback == "positive":
            neuron.weight = min(1.0, neuron.weight + strength)
        else:
            neuron.weight = max(0.0, neuron.weight - strength)
        
        return {
            "neuron_id": neuron_id,
            "old_weight": round(old_weight, 4),
            "new_weight": round(neuron.weight, 4),
            "reconsolidation_strength": strength,
            "timestamp": datetime.now().isoformat()
        }
    
    # ============================================================
    # PODA DE NEURÔNIOS — Remover Neurônios Fracos
    # ============================================================
    
    def prune_weak_neurons(self, fitness_threshold=0.1):
        """
        Remove neurônios com baixo fitness (poda)
        Simula apoptose neuronal
        """
        neurons_to_prune = [
            nid for nid, neuron in self.neurons.items()
            if neuron.get_fitness() < fitness_threshold and neuron.age > 50
        ]
        
        pruned_info = []
        for nid in neurons_to_prune:
            neuron = self.neurons[nid]
            pruned_info.append({
                "neuron_id": nid,
                "fitness": round(neuron.get_fitness(), 4),
                "age": neuron.age,
                "timestamp": datetime.now().isoformat()
            })
            self.pruned_neurons.append(neuron.get_state())
            del self.neurons[nid]
        
        return {
            "pruned_count": len(pruned_info),
            "remaining_neurons": len(self.neurons),
            "pruned_neurons": pruned_info
        }
    
    # ============================================================
    # FAZER PREVISÃO COM NEUROPLASTICIDADE
    # ============================================================
    
    def predict_with_neuroplasticity(self, features):
        """
        Faz previsão usando todos os 5 mecanismos
        """
        # 1. Inibição lateral — encontrar neurônio vencedor por padrão
        predictions = {}
        for pattern in ["rosa", "boa", "baixa"]:
            inhibition_result = self.lateral_inhibition(pattern)
            if inhibition_result:
                predictions[pattern] = {
                    "winner_id": inhibition_result["winner_id"],
                    "confidence": inhibition_result["winner_fitness"]
                }
        
        # Encontrar padrão com maior confiança
        best_pattern = max(
            predictions.items(),
            key=lambda x: x[1]["confidence"]
        )
        
        return {
            "predicted_pattern": best_pattern[0],
            "confidence": round(best_pattern[1]["confidence"], 4),
            "winner_neuron": best_pattern[1]["winner_id"],
            "all_predictions": predictions
        }
    
    # ============================================================
    # ESTATÍSTICAS E MONITORAMENTO
    # ============================================================
    
    def get_neuroplasticity_stats(self):
        """Retorna estatísticas de neuroplasticidade"""
        total_neurons = len(self.neurons)
        avg_weight = np.mean([n.weight for n in self.neurons.values()])
        avg_fitness = np.mean([n.get_fitness() for n in self.neurons.values()])
        
        # Calcular taxa de aprendizado
        total_successes = sum(n.success_count for n in self.neurons.values())
        total_activations = sum(n.activation_count for n in self.neurons.values())
        learning_rate = total_successes / max(1, total_activations)
        
        return {
            "total_neurons": total_neurons,
            "pruned_neurons": len(self.pruned_neurons),
            "avg_weight": round(avg_weight, 4),
            "avg_fitness": round(avg_fitness, 4),
            "learning_rate": round(learning_rate, 4),
            "short_term_memory_size": len(self.short_term_memory),
            "long_term_memory_size": len(self.long_term_memory),
            "consolidations": len(self.consolidation_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_neuron_states(self):
        """Retorna estado de todos os neurônios"""
        return {
            nid: neuron.get_state()
            for nid, neuron in self.neurons.items()
        }
    
    def age_neurons(self):
        """Incrementa idade de todos os neurônios"""
        for neuron in self.neurons.values():
            neuron.age += 1
    
    def save_state(self, filepath):
        """Salva estado da neuroplasticidade em arquivo"""
        state = {
            "neurons": self.get_neuron_states(),
            "stats": self.get_neuroplasticity_stats(),
            "short_term_memory": list(self.short_term_memory),
            "long_term_memory": self.long_term_memory,
            "pruned_neurons": self.pruned_neurons,
            "timestamp": datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        return {"status": "saved", "filepath": filepath}
    
    def load_state(self, filepath):
        """Carrega estado da neuroplasticidade de arquivo"""
        if not os.path.exists(filepath):
            return {"status": "file_not_found"}
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        # Restaurar neurônios
        self.neurons = {}
        for nid, neuron_state in state.get("neurons", {}).items():
            neuron = Neuron(
                neuron_state["id"],
                neuron_state["pattern_type"],
                neuron_state["weight"]
            )
            neuron.activation_count = neuron_state["activation_count"]
            neuron.success_count = int(neuron_state["success_rate"] * neuron_state["activation_count"])
            neuron.age = neuron_state["age"]
            self.neurons[nid] = neuron
        
        return {"status": "loaded", "filepath": filepath}


# ============================================================
# EXEMPLO DE USO
# ============================================================

if __name__ == "__main__":
    import config as cfg
    
    # Inicializar engine
    engine = NeuroplaticityEngine(cfg)
    
    print("🧠 NEUROPLASTICIDADE EM IA")
    print("=" * 50)
    
    # Simular 20 rodadas
    for i in range(20):
        print(f"\n📊 Rodada {i+1}")
        
        # 1. Fazer previsão
        prediction = engine.predict_with_neuroplasticity({})
        print(f"Previsão: {prediction['predicted_pattern']} ({prediction['confidence']})")
        
        # 2. Simular feedback
        feedback = "positive" if np.random.random() > 0.3 else "negative"
        
        # 3. Aplicar plasticidade sináptica
        winner_id = prediction["winner_neuron"]
        synaptic_result = engine.synaptic_plasticity(winner_id, feedback)
        print(f"Plasticidade: {synaptic_result['type']} → novo peso: {synaptic_result['new_weight']}")
        
        # 4. Consolidar memória
        experience = {
            "prediction": prediction["predicted_pattern"],
            "feedback": feedback,
            "confidence": prediction["confidence"],
            "timestamp": datetime.now().isoformat()
        }
        consolidation = engine.consolidate_memory(experience)
        print(f"Memória: {consolidation['status']}")
        
        # 5. A cada 5 rodadas: neurogênese
        if i % 5 == 0:
            new_neuron = engine.neurogenesis("rosa", "new_pattern_detected")
            print(f"Neurogênese: Novo neurônio {new_neuron['neuron_id']}")
        
        # 6. A cada 10 rodadas: poda
        if i % 10 == 0:
            prune_result = engine.prune_weak_neurons()
            print(f"Poda: {prune_result['pruned_count']} neurônios removidos")
        
        # 7. Envelhecer neurônios
        engine.age_neurons()
    
    # Estatísticas finais
    print("\n" + "=" * 50)
    print("📊 ESTATÍSTICAS FINAIS")
    stats = engine.get_neuroplasticity_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
