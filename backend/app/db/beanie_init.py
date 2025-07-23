from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Import your models here when you create them
# from app.features.projects.models import Project


async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(
        database=client.get_default_database(),
        document_models=[],  # Add models here
    )
