#!/usr/bin/env python3
import os
from decimal import Decimal
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "local")
if ENV.lower() == "local":
    URI = os.getenv("MONGODB_URI_LOCAL", "mongodb://localhost:27017/electrohub_nosql")
else:
    URI = os.getenv("MONGODB_URI_ATLAS", "")
DB_NAME = os.getenv("MONGODB_DB_NAME", "electrohub_nosql")

client = MongoClient(URI)
db = client[DB_NAME]

# Clear collections
for coll in ["products", "brands", "categories", "users", "orders", "reviews", "carts"]:
    db[coll].drop()

# Categories
categories = [
    {"name": "Smartphones", "slug": "smartphones", "description": "Mobile phones"},
    {"name": "Laptops", "slug": "laptops", "description": "Laptops & Notebooks"},
    {"name": "Televisions", "slug": "televisions", "description": "TVs"},
    {"name": "Headphones", "slug": "headphones", "description": "Audio devices"},
]
cat_ids = {}
for c in categories:
    res = db.categories.insert_one(c)
    cat_ids[c["slug"]] = res.inserted_id

# Brands
brands = [
    {"name": "Apple"}, {"name": "Samsung"}, {"name": "OnePlus"},
    {"name": "Dell"}, {"name": "ASUS"}, {"name": "Sony"}, {"name": "LG"}, {"name": "Bose"}
]
brand_ids = {}
for b in brands:
    res = db.brands.insert_one(b)
    brand_ids[b["name"]] = res.inserted_id

# Products (subset)
products = [
    {
        "name": "Samsung Galaxy S24", "slug": "samsung-galaxy-s24",
        "brand": {"_id": brand_ids["Samsung"], "name": "Samsung"},
        "category": {"_id": cat_ids["smartphones"], "name": "Smartphones"},
        "description": "Samsung Galaxy S24",
        "price": 74999, "discount_price": 62999, "stock": 15,
        "specifications": [
            {"key": "Display", "value": "6.2-inch Dynamic AMOLED 2X"},
            {"key": "RAM", "value": "8 GB"},
            {"key": "Storage", "value": "256 GB"}
        ],
        "reviews": [], "price_history": [],
        "average_rating": 0, "total_reviews": 0,
        "is_active": True, "is_featured": True,
        "created_at": datetime.utcnow()
    }
]

for p in products:
    db.products.insert_one(p)

# Demo user
db.users.insert_one({
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo12345",
    "created_at": datetime.utcnow()
})

print("Seeded successfully")
print("products:", db.products.count_documents({}), "categories:", db.categories.count_documents({}), "brands:", db.brands.count_documents({}))
client.close()
