"""Initialize Azure Cosmos DB database and container."""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.identity import DefaultAzureCredential

from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def initialize_cosmos_db_sync() -> bool:
    """
    Initialize Cosmos DB database and container synchronously.
    
    Returns:
        True if successful, False otherwise
    """
    settings = get_settings()
    
    if not settings.cosmos_connection_string:
        logger.error("COSMOS_CONNECTION_STRING not configured")
        return False
    
    try:
        # Check if using Azure AD authentication or connection string
        if "AccountKey=" in settings.cosmos_connection_string:
            # Using connection string with account key
            client = CosmosClient.from_connection_string(settings.cosmos_connection_string)
            logger.info("Connected to Cosmos DB using account key")
        else:
            # Using Azure AD authentication (DefaultAzureCredential)
            # Extract endpoint from connection string or use directly
            endpoint = settings.cosmos_connection_string.replace("AccountEndpoint=", "").replace(";", "").strip()
            if not endpoint.startswith("https://"):
                endpoint = f"https://{settings.cosmos_database_name}.documents.azure.com:443/"
            
            credential = DefaultAzureCredential()
            client = CosmosClient(endpoint, credential)
            logger.info(f"Connected to Cosmos DB using Azure AD authentication: {endpoint}")
        
        # Create database
        try:
            database = client.create_database(id=settings.cosmos_database_name)
            logger.info(f"Created database: {settings.cosmos_database_name}")
        except exceptions.CosmosResourceExistsError:
            database = client.get_database_client(settings.cosmos_database_name)
            logger.info(f"Database already exists: {settings.cosmos_database_name}")
        
        # Create container with partition key
        try:
            container = database.create_container(
                id=settings.cosmos_container_name,
                partition_key=PartitionKey(path="/userId"),
                offer_throughput=400  # Minimum RU/s for manual throughput
            )
            logger.info(f"Created container: {settings.cosmos_container_name}")
            logger.info(f"Partition key: /userId")
            logger.info(f"Throughput: 400 RU/s")
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(settings.cosmos_container_name)
            logger.info(f"Container already exists: {settings.cosmos_container_name}")
        
        # Verify container configuration
        container_properties = container.read()
        logger.info(f"Container properties: {container_properties.get('id')}")
        logger.info(f"Partition key path: {container_properties.get('partitionKey', {}).get('paths')}")
        
        logger.info("✅ Cosmos DB initialization successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Cosmos DB: {e}", exc_info=True)
        return False


async def initialize_cosmos_db_async() -> bool:
    """
    Initialize Cosmos DB database and container asynchronously.
    
    Returns:
        True if successful, False otherwise
    """
    settings = get_settings()
    
    if not settings.cosmos_connection_string:
        logger.error("COSMOS_CONNECTION_STRING not configured")
        return False
    
    try:
        # Create async Cosmos client
        async with AsyncCosmosClient.from_connection_string(
            settings.cosmos_connection_string
        ) as client:
            logger.info("Connected to Cosmos DB (async)")
            
            # Create database
            try:
                database = await client.create_database(id=settings.cosmos_database_name)
                logger.info(f"Created database: {settings.cosmos_database_name}")
            except exceptions.CosmosResourceExistsError:
                database = client.get_database_client(settings.cosmos_database_name)
                logger.info(f"Database already exists: {settings.cosmos_database_name}")
            
            # Create container with partition key
            try:
                container = await database.create_container(
                    id=settings.cosmos_container_name,
                    partition_key=PartitionKey(path="/userId"),
                    offer_throughput=400  # Minimum RU/s for manual throughput
                )
                logger.info(f"Created container: {settings.cosmos_container_name}")
                logger.info(f"Partition key: /userId")
                logger.info(f"Throughput: 400 RU/s")
            except exceptions.CosmosResourceExistsError:
                container = database.get_container_client(settings.cosmos_container_name)
                logger.info(f"Container already exists: {settings.cosmos_container_name}")
            
            # Verify container configuration
            container_properties = await container.read()
            logger.info(f"Container properties: {container_properties.get('id')}")
            logger.info(f"Partition key path: {container_properties.get('partitionKey', {}).get('paths')}")
            
            logger.info("✅ Cosmos DB initialization successful (async)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize Cosmos DB (async): {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    logger.info("Starting Cosmos DB initialization...")
    logger.info("=" * 60)
    
    # Try synchronous initialization first
    success = initialize_cosmos_db_sync()
    
    if not success:
        logger.error("Initialization failed")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Cosmos DB is ready for use")
    sys.exit(0)


if __name__ == "__main__":
    main()
