# 🤖 CLI do Agente de Value Betting

Guia completo de uso do sistema via linha de comando.

---

## 📋 Modos de Uso

### 1. Menu Interativo (Recomendado)
```bash
python3 cli/main.py
```

**Menu com 7 opções:**
- 📊 Ver oportunidades de hoje
- ✅ Registrar resultado de aposta
- 📈 Ver estatísticas
- 📋 Ver histórico de apostas
- 🔄 Forçar transição de fase
- 📁 Exportar dados
- 🧪 Limpar cache Redis

### 2. Comandos Rápidos
```bash
# Ver oportunidades do dia
python3 cli/commands.py today

# Ver estatísticas
python3 cli/commands.py stats

# Ver histórico (últimas 10)
python3 cli/commands.py history

# Ver histórico (últimas N)
python3 cli/commands.py history 20

# Ver ajuda
python3 cli/commands.py help
```

---

## 🚀 Primeiro Uso

### 1. Configure suas API keys

Edite o arquivo `.env`:
```bash
FOOTBALL_API_KEY=sua_key_aqui
ODDS_API_KEY=sua_key_aqui
ENVIRONMENT=development
```

### 2. Inicie o CLI
```bash
python3 cli/main.py
```

### 3. Escolha a opção 1

Digite `1` para ver oportunidades.

### 4. Informe sua banca

Digite o valor da sua banca atual (ex: `100`).

### 5. Analise as oportunidades

O sistema mostrará:
- Jogos com odds reais
- EV calculado
- Stake sugerido
- Retorno potencial

### 6. Registre suas apostas (Opcional)

Responda `s` quando perguntado se quer registrar.

---

## 📊 Opções do Menu

### Opção 1: Ver Oportunidades

**O que faz:**
- Busca jogos reais via APIs
- Calcula probabilidades
- Identifica value bets (EV positivo)
- Sugere stakes baseados na fase

**Exemplo de output:**
```
1. Athletic Club x Espanyol
   Mercado: Over 2.5 | Odd: 2.40
   Probabilidade: 69.2% | EV: +66%
   💰 Stake: R$ 15.00
```

### Opção 2: Registrar Resultado

**O que faz:**
- Lista apostas pendentes
- Permite marcar como won/lost/void
- Atualiza estatísticas

**Quando usar:**
Após o jogo terminar, registre o resultado para manter histórico atualizado.

### Opção 3: Ver Estatísticas

**Métricas mostradas:**
- Total de apostas
- Win rate
- ROI
- Lucro/Prejuízo total
- Odd média

### Opção 4: Ver Histórico

**O que mostra:**
- Últimas N apostas
- Data, jogo, mercado
- Odds e stake
- Status e resultado

### Opção 7: Limpar Cache

**Quando usar:**
- Quando quiser forçar busca de dados novos
- Se odds estiverem desatualizadas

---

## 🎯 Fluxo Recomendado

### Uso Diário
```bash
# 1. De manhã: ver oportunidades
python3 cli/commands.py today

# 2. Anotar apostas interessantes

# 3. Entrar manualmente na casa de apostas

# 4. Registrar no sistema (menu interativo)
python3 cli/main.py
# Opção 2 → Registrar aposta

# 5. Ao final do dia: registrar resultados
python3 cli/main.py
# Opção 2 → Atualizar resultados

# 6. Verificar estatísticas
python3 cli/commands.py stats
```

---

## ⚙️ Configurações Importantes

### Ambiente (Development vs Production)

**Development** (padrão):
- Usa dados simulados se APIs falharem
- Permite testar sem risco

**Production**:
- Só opera com dados reais
- Aborta se APIs não estiverem disponíveis

**Como alterar:**
```bash
# No .env
ENVIRONMENT=production
```

### Gestão de Banca

O sistema ajusta automaticamente baseado na **fase atual**:

| Fase | Meta | Stake Máximo | EV Mínimo |
|------|------|-------------|-----------|
| 1 | R$ 1.000 | 15% | 8% |
| 2 | R$ 5.000 | 10% | 9% |
| 3 | R$ 25.000 | 6% | 10% |
| 4 | R$ 100.000 | 4% | 12% |
| Consolidação | - | 1.5% | 12% |

---

## 🐛 Troubleshooting

### "Nenhuma oportunidade encontrada"

**Possíveis causas:**
- Não há jogos hoje
- Odds não têm EV suficiente
- APIs não retornaram dados

**Solução:**
```bash
# Limpar cache e tentar novamente
python3 cli/main.py
# Opção 7
```

### "APIs não configuradas"

**Solução:**
Edite `.env` e adicione suas keys:
```
FOOTBALL_API_KEY=sua_key
ODDS_API_KEY=sua_key
```

### Cache desatualizado

**Solução:**
```bash
python3 scripts/clear_cache.py
```

---

## 📈 Dicas de Uso

1. **Rode 2x por dia**: Manhã e tarde (odds mudam)
2. **Sempre registre resultados**: Estatísticas são cruciais
3. **Respeite os stakes sugeridos**: Sistema calcula baseado em risco
4. **Limpe cache se necessário**: Cache dura 6h (jogos) e 15min (odds)
5. **Acompanhe o ROI**: Se negativo por 30+ apostas, revise estratégia

---

## 🔗 Links Úteis

- [Documentação completa](../README.md)
- [Checklist de Sprints](../SPRINTS.md)
- [Arquitetura do sistema](ARCHITECTURE.md)