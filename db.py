import os
import psycopg2
import pymongo

DB_TYPE = os.getenv("DB_TYPE", "postgres")

def save_campaign(data):
    if DB_TYPE == "postgres":
        conn = psycopg2.connect(os.getenv("POSTGRES_URL"))
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id SERIAL PRIMARY KEY,
                product TEXT,
                audience TEXT,
                ad_copy TEXT,
                email_campaign TEXT,
                social_posts TEXT,
                image_url TEXT,
                audio_url TEXT
            )
        """)
        cur.execute("""
            INSERT INTO campaigns (product, audience, ad_copy, email_campaign, social_posts, image_url, audio_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (data["product"], data["audience"], data["ad_copy"], data["email"], data["social"], data["image"], data["audio"]))
        conn.commit()
        cur.close()
        conn.close()

    elif DB_TYPE == "mongo":
        client = pymongo.MongoClient(os.getenv("MONGO_URL"))
        db = client["marketing_db"]
        campaigns = db["campaigns"]
        campaigns.insert_one(data)
