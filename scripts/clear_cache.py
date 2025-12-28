import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cache.redis_client import RedisCache

def clear_cache():
    print("\n" + "="*60)
    print("🗑️  LIMPANDO CACHE REDIS")
    print("="*60)
    
    cache = RedisCache()
    
    confirm = input("\n⚠️  Isso vai limpar TODOS os dados do cache. Confirma? (s/n): ")
    
    if confirm.lower() == 's':
        success = cache.clear_all()
        if success:
            print("✅ Cache limpo com sucesso!")
        else:
            print("❌ Erro ao limpar cache")
    else:
        print("❌ Operação cancelada")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    clear_cache()