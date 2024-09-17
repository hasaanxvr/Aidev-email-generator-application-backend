from pymongo import MongoClient

# Replace the URI string with your MongoDB deployment's connection string.
# For local MongoDB instance, the connection URI is usually mongodb://localhost:27017
client = MongoClient("mongodb+srv://doadmin:Ir69NU72mu15Y3l0@db-mongodb-nyc3-ai-email-22b5feac.mongo.ondigitalocean.com/admin?tls=true&authSource=admin&replicaSet=db-mongodb-nyc3-ai-email")

# List all databases
databases = client.list_database_names()

print("Databases:")
for db in databases:
    print(f"- {db}")


db_name = input("email-generation-test")

if db_name in databases:
    db = client[db_name]
    # List all collections (tables) in the selected database
    collections = db.list_collection_names()
    
    if collections:
        print(f"\nCollections in database '{db_name}':")
        for collection in collections:
            print(f"- {collection}")
    else:
        print(f"No collections found in database '{db_name}'")
else:
    print(f"Database '{db_name}' not found!")