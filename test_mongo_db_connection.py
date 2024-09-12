from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Replace the following with your MongoDB connection string
connection_string = "mongodb+srv://doadmin:Ir69NU72mu15Y3l0@db-mongodb-nyc3-ai-email-22b5feac.mongo.ondigitalocean.com/admin?tls=true&authSource=admin&replicaSet=db-mongodb-nyc3-ai-email"

# Create a MongoClient object
client = MongoClient(connection_string)

# Test the connection
try:
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("MongoDB connection successful")
except ConnectionFailure as e:
    print(f"MongoDB connection failed: {e}")
