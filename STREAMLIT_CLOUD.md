# 🌐 Guia: Deploy no Streamlit Cloud

## Pré-requisitos

- ✅ Repositório GitHub público
- ✅ Conta Streamlit Cloud (grátis em https://streamlit.io/cloud)
- ✅ Arquivos atualizados no repositório

## Passo 1: Preparar Repositório

```bash
# Clone seu repositório
git clone https://github.com/seu-usuario/sniperdefinitivo.git
cd sniperdefinitivo

# Copie os arquivos otimizados
cp ../sniperdefinitivo-otimizado/* .

# Commit e push
git add .
git commit -m "Aviator AI v2.0 Otimizado"
git push origin main
```

## Passo 2: Conectar ao Streamlit Cloud

1. Acesse: https://streamlit.io/cloud
2. Clique em "New app"
3. Selecione:
   - Repository: `seu-usuario/sniperdefinitivo`
   - Branch: `main`
   - Main file: `app.py`
4. Clique em "Deploy"

## Passo 3: Aguardar Deploy

- ⏳ Primeira vez: 2-3 minutos
- ✅ Atualizações: 1-2 minutos
- 🔄 Auto-reload: Ativado por padrão

## Passo 4: Testar

1. Abra a URL da app
2. Verifique:
   - ✅ Título atualizado
   - ✅ Botão de feedback negativo
   - ✅ Classificação 5x/10x/3x

## Troubleshooting

### App não carrega
- Recarregue: Ctrl+F5
- Aguarde 2-3 minutos
- Verifique logs: "..." → "View logs"

### Erro de módulo
- Verifique `requirements.txt`
- Adicione dependência faltante
- Faça push novamente

### Banco de dados travado
- Clique "..." → "Reboot app"
- Aguarde 30 segundos
- Recarregue a página

## Atualizar Futuramente

```bash
# Edite os arquivos localmente
# Commit e push
git add .
git commit -m "Descrição da atualização"
git push origin main

# Streamlit Cloud faz deploy automaticamente
```

## 📊 Monitorar Performance

1. Clique em "..." → "View logs"
2. Verifique:
   - Tempo de carregamento
   - Erros de módulo
   - Uso de memória

## 🔐 Secrets (Opcional)

Se usar API real, adicione em `.streamlit/secrets.toml`:

```toml
SPRIBE_API_KEY = "sua-chave"
SPRIBE_API_URL = "https://api.spribe.co"
```

Não faça commit de `secrets.toml`!

---

**✅ Deploy bem-sucedido! Sua app está ao vivo!**
