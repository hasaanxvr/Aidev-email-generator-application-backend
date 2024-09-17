from pymongo import MongoClient

client = MongoClient('mongodb+srv://doadmin:Ir69NU72mu15Y3l0@db-mongodb-nyc3-ai-email-22b5feac.mongo.ondigitalocean.com/admin?tls=true&authSource=admin&replicaSet=db-mongodb-nyc3-ai-email')

db_name = "email-generation-test"  # Replace with your database name
db = client[db_name]

# Explicitly create collections (if they don't exist)
collection_names = ["email-history", "person-data", "users"]

for collection_name in collection_names:
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        print(f"Collection '{collection_name}' created in database '{db_name}'")
    else:
        print(f"Collection '{collection_name}' already exists in database '{db_name}'")

# Verify the collections were created
collections = db.list_collection_names()
print("\nCollections in database:")
for collection in collections:
    print(f"- {collection}")