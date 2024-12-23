from pydantic import BaseModel
from typing import Union
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# MongoDB Connection
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["FastApi"]  # Replace with your DB name
collection = db["testCollection"]

# Create FastAPI instance
app = FastAPI()

print(client["FastApi"])
# Define the Item model for request body
class Item(BaseModel):
    name: str
    description: Union[str, None] = None  # Optional field
    price: float
    tax: Union[float, None] = None  # Optional field

# Define the ItemDB model for the response, extending the Item model
class ItemDB(Item):
    id: str  # MongoDB ObjectId as a string

# POST API to create an item
@app.post("/items/", response_model=ItemDB)
async def create_item(item: Item):
    item_dict = item.dict()  # Convert Pydantic model to a dictionary
    result = await collection.insert_one(item_dict)  # Insert the item into MongoDB
    created_item = await collection.find_one({"_id": result.inserted_id})  # Retrieve the inserted item
    if created_item:
        created_item["id"] = str(created_item["_id"])  # Convert ObjectId to string
        del created_item["_id"]  # Remove the original ObjectId
        return ItemDB(**created_item)  # Return as ItemDB
    else:
        raise HTTPException(status_code=500, detail="Failed to create item")
