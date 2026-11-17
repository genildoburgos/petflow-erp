import os
from contextlib import contextmanager
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

Base = declarative_base()

def get_database_url() -> str:
    """
    Obtém a URL do banco PostgreSQL a partir de st.secrets ou variável de ambiente.
    Normaliza a URI para compatibilidade total com SQLAlchemy 2.0.
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
    Configurado especificamente para compatibilidade com o Transaction Pooler do Supabase (porta 6543 / PgBouncer).
    """
    db_url = get_database_url()
    
    connect_args = {}
    # Se usando psycopg v3 com Transaction Pooler, desativa prepared statements para evitar erro 'prepared statement already exists'
    if "psycopg" in db_url and "psycopg2" not in db_url:
        connect_args["prepare_threshold"] = None
    
    # Supabase / PostgreSQL pool config
    engine = create_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_recycle=1800,
        pool_pre_ping=True,
        connect_args=connect_args
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
    Testa a conectividade com o PostgreSQL no Supabase e emite alertas preventivos de pooler.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                db_url = get_database_url()
                aviso_extra = ""
                if "supabase.co:5432" in db_url:
                    aviso_extra = " (Dica: Recomendamos usar a porta 6543 Transaction Pooler do Supabase para economizar conexões)."
                return True, f"Conexão ativa com o PostgreSQL{aviso_extra}"
            return False, "Resposta inesperada do banco de dados."
    except Exception as e:
        return False, f"Falha ao conectar ao banco de dados: {str(e)}"
