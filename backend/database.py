from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# The database URL for asyncpg based on the local docker-compose setup
DATABASE_URL = "postgresql+asyncpg://brvm_user:brvm_password@localhost:5433/brvm_tracker"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Mettre à True pour afficher les logs SQL dans la console
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()

# Dependency SQL pour les requêtes FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
