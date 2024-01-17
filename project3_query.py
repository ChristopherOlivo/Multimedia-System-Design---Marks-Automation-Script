import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["Project2"]
col2 = db["mycollection2"]

# Define the query to find ranges with frames under 6003
query = {"frames": {"$lt": 6003}}
result = col2.find(query)

# Iterate over the query result and print the ranges
for item in result:
    print(item)
