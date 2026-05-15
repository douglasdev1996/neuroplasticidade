# 🚀 GUIA DE DEPLOY — Aviator AI v2.0 Otimizado

Este guia mostra como atualizar seu repositório GitHub com a versão otimizada e fazer deploy no Streamlit Cloud.

---

## 📋 Pré-requisitos

- ✅ Conta GitHub
- ✅ Conta Streamlit Cloud (grátis)
- ✅ Git instalado
- ✅ Repositório GitHub já criado

---

## 🔄 Passo 1: Atualizar Repositório Local

### 1.1 Clone o repositório (se ainda não tiver)

```bash
git clone https://github.com/seu-usuario/sniperdefinitivo.git
cd sniperdefinitivo
```

### 1.2 Copie os arquivos otimizados

Copie estes arquivos da pasta `sniperdefinitivo-otimizado/` para seu repositório:

```bash
# Arquivos principais (ATUALIZADOS)
cp ../sniperdefinitivo-otimizado/app.py .
cp ../sniperdefinitivo-otimizado/engine.py .
cp ../sniperdefinitivo-otimizado/config.py .

# Arquivo de núcleo de IA (compatível)
cp ../sniperdefinitivo-otimizado/aviator_ai_core.py .

# Documentação
cp ../sniperdefinitivo-otimizado/README.md .
cp ../sniperdefinitivo-otimizado/DEPLOY.md .
```

### 1.3 Verifique os arquivos

```bash
ls -la
```

Você deve ver:
- ✅ `app.py` (11 KB - versão otimizada com feedback)
- ✅ `engine.py` (12 KB - lógica 5x/10x/3x)
- ✅ `config.py` (1 KB - configurações ajustadas)
- ✅ `aviator_ai_core.py` (13 KB - IA)
- ✅ `requirements.txt`
- ✅ `Procfile`
- ✅ `runtime.txt`
- ✅ `README.md` (novo)
- ✅ `DEPLOY.md` (novo)

---

## 📤 Passo 2: Fazer Push para GitHub

### 2.1 Adicione os arquivos

```bash
git add app.py engine.py config.py aviator_ai_core.py README.md DEPLOY.md
```

### 2.2 Commit

```bash
git commit -m "🚀 Aviator AI v2.0 Otimizado - Entrada 5x, Não entrar <3x, Objetivo 10x, Feedback Loop (RLHF)"
```

### 2.3 Push

```bash
git push origin main
```

**Resultado esperado:**
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 1.23 KiB | 1.23 MiB/s, done.
Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
To github.com:seu-usuario/sniperdefinitivo.git
   abc1234..def5678  main -> main
```

---

## 🌐 Passo 3: Deploy no Streamlit Cloud

### 3.1 Acesse Streamlit Cloud

1. Abra: [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Clique em **"New app"**

### 3.2 Configure a App

1. **GitHub account**: Selecione sua conta
2. **Repository**: `seu-usuario/sniperdefinitivo`
3. **Branch**: `main`
4. **Main file path**: `app.py`

### 3.3 Clique em "Deploy"

A app será implantada automaticamente. Aguarde 2-3 minutos.

**Você verá:**
- ✅ "App is running"
- ✅ URL: `https://seu-app-name.streamlit.app`

---

## ✅ Passo 4: Verificar Deploy

### 4.1 Teste a App

1. Abra a URL da app
2. Aguarde 6-10 segundos para carregar
3. Verifique:
   - ✅ Título: "🚀 AVIATOR AI - BINARY SNIPER MODE v2 (OTIMIZADO)"
   - ✅ Gráfico de velas
   - ✅ Seção "CALIBRAÇÃO COM FEEDBACK" com botão "❌ FEEDBACK NEGATIVO"
   - ✅ Banco de dados mostrando "Velas Boas (5x-9.99x)"

### 4.2 Teste o Feedback

1. Vá para "CALIBRAÇÃO COM FEEDBACK"
2. Insira um valor em "Multiplicador Real Obtido"
3. Clique em "❌ FEEDBACK NEGATIVO"
4. Verifique se aparece: "✅ Feedback registrado! Modelo ajustado."

---

## 🔄 Passo 5: Atualizações Futuras

### Para atualizar a app com novas versões:

```bash
# 1. Copie os arquivos atualizados
cp ../sniperdefinitivo-otimizado/app.py .

# 2. Commit e push
git add app.py
git commit -m "🔄 Atualização v2.1 - Melhorias de performance"
git push origin main

# 3. Streamlit Cloud faz deploy automaticamente (1-2 min)
```

---

## 🛠️ Troubleshooting

### Erro: "Repository not found"

**Solução:**
1. Verifique se o repositório é **público**
2. Verifique se o nome está correto

### Erro: "ModuleNotFoundError"

**Solução:**
1. Verifique `requirements.txt`
2. Adicione a dependência faltante
3. Faça push novamente

### App não atualiza após push

**Solução:**
1. Aguarde 2-3 minutos
2. Recarregue a página (Ctrl+F5)
3. Verifique o log: Clique em "..." → "View logs"

### Erro: "Database is locked"

**Solução:**
1. Clique em "..." → "Reboot app"
2. Aguarde 30 segundos
3. Recarregue a página

---

## 📊 Comparação: Versão Antiga vs v2.0 Otimizado

| Feature | Antiga | v2.0 |
|---------|--------|------|
| Entrada | 2x-10x | **5x-9.9x** ✅ |
| Não entrar | > 2x | **< 3x** ✅ |
| Objetivo | 10x+ | **10x+** ✅ |
| Feedback Negativo | ❌ | **✅** |
| Calibração Manual | ❌ | **✅** |
| Histórico de Feedback | ❌ | **✅** |
| Backtesting | ✅ | **✅ Melhorado** |
| Precisão Alvo | 95% | **99%** ✅ |

---

## 📞 Suporte

### Se algo não funcionar:

1. **Verifique os logs**: Clique em "..." → "View logs"
2. **Reboot a app**: Clique em "..." → "Reboot app"
3. **Atualize o repositório**: `git push origin main`

---

## 🎯 Próximos Passos

Após o deploy bem-sucedido:

1. ✅ Teste a app por 1-2 horas
2. ✅ Use o botão de feedback negativo para calibrar
3. ✅ Monitore a precisão (alvo: 99%)
4. ✅ Colete dados (mínimo 160 rodadas para melhor desempenho)
5. ✅ Ajuste `config.py` se necessário

---

## 📝 Changelog

### v2.0 (Maio 2026)

- ✅ Entrada ajustada para 5x-9.9x
- ✅ Não entrar < 3x
- ✅ Objetivo Rosa ≥ 10x
- ✅ Botão de feedback negativo (RLHF)
- ✅ Calibração automática
- ✅ Histórico de feedback
- ✅ Métricas otimizadas
- ✅ Documentação completa

---

**🚀 Deploy bem-sucedido! Sua app está pronta para uso!**
