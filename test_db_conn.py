import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
import ssl

async def test_conn():
    print(f"Testing connection to: {settings.database_url}")
    ssl_context = ssl.create_default_context()
    
    # Try without SSL first
    try:
        engine = create_async_engine(settings.database_url)
        async with engine.connect() as conn:
            print("Connected successfully without SSL!")
            await engine.dispose()
            return
    except Exception as e:
        print(f"Failed without SSL: {e}")

    # Try with SSL
    try:
        engine = create_async_engine(settings.database_url, connect_args={"ssl": ssl_context})
        async with engine.connect() as conn:
            print("Connected successfully with SSL!")
            await engine.dispose()
            return
    except Exception as e:
        print(f"Failed with SSL: {e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
