import time
from typing import Callable, Any
from functools import wraps

def retry_on_rate_limit(max_retries: int = 3, base_delay: int = 2):
    """Decorator para retry automático em caso de rate limit"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    error_str = str(e)
                    
                    # Detecta rate limit (429)
                    if '429' in error_str or 'rate limit' in error_str.lower():
                        retries += 1
                        
                        if retries >= max_retries:
                            print(f"❌ Rate limit atingido após {max_retries} tentativas")
                            raise
                        
                        # Backoff exponencial
                        delay = base_delay * (2 ** (retries - 1))
                        print(f"⚠️  Rate limit detectado. Aguardando {delay}s... (tentativa {retries}/{max_retries})")
                        time.sleep(delay)
                    else:
                        # Outro erro, propaga
                        raise
            
            return None
        
        return wrapper
    return decorator