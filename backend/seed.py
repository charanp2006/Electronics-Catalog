#!/usr/bin/env python3
"""Seed the ElectroHub database with sample catalog data.

Usage:
    python seed.py

Drops and recreates the core collections, inserts categories, brands,
products (with embedded specs/reviews/price history), a sample user and
required indexes.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient

from app.core.config import settings

load_dotenv()


def now() -> datetime:
    return datetime.now(timezone.utc)


def days_ago(n: int) -> datetime:
    return now() - timedelta(days=n)


def image_for(slug: str) -> str:
    return f"https://picsum.photos/seed/{slug}/600/600"


def img(seed: str) -> list:
    return [
        f"https://picsum.photos/seed/{seed}-1/600/600",
        f"https://picsum.photos/seed/{seed}-2/600/600",
        f"https://picsum.photos/seed/{seed}-3/600/600",
    ]


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


client = MongoClient(settings.mongo_uri)
db = client[settings.MONGODB_DB_NAME]

# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------
for coll in ["products", "brands", "categories", "users", "orders", "reviews", "carts"]:
    db[coll].drop()

# ---------------------------------------------------------------------------
# Demo user
# ---------------------------------------------------------------------------
demo_user = {
    "username": "demo",
    "name": "Demo User",
    "email": "demo@example.com",
    "password": hash_password("demo12345"),
    "is_active": True,
    "created_at": now(),
}
user_id = db.users.insert_one(demo_user).inserted_id

# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
categories = [
    {"name": "Smartphones", "slug": "smartphones", "description": "Mobile phones & accessories",
     "icon": "smartphone"},
    {"name": "Laptops", "slug": "laptops", "description": "Laptops & notebooks", "icon": "laptop"},
    {"name": "Televisions", "slug": "televisions", "description": "Smart TVs & displays", "icon": "tv"},
    {"name": "Headphones", "slug": "headphones", "description": "Headphones & earbuds", "icon": "headphones"},
]
cat_ids = {}
for c in categories:
    c["created_at"] = now()
    cat_ids[c["slug"]] = db.categories.insert_one(c).inserted_id

# ---------------------------------------------------------------------------
# Brands
# ---------------------------------------------------------------------------
brands = [
    {"name": "Apple", "slug": "apple", "country": "USA", "logo": "https://picsum.photos/seed/apple-logo/120/60"},
    {"name": "Samsung", "slug": "samsung", "country": "South Korea", "logo": "https://picsum.photos/seed/samsung-logo/120/60"},
    {"name": "OnePlus", "slug": "oneplus", "country": "China", "logo": "https://picsum.photos/seed/oneplus-logo/120/60"},
    {"name": "Dell", "slug": "dell", "country": "USA", "logo": "https://picsum.photos/seed/dell-logo/120/60"},
    {"name": "ASUS", "slug": "asus", "country": "Taiwan", "logo": "https://picsum.photos/seed/asus-logo/120/60"},
    {"name": "Sony", "slug": "sony", "country": "Japan", "logo": "https://picsum.photos/seed/sony-logo/120/60"},
    {"name": "LG", "slug": "lg", "country": "South Korea", "logo": "https://picsum.photos/seed/lg-logo/120/60"},
    {"name": "Bose", "slug": "bose", "country": "USA", "logo": "https://picsum.photos/seed/bose-logo/120/60"},
]
brand_ids = {}
for b in brands:
    b["created_at"] = now()
    brand_ids[b["slug"]] = db.brands.insert_one(b).inserted_id


def review(rating: int, comment: str, age_days: int, username: str = "demo") -> dict:
    return {
        "user_id": str(user_id),
        "username": username,
        "rating": rating,
        "comment": comment,
        "created_at": days_ago(age_days),
    }


# ---------------------------------------------------------------------------
# Products (12)
# ---------------------------------------------------------------------------
products = [
    {
        "name": "Samsung Galaxy S24", "slug": "samsung-galaxy-s24",
        "brand": {"_id": brand_ids["samsung"], "name": "Samsung", "slug": "samsung"},
        "category": {"_id": cat_ids["smartphones"], "name": "Smartphones", "slug": "smartphones"},
        "description": "Compact flagship with a 6.2-inch Dynamic AMOLED 2X display, Snapdragon 8 Gen 3 and Galaxy AI features.",
        "price": 79999, "discount_price": 62999, "stock": 15,
        "specifications": [
            {"key": "Display", "value": "6.2-inch Dynamic AMOLED 2X, 120Hz"},
            {"key": "Processor", "value": "Snapdragon 8 Gen 3"},
            {"key": "RAM", "value": "8 GB"},
            {"key": "Storage", "value": "256 GB"},
            {"key": "Battery", "value": "4000 mAh"},
        ],
        "reviews": [
            review(5, "Excellent camera and battery life.", 12),
            review(4, "Great phone, slightly pricey.", 30, "alex"),
        ],
        "price_history": [
            {"old_price": 79999, "new_price": 62999, "changed_at": days_ago(20)},
        ],
        "is_featured": True,
    },
    {
        "name": "Apple iPhone 15 Pro", "slug": "apple-iphone-15-pro",
        "brand": {"_id": brand_ids["apple"], "name": "Apple", "slug": "apple"},
        "category": {"_id": cat_ids["smartphones"], "name": "Smartphones", "slug": "smartphones"},
        "description": "Titanium build, A17 Pro chip and a customizable Action button. USB-C finally arrives on iPhone.",
        "price": 134900, "discount_price": 124900, "stock": 8,
        "specifications": [
            {"key": "Display", "value": "6.1-inch Super Retina XDR"},
            {"key": "Processor", "value": "A17 Pro"},
            {"key": "RAM", "value": "8 GB"},
            {"key": "Storage", "value": "256 GB"},
            {"key": "Camera", "value": "48MP Main + 12MP Ultra Wide"},
        ],
        "reviews": [review(5, "Buttery smooth and the camera is stunning.", 10)],
        "price_history": [{"old_price": 134900, "new_price": 124900, "changed_at": days_ago(15)}],
        "is_featured": True,
    },
    {
        "name": "OnePlus 12", "slug": "oneplus-12",
        "brand": {"_id": brand_ids["oneplus"], "name": "OnePlus", "slug": "oneplus"},
        "category": {"_id": cat_ids["smartphones"], "name": "Smartphones", "slug": "smartphones"},
        "description": "Flagship killer with Snapdragon 8 Gen 3 and 100W fast charging.",
        "price": 64999, "discount_price": None, "stock": 20,
        "specifications": [
            {"key": "Display", "value": "6.82-inch LTPO AMOLED, 120Hz"},
            {"key": "Processor", "value": "Snapdragon 8 Gen 3"},
            {"key": "RAM", "value": "12 GB"},
            {"key": "Storage", "value": "256 GB"},
            {"key": "Charging", "value": "100W SUPERVOOC"},
        ],
        "reviews": [review(4, "Fast charging is unreal, great value.", 8)],
        "price_history": [],
        "is_featured": False,
    },
    {
        "name": "Apple MacBook Air M3", "slug": "apple-macbook-air-m3",
        "brand": {"_id": brand_ids["apple"], "name": "Apple", "slug": "apple"},
        "category": {"_id": cat_ids["laptops"], "name": "Laptops", "slug": "laptops"},
        "description": "Featherweight laptop with the M3 chip, 18-hour battery and a gorgeous Liquid Retina display.",
        "price": 114900, "discount_price": 104900, "stock": 10,
        "specifications": [
            {"key": "Display", "value": "13.6-inch Liquid Retina"},
            {"key": "Chip", "value": "Apple M3"},
            {"key": "RAM", "value": "8 GB Unified"},
            {"key": "Storage", "value": "256 GB SSD"},
            {"key": "Battery", "value": "Up to 18 hours"},
        ],
        "reviews": [
            review(5, "Silent, cool and all-day battery.", 18),
            review(5, "Perfect for students.", 40, "priya"),
        ],
        "price_history": [{"old_price": 114900, "new_price": 104900, "changed_at": days_ago(25)}],
        "is_featured": True,
    },
    {
        "name": "Dell XPS 13", "slug": "dell-xps-13",
        "brand": {"_id": brand_ids["dell"], "name": "Dell", "slug": "dell"},
        "category": {"_id": cat_ids["laptops"], "name": "Laptops", "slug": "laptops"},
        "description": "Premium ultrabook with an InfinityEdge display and Intel Core Ultra 7.",
        "price": 129990, "discount_price": 119990, "stock": 6,
        "specifications": [
            {"key": "Display", "value": "13.4-inch FHD+ InfinityEdge"},
            {"key": "Processor", "value": "Intel Core Ultra 7 155H"},
            {"key": "RAM", "value": "16 GB LPDDR5"},
            {"key": "Storage", "value": "512 GB SSD"},
        ],
        "reviews": [review(4, "Beautiful screen, gets a little warm.", 22)],
        "price_history": [],
        "is_featured": False,
    },
    {
        "name": "ASUS ROG Zephyrus G14", "slug": "asus-rog-zephyrus-g14",
        "brand": {"_id": brand_ids["asus"], "name": "ASUS", "slug": "asus"},
        "category": {"_id": cat_ids["laptops"], "name": "Laptops", "slug": "laptops"},
        "description": "Compact gaming powerhouse with Ryzen 9 and RTX 4070 graphics.",
        "price": 174990, "discount_price": 159990, "stock": 5,
        "specifications": [
            {"key": "Display", "value": "14-inch QHD+ OLED, 120Hz"},
            {"key": "Processor", "value": "AMD Ryzen 9 8945HS"},
            {"key": "Graphics", "value": "NVIDIA RTX 4070 8GB"},
            {"key": "RAM", "value": "16 GB"},
            {"key": "Storage", "value": "1 TB SSD"},
        ],
        "reviews": [review(5, "Best portable gaming laptop I've owned.", 14)],
        "price_history": [{"old_price": 174990, "new_price": 159990, "changed_at": days_ago(18)}],
        "is_featured": True,
    },
    {
        "name": "Sony Bravia XR X90L 55\"", "slug": "sony-bravia-xr-x90l-55",
        "brand": {"_id": brand_ids["sony"], "name": "Sony", "slug": "sony"},
        "category": {"_id": cat_ids["televisions"], "name": "Televisions", "slug": "televisions"},
        "description": "4K Full Array LED TV powered by the Cognitive Processor XR.",
        "price": 139990, "discount_price": 119990, "stock": 7,
        "specifications": [
            {"key": "Screen Size", "value": "55 inch"},
            {"key": "Resolution", "value": "4K UHD (3840 x 2160)"},
            {"key": "Panel", "value": "Full Array LED"},
            {"key": "Refresh Rate", "value": "120Hz"},
            {"key": "HDR", "value": "Dolby Vision, HDR10"},
        ],
        "reviews": [review(4, "Crisp picture and great upscaling.", 26)],
        "price_history": [{"old_price": 139990, "new_price": 119990, "changed_at": days_ago(12)}],
        "is_featured": False,
    },
    {
        "name": "LG OLED evo C4 65\"", "slug": "lg-oled-evo-c4-65",
        "brand": {"_id": brand_ids["lg"], "name": "LG", "slug": "lg"},
        "category": {"_id": cat_ids["televisions"], "name": "Televisions", "slug": "televisions"},
        "description": "Self-lit OLED evo panel with perfect blacks and 144Hz gaming support.",
        "price": 249990, "discount_price": 219990, "stock": 4,
        "specifications": [
            {"key": "Screen Size", "value": "65 inch"},
            {"key": "Resolution", "value": "4K UHD"},
            {"key": "Panel", "value": "OLED evo"},
            {"key": "Refresh Rate", "value": "144Hz"},
            {"key": "Gaming", "value": "G-Sync, FreeSync Premium"},
        ],
        "reviews": [review(5, "Incredible picture for movies and games.", 16)],
        "price_history": [{"old_price": 249990, "new_price": 219990, "changed_at": days_ago(9)}],
        "is_featured": True,
    },
    {
        "name": "Samsung Neo QLED 4K 55\"", "slug": "samsung-neo-qled-4k-55",
        "brand": {"_id": brand_ids["samsung"], "name": "Samsung", "slug": "samsung"},
        "category": {"_id": cat_ids["televisions"], "name": "Televisions", "slug": "televisions"},
        "description": "Quantum Mini LED TV with brilliant brightness and anti-glare coating.",
        "price": 159990, "discount_price": 139990, "stock": 9,
        "specifications": [
            {"key": "Screen Size", "value": "55 inch"},
            {"key": "Resolution", "value": "4K UHD"},
            {"key": "Panel", "value": "Neo QLED Mini LED"},
            {"key": "Refresh Rate", "value": "120Hz"},
        ],
        "reviews": [review(4, "Bright and vivid, great for sports.", 33)],
        "price_history": [],
        "is_featured": False,
    },
    {
        "name": "Sony WH-1000XM5", "slug": "sony-wh-1000xm5",
        "brand": {"_id": brand_ids["sony"], "name": "Sony", "slug": "sony"},
        "category": {"_id": cat_ids["headphones"], "name": "Headphones", "slug": "headphones"},
        "description": "Industry-leading noise cancelling over-ear headphones with 30-hour battery.",
        "price": 34990, "discount_price": 29990, "stock": 25,
        "specifications": [
            {"key": "Type", "value": "Over-ear, wireless"},
            {"key": "Noise Cancelling", "value": "Yes, auto NC optimizer"},
            {"key": "Battery", "value": "30 hours"},
            {"key": "Connectivity", "value": "Bluetooth 5.2, multipoint"},
        ],
        "reviews": [
            review(5, "Best noise cancellation on the market.", 6),
            review(4, "Comfortable for long flights.", 28, "sam"),
        ],
        "price_history": [{"old_price": 34990, "new_price": 29990, "changed_at": days_ago(10)}],
        "is_featured": True,
    },
    {
        "name": "Bose QuietComfort Ultra", "slug": "bose-quietcomfort-ultra",
        "brand": {"_id": brand_ids["bose"], "name": "Bose", "slug": "bose"},
        "category": {"_id": cat_ids["headphones"], "name": "Headphones", "slug": "headphones"},
        "description": "Immersive spatial audio with world-class noise cancellation.",
        "price": 39900, "discount_price": 35900, "stock": 18,
        "specifications": [
            {"key": "Type", "value": "Over-ear, wireless"},
            {"key": "Noise Cancelling", "value": "QuietComfort, CustomTune"},
            {"key": "Battery", "value": "24 hours"},
            {"key": "Audio", "value": "Bose Immersive Audio"},
        ],
        "reviews": [review(4, "Superb comfort and immersive mode.", 20)],
        "price_history": [],
        "is_featured": False,
    },
    {
        "name": "Apple AirPods Pro 2", "slug": "apple-airpods-pro-2",
        "brand": {"_id": brand_ids["apple"], "name": "Apple", "slug": "apple"},
        "category": {"_id": cat_ids["headphones"], "name": "Headphones", "slug": "headphones"},
        "description": "Active noise cancellation, Adaptive Audio and USB-C charging case.",
        "price": 24900, "discount_price": 21900, "stock": 30,
        "specifications": [
            {"key": "Type", "value": "In-ear, wireless"},
            {"key": "Noise Cancelling", "value": "Active Noise Cancellation"},
            {"key": "Battery", "value": "6 hours (30 with case)"},
            {"key": "Chip", "value": "Apple H2"},
        ],
        "reviews": [review(5, "Seamless with iPhone, great ANC.", 11)],
        "price_history": [{"old_price": 24900, "new_price": 21900, "changed_at": days_ago(7)}],
        "is_featured": True,
    },
]

for p in products:
    reviews = p.get("reviews", [])
    p["average_rating"] = round(sum(r["rating"] for r in reviews) / len(reviews), 2) if reviews else 0.0
    p["total_reviews"] = len(reviews)
    p["images"] = img(p["slug"])
    p["image"] = image_for(p["slug"])
    p["is_active"] = True
    p["created_at"] = now()
    p["updated_at"] = now()

db.products.insert_many(products)

# ---------------------------------------------------------------------------
# Indexes
# ---------------------------------------------------------------------------
db.products.create_index("slug", unique=True)
db.products.create_index("name")
db.products.create_index("brand._id")
db.products.create_index("category._id")
db.products.create_index("price")
db.products.create_index("is_active")
db.users.create_index("email", unique=True)
db.users.create_index("username", unique=True)
db.brands.create_index("slug", unique=True)
db.categories.create_index("slug", unique=True)

print("Seeded successfully")
print(
    "products:", db.products.count_documents({}),
    "categories:", db.categories.count_documents({}),
    "brands:", db.brands.count_documents({}),
    "users:", db.users.count_documents({}),
)
client.close()
