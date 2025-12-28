from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/agente_betting')

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    """Context manager para sessão do banco"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def test_connection():
    """Testa conexão com o banco"""
    try:
        with get_db() as db:
            result = db.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return False