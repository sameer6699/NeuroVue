from pymongo import MongoClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """
    MongoDB Connection Handler
    This class manages the connection to MongoDB database
    """
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            try:
                # MongoDB connection URI
                self.uri = "mongodb://localhost:27017"
                self.db_name = "NeuroVue"
                
                # Create MongoDB client
                self._client = MongoClient(self.uri)
                
                # Test the connection
                self._client.admin.command('ping')
                logger.info("MongoDB connection established successfully!")
                
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise

    @property
    def client(self):
        """
        Returns the MongoDB client instance
        """
        return self._client

    @property
    def database(self):
        """
        Returns the database instance
        """
        return self._client[self.db_name]

    def close(self):
        """
        Closes the MongoDB connection
        """
        if self._client:
            self._client.close()
            self._client = None 