"""
Configuración de la base de datos.

Este módulo configura SQLAlchemy para conectarse a PostgreSQL.
Proporciona la sesión de BD y la clase Base para los modelos.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Motor de base de datos
# create_engine crea una conexión pool a PostgreSQL
# pool_pre_ping=True verifica que la conexión esté activa antes de usarla
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexión antes de usar
    echo=False  # Cambiar a True para ver queries SQL en consola (debugging)
)

# Fábrica de sesiones
# Cada request HTTP tendrá su propia sesión de BD
SessionLocal = sessionmaker(
    autocommit=False,  # No hacer commit automático (control manual)
    autoflush=False,   # No hacer flush automático
    bind=engine        # Usar el engine creado arriba
)

# Clase base para todos los modelos
# Todos los modelos heredarán de esta clase
Base = declarative_base()


def get_db():
    """
    Dependency para obtener sesión de base de datos.

    Esta función se usa como dependency en FastAPI endpoints.
    Crea una sesión, la pasa al endpoint, y la cierra automáticamente al terminar.

    Uso en endpoints:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items

    Yields:
        Session: Sesión de SQLAlchemy para hacer queries
    """
    db = SessionLocal()
    try:
        yield db  # Pasar la sesión al endpoint
    finally:
        db.close()  # Cerrar sesión al terminar (siempre se ejecuta)


def create_tables():
    """
    Crea todas las tablas en la base de datos.

    Esta función se llama al iniciar la aplicación (en main.py).
    Lee todos los modelos que heredan de Base y crea sus tablas.
    Si la tabla ya existe, no hace nada.
    """
    Base.metadata.create_all(bind=engine)
