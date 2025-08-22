# 🚀 CryptoAnalyzer Pro - Guia de Instalação Completa

## 📋 **PRÉ-REQUISITOS**

### **1. Sistema Operacional:**
- Ubuntu 20.04+ ou Debian 11+
- Mínimo 4GB RAM, 20GB disco
- Acesso root ou sudo

### **2. Instalar Docker e Docker Compose:**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar sessão ou executar:
newgrp docker
```

## 🔧 **INSTALAÇÃO DO CRYPTOANALYZER PRO**

### **1. Clonar o Repositório:**
```bash
git clone https://github.com/bernini10/CryptoAnalyzer-Pro-Funcional.git
cd CryptoAnalyzer-Pro-Funcional
```

### **2. Configurar Variáveis de Ambiente:**
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais
nano .env
```

**Configurações obrigatórias no .env:**
```env
# Database
DATABASE_URL=postgresql+asyncpg://cryptouser:senha123@postgres:5432/cryptoanalyzer
POSTGRES_USER=cryptouser
POSTGRES_PASSWORD=senha123
POSTGRES_DB=cryptoanalyzer

# Redis
REDIS_URL=redis://redis:6379/0

# APIs (OBRIGATÓRIAS)
COINGECKO_API_KEY=sua-chave-coingecko
GEMINI_API_KEY=sua-chave-gemini

# Notificações (OPCIONAIS)
TELEGRAM_BOT_TOKEN=seu-token-telegram
DISCORD_WEBHOOK_URL=sua-url-discord

# Segurança
SECRET_KEY=sua-chave-secreta-forte
```

### **3. Construir e Iniciar o Sistema:**
```bash
# Construir containers
docker-compose build

# Iniciar sistema
docker-compose up -d

# Verificar status
docker-compose ps
```

### **4. Verificar Funcionamento:**
```bash
# Testar backend
curl http://localhost:8000/health

# Testar frontend
curl http://localhost:3000
```

## 🌐 **ACESSAR O SISTEMA**

### **URLs Locais:**
- **Dashboard**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs

### **URLs Públicas (se configurado):**
- Configure seu firewall para liberar as portas 3000 e 8000
- Use nginx reverse proxy para domínio personalizado

## 📊 **FUNCIONALIDADES DISPONÍVEIS**

### **✅ Dashboard Completo:**
- **Visão Geral**: Market cap, dominância BTC, volume
- **Top 50 Cryptos**: Lista completa com dados em tempo real
- **Análise Técnica**: Indicadores avançados e recomendações IA
- **Alt Season**: Ranking e análise de altcoins promissoras
- **Alertas**: Notificações em tempo real

### **✅ API Backend:**
- **Health Check**: `/health`
- **Lista Cryptos**: `/api/crypto/list`
- **Análise Alt Season**: `/api/analysis/altcoins`
- **Documentação**: `/docs`

## 🔔 **CONFIGURAR NOTIFICAÇÕES**

### **Telegram:**
1. Criar bot no @BotFather
2. Obter token e adicionar no .env
3. Iniciar conversa com o bot
4. Sistema enviará notificações automaticamente

### **Discord:**
1. Criar webhook no seu servidor Discord
2. Adicionar URL no .env
3. Sistema enviará alertas no canal configurado

## 🛠️ **COMANDOS ÚTEIS**

### **Gerenciar Containers:**
```bash
# Ver logs
docker-compose logs -f

# Reiniciar serviços
docker-compose restart

# Parar sistema
docker-compose down

# Atualizar código
git pull
docker-compose build
docker-compose up -d
```

### **Backup do Banco:**
```bash
# Fazer backup
docker exec crypto_postgres pg_dump -U cryptouser cryptoanalyzer > backup.sql

# Restaurar backup
docker exec -i crypto_postgres psql -U cryptouser cryptoanalyzer < backup.sql
```

### **Monitoramento:**
```bash
# Ver uso de recursos
docker stats

# Ver logs específicos
docker-compose logs backend
docker-compose logs frontend
```

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Backend não inicia:**
```bash
# Verificar logs
docker-compose logs backend

# Problemas comuns:
# 1. Banco não conecta - verificar .env
# 2. Porta ocupada - matar processo na porta 8000
# 3. Dependências - rebuild container
```

### **Frontend não carrega:**
```bash
# Verificar se backend está funcionando
curl http://localhost:8000/health

# Verificar logs do nginx
docker-compose logs frontend
```

### **Dados não atualizam:**
```bash
# Verificar conexão com APIs externas
docker exec crypto_backend curl -s https://api.coingecko.com/api/v3/ping

# Reiniciar scheduler
docker-compose restart backend
```

## 📈 **OTIMIZAÇÕES DE PERFORMANCE**

### **Para Produção:**
```bash
# Usar volumes nomeados para dados
# Configurar backup automático
# Usar nginx reverse proxy
# Configurar SSL/HTTPS
# Monitorar recursos com Prometheus
```

### **Escalabilidade:**
```bash
# Adicionar mais workers
# Usar Redis Cluster
# Load balancer para múltiplas instâncias
# CDN para assets estáticos
```

## 🔐 **SEGURANÇA**

### **Recomendações:**
- Trocar senhas padrão
- Usar HTTPS em produção
- Configurar firewall
- Backup regular dos dados
- Monitorar logs de acesso

## 📞 **SUPORTE**

### **Em caso de problemas:**
1. Verificar logs: `docker-compose logs`
2. Consultar documentação da API: http://localhost:8000/docs
3. Verificar issues no GitHub
4. Contatar suporte técnico

---

## 🎉 **SISTEMA PRONTO!**

Após seguir este guia, você terá o **CryptoAnalyzer Pro** funcionando completamente com:

✅ **Dashboard profissional** com todas as funcionalidades
✅ **API backend** robusta e escalável  
✅ **Notificações** Telegram e Discord
✅ **Análises técnicas** avançadas
✅ **Dados em tempo real** de 50+ criptomoedas
✅ **Sistema de alertas** inteligente

**Acesse http://localhost:3000 e comece a usar!**

