from django.apps import AppConfig
from config.mongodb import MongoDBConnection

class WebProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_project'

    def ready(self):
        """
        This method is called when Django starts
        """
        try:
            # Initialize MongoDB connection
            mongo_connection = MongoDBConnection()
            print("\n" + "="*50)
            print("MongoDB Connection Establish Successfully!")
            print("="*50 + "\n")
        except Exception as e:
            print("\n" + "="*50)
            print(f"MongoDB Connection Failed: {str(e)}")
            print("="*50 + "\n") 