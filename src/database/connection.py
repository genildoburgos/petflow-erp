import os
from contextlib import contextmanager
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

def get_database_url() -> str:
    """
    Obtém a URL do banco PostgreSQL a partir de st.secrets ou variável de ambiente.
    Normaliza a URI para compatibilidade com SQLAlchemy 2.0.
    """
    url = ""
    try:
        if "database" in st.secrets and "url" in st.secrets["database"]:
            url = st.secrets["database"]["url"]
    except Exception:
        pass
    
    if not url:
        url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/petflow_db")
        
    # Normalização para SQLAlchemy: converte postgres:// para postgresql:// se necessário
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    return url

@st.cache_resource
def get_engine():
    """
    Cria e armazena em cache o engine de conexão SQLAlchemy com pool otimizado.
    """
    db_url = get_database_url()
    
    # Supabase / PostgreSQL pool config
    engine = create_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_recycle=1800,
        pool_pre_ping=True
    )
    return engine

def get_session_factory():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """
    Context manager para transações atômicas com a Service Layer.
    Garante commit em caso de sucesso e rollback imediato em caso de erro.
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def test_connection() -> tuple[bool, str]:
    """
    Testa a conectividade com o PostgreSQL no Supabase.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                return True, "Conexão estabelecida com sucesso com o PostgreSQL (Supabase)!"
            return False, "Resposta inesperada do banco de dados."
    except Exception as e:
        return False, f"Falha ao conectar ao banco de dados: {str(e)}"
