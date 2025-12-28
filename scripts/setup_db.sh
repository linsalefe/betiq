#!/bin/bash

echo "🗄️  Criando banco de dados..."

# Cria banco de dados
createdb agente_betting 2>/dev/null || echo "⚠️  Banco já existe"

# Verifica se foi criado
psql -d agente_betting -c "SELECT 'Banco criado com sucesso!' as status;" 

echo "✅ Setup do banco concluído!"