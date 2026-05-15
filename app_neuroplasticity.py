"""
🧠 DEMONSTRAÇÃO DE NEUROPLASTICIDADE EM IA
App simples que demonstra os 5 mecanismos de neuroplasticidade
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Configurar página
st.set_page_config(page_title="🧠 Neuroplasticidade em IA", page_icon="🧠", layout="wide")

# CSS customizado
st.markdown("""
<style>
.main { background-color: #050505; color: #ffffff; }
.metric-card { background: #111; border-radius: 8px; padding: 15px; border: 1px solid #333; margin-bottom: 10px; text-align: center; }
.mechanism-box { background: #1a1a2e; border-radius: 8px; padding: 20px; border: 2px solid #00ff00; margin-bottom: 15px; }
.neuron-box { background: #0f3460; border-radius: 8px; padding: 15px; border: 1px solid #00aaff; margin-bottom: 10px; }
.status-good { background: #1a3a1a; border: 2px solid #00ff00; border-radius: 8px; padding: 12px; }
.status-warning { background: #3a2a1a; border: 2px solid #ffaa00; border-radius: 8px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if "neurons" not in st.session_state:
    st.session_state.neurons = {
        "rosa_0": {"weight": 0.50, "activations": 0, "successes": 0, "age": 0},
        "rosa_1": {"weight": 0.45, "activations": 0, "successes": 0, "age": 0},
        "boa_0": {"weight": 0.55, "activations": 0, "successes": 0, "age": 0},
        "boa_1": {"weight": 0.48, "activations": 0, "successes": 0, "age": 0},
        "baixa_0": {"weight": 0.52, "activations": 0, "successes": 0, "age": 0},
    }
    st.session_state.short_term_memory = []
    st.session_state.long_term_memory = []
    st.session_state.pruned_neurons = []
    st.session_state.round_count = 0

# --- HEADER ---
st.title("🧠 NEUROPLASTICIDADE EM IA — Demonstração Interativa")
st.markdown("**5 Mecanismos Biológicos de Aprendizado Implementados**")

# --- ESTATÍSTICAS GERAIS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
    Total de Neurônios<br>
    <b style="font-size:24px; color:#00ff00;">{len(st.session_state.neurons)}</b>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
    Neurônios Podados<br>
    <b style="font-size:24px; color:#ff4444;">{len(st.session_state.pruned_neurons)}</b>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_weight = np.mean([n["weight"] for n in st.session_state.neurons.values()])
    st.markdown(f"""
    <div class="metric-card">
    Peso Médio<br>
    <b style="font-size:24px; color:#00aaff;">{avg_weight:.2f}</b>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
    Rodadas Processadas<br>
    <b style="font-size:24px; color:#ffaa00;">{st.session_state.round_count}</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 5 MECANISMOS DE NEUROPLASTICIDADE ---
st.subheader("🧬 5 Mecanismos de Neuroplasticidade")

# 1. PLASTICIDADE SINÁPTICA
st.markdown("### 1️⃣ Plasticidade Sináptica (Ajuste Dinâmico de Pesos)")
st.markdown("""
**O que é:** Neurônios ajustam a força de suas conexões baseado em feedback
- **LTP (Reforço):** Peso aumenta com acertos
- **LTD (Inibição):** Peso diminui com erros
""")

col_ps1, col_ps2 = st.columns(2)
with col_ps1:
    if st.button("✅ Simular Acerto (LTP)", key="ltp"):
        # Aumentar peso do melhor neurônio
        best_neuron = max(st.session_state.neurons.items(), 
                         key=lambda x: x[1]["weight"])[0]
        st.session_state.neurons[best_neuron]["weight"] = min(
            1.0, 
            st.session_state.neurons[best_neuron]["weight"] + 0.1
        )
        st.session_state.neurons[best_neuron]["successes"] += 1
        st.session_state.neurons[best_neuron]["activations"] += 1
        st.success(f"✅ Peso de {best_neuron} aumentado!")
        st.rerun()

with col_ps2:
    if st.button("❌ Simular Erro (LTD)", key="ltd"):
        # Diminuir peso do pior neurônio
        worst_neuron = min(st.session_state.neurons.items(), 
                          key=lambda x: x[1]["weight"])[0]
        st.session_state.neurons[worst_neuron]["weight"] = max(
            0.0, 
            st.session_state.neurons[worst_neuron]["weight"] - 0.1
        )
        st.session_state.neurons[worst_neuron]["activations"] += 1
        st.error(f"❌ Peso de {worst_neuron} diminuído!")
        st.rerun()

st.markdown("---")

# 2. NEUROGÊNESE
st.markdown("### 2️⃣ Neurogênese (Criação de Novos Neurônios)")
st.markdown("""
**O que é:** IA cria novo neurônio quando detecta novo padrão
- Novo neurônio começa com peso baixo (0.3)
- Se aprende com o tempo
""")

if st.button("🌱 Criar Novo Neurônio", key="neurogenesis"):
    new_id = f"new_{len(st.session_state.neurons)}"
    st.session_state.neurons[new_id] = {
        "weight": 0.3,
        "activations": 0,
        "successes": 0,
        "age": 0
    }
    st.success(f"🌱 Novo neurônio criado: {new_id}")
    st.rerun()

st.markdown("---")

# 3. CONSOLIDAÇÃO DE MEMÓRIA
st.markdown("### 3️⃣ Consolidação de Memória (Curto/Longo Prazo)")
st.markdown("""
**O que é:** Experiências são consolidadas de curto para longo prazo
- Memória de curto prazo: últimas 100 rodadas (flexível)
- Memória de longo prazo: histórico completo (estável)
""")

if st.button("💾 Consolidar Memória", key="consolidation"):
    experience = {
        "timestamp": datetime.now().isoformat(),
        "neurons": {k: v["weight"] for k, v in st.session_state.neurons.items()},
        "round": st.session_state.round_count
    }
    st.session_state.short_term_memory.append(experience)
    
    if len(st.session_state.short_term_memory) >= 10:
        consolidated = {
            "timestamp": datetime.now().isoformat(),
            "batch_size": len(st.session_state.short_term_memory),
            "avg_weights": {
                k: np.mean([e["neurons"][k] for e in st.session_state.short_term_memory])
                for k in st.session_state.neurons.keys()
            }
        }
        st.session_state.long_term_memory.append(consolidated)
        st.session_state.short_term_memory = []
        st.success("💾 Memória consolidada para longo prazo!")
    else:
        st.info(f"📝 Memória de curto prazo: {len(st.session_state.short_term_memory)}/10")
    st.rerun()

st.markdown("---")

# 4. INIBIÇÃO LATERAL
st.markdown("### 4️⃣ Inibição Lateral (Competição entre Neurônios)")
st.markdown("""
**O que é:** Neurônios competem para fazer previsão
- Melhor neurônio "vence"
- Neurônios fracos são inibidos
""")

if st.button("⚔️ Simular Competição", key="lateral_inhibition"):
    # Encontrar vencedor
    winner = max(st.session_state.neurons.items(), 
                key=lambda x: x[1]["weight"])
    
    # Inibir perdedores
    for neuron_id, neuron in st.session_state.neurons.items():
        if neuron_id != winner[0]:
            neuron["weight"] = max(0.0, neuron["weight"] - 0.05)
    
    st.success(f"⚔️ Neurônio vencedor: {winner[0]} (peso: {winner[1]['weight']:.2f})")
    st.rerun()

st.markdown("---")

# 5. RECONSOLIDAÇÃO
st.markdown("### 5️⃣ Reconsolidação (Reaprendizado)")
st.markdown("""
**O que é:** Quando feedback contradiz memória anterior
- IA reconsidera padrão antigo
- Memória é atualizada
""")

if st.button("🔄 Reconsolidar Memória", key="reconsolidation"):
    if st.session_state.long_term_memory:
        # Atualizar pesos baseado em nova informação
        for neuron_id in st.session_state.neurons.keys():
            st.session_state.neurons[neuron_id]["weight"] = min(
                1.0,
                st.session_state.neurons[neuron_id]["weight"] + 0.05
            )
        st.success("🔄 Memória reconsolidada com novo feedback!")
    else:
        st.warning("⚠️ Nenhuma memória de longo prazo para reconsolidar")
    st.rerun()

st.markdown("---")

# PODA DE NEURÔNIOS
st.markdown("### 🧬 Poda de Neurônios (Remover Fracos)")
st.markdown("""
**O que é:** Remove neurônios com baixo fitness
- Simula morte neuronal natural
- Mantém apenas neurônios úteis
""")

if st.button("✂️ Podar Neurônios Fracos", key="pruning"):
    neurons_to_prune = []
    for nid, neuron in st.session_state.neurons.items():
        fitness = neuron["weight"] * (neuron["successes"] / max(1, neuron["activations"]))
        if fitness < 0.2 and neuron["age"] > 5:
            neurons_to_prune.append(nid)
    
    for nid in neurons_to_prune:
        st.session_state.pruned_neurons.append(st.session_state.neurons.pop(nid))
    
    if neurons_to_prune:
        st.success(f"✂️ {len(neurons_to_prune)} neurônios podados!")
    else:
        st.info("ℹ️ Nenhum neurônio fraco para podar")
    st.rerun()

st.markdown("---")

# --- ESTADO DOS NEURÔNIOS ---
st.subheader("🧠 Estado Atual dos Neurônios")

neuron_data = []
for nid, neuron in st.session_state.neurons.items():
    success_rate = neuron["successes"] / max(1, neuron["activations"])
    fitness = neuron["weight"] * success_rate
    neuron_data.append({
        "Neurônio": nid,
        "Peso": f"{neuron['weight']:.2f}",
        "Ativações": neuron["activations"],
        "Sucessos": neuron["successes"],
        "Taxa Sucesso": f"{success_rate*100:.1f}%",
        "Fitness": f"{fitness:.2f}",
        "Idade": neuron["age"]
    })

df_neurons = pd.DataFrame(neuron_data)
st.dataframe(df_neurons, use_container_width=True, hide_index=True)

st.markdown("---")

# --- ESTATÍSTICAS DE MEMÓRIA ---
st.subheader("💾 Estatísticas de Memória")

col_mem1, col_mem2, col_mem3 = st.columns(3)

with col_mem1:
    st.markdown(f"""
    <div class="metric-card">
    Memória Curto Prazo<br>
    <b style="font-size:20px; color:#00ff00;">{len(st.session_state.short_term_memory)}</b>
    </div>
    """, unsafe_allow_html=True)

with col_mem2:
    st.markdown(f"""
    <div class="metric-card">
    Memória Longo Prazo<br>
    <b style="font-size:20px; color:#00aaff;">{len(st.session_state.long_term_memory)}</b>
    </div>
    """, unsafe_allow_html=True)

with col_mem3:
    total_memory = len(st.session_state.short_term_memory) + len(st.session_state.long_term_memory)
    st.markdown(f"""
    <div class="metric-card">
    Memória Total<br>
    <b style="font-size:20px; color:#ffaa00;">{total_memory}</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- INCREMENTAR RODADA ---
if st.button("➕ Próxima Rodada", key="next_round"):
    st.session_state.round_count += 1
    for neuron in st.session_state.neurons.values():
        neuron["age"] += 1
    st.success(f"✅ Rodada {st.session_state.round_count} processada!")
    st.rerun()

st.markdown("---")

# --- FOOTER ---
st.caption("""
🧠 **NEUROPLASTICIDADE EM IA**
- 5 mecanismos biológicos implementados
- Simulação interativa de aprendizado
- Demonstração de como IA aprende como cérebro humano
""")
