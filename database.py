import sqlite3
import os
from datetime import datetime

DB_FILE = 'listings.db'

def get_db_connection():
    """Get a connection to the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables and sample data."""
    if not os.path.exists(DB_FILE):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create listings table
        cursor.execute('''
            CREATE TABLE listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                builder_name TEXT NOT NULL,
                price INTEGER NOT NULL,
                style_tags TEXT NOT NULL,
                image_path TEXT,
                difficulty TEXT DEFAULT 'Medium',
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create purchases table
        cursor.execute('''
            CREATE TABLE purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                buyer_name TEXT NOT NULL,
                discord_username TEXT,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
            )
        ''')

        # Insert sample listings
        sample_listings = [
            ('Modern Mansion', 'A sleek contemporary mansion with glass features and minimalist design. Perfect for roleplay!', 'BuilderPro', 5000, 'Modern,Contemporary', 'static/images/mansion1.jpg', 'Hard', 'Downtown'),
            ('Fantasy Castle', 'An epic medieval castle with towers, drawbridge, and secret passages. Rich in detail and atmosphere.', 'CastleKing', 7500, 'Fantasy,Medieval', 'static/images/castle1.jpg', 'Hard', 'Forest Hills'),
            ('Cozy Wood Cottage', 'A charming countryside cottage with gardens and a small farm. Great for starter homes!', 'HomeSweetHome', 2000, 'Cottage,Nature', 'static/images/cottage1.jpg', 'Easy', 'Village'),
            ('Futuristic Base', 'A sci-fi inspired structure with neon lights and advanced technology aesthetic.', 'TechBuilder', 5500, 'Futuristic,Tech', 'static/images/futuristic1.jpg', 'Medium', 'Tech District'),
            ('Underground Lair', 'A hidden underground base carved into a mountain with multiple levels and crafting stations.', 'DarkMiner', 3500, 'Underground,Base', 'static/images/lair1.jpg', 'Medium', 'Mountain Ridge'),
        ]

        for listing in sample_listings:
            cursor.execute('''
                INSERT INTO listings (title, description, builder_name, price, style_tags, image_path, difficulty, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', listing)

        conn.commit()
        conn.close()
        print(f"Database initialized at {DB_FILE}")

def add_listing(title, description, builder_name, price, style_tags, image_path, difficulty='Medium', location=''):
    """Add a new listing to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO listings (title, description, builder_name, price, style_tags, image_path, difficulty, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, builder_name, price, style_tags, image_path, difficulty, location))
    conn.commit()
    listing_id = cursor.lastrowid
    conn.close()
    return listing_id

def get_all_listings():
    """Get all listings from the database."""
    conn = get_db_connection()
    listings = conn.execute('SELECT * FROM listings ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(row) for row in listings]

def get_listing(listing_id):
    """Get a single listing by ID."""
    conn = get_db_connection()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    conn.close()
    return dict(listing) if listing else None

def delete_listing(listing_id):
    """Delete a listing by ID and all associated purchases."""
    conn = get_db_connection()
    # Get the listing to delete its image
    listing = conn.execute('SELECT image_path FROM listings WHERE id = ?', (listing_id,)).fetchone()

    # Delete purchases first (cascade will handle it, but explicit for clarity)
    conn.execute('DELETE FROM purchases WHERE listing_id = ?', (listing_id,))
    # Delete the listing
    conn.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
    conn.commit()
    conn.close()

    # Delete the image file if it exists
    if listing and listing['image_path'] and os.path.exists(listing['image_path']):
        try:
            os.remove(listing['image_path'])
        except:
            pass

    return True

def update_listing(listing_id, title, description, builder_name, price, style_tags, difficulty='Medium', location=''):
    """Update a listing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE listings
        SET title = ?, description = ?, builder_name = ?, price = ?, style_tags = ?, difficulty = ?, location = ?
        WHERE id = ?
    ''', (title, description, builder_name, price, style_tags, difficulty, location, listing_id))
    conn.commit()
    conn.close()
    return True

def add_purchase(listing_id, buyer_name, discord_username=None):
    """Record a house purchase."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO purchases (listing_id, buyer_name, discord_username)
        VALUES (?, ?, ?)
    ''', (listing_id, buyer_name, discord_username))
    conn.commit()
    purchase_id = cursor.lastrowid
    conn.close()
    return purchase_id

def get_purchases(listing_id):
    """Get all purchases for a listing."""
    conn = get_db_connection()
    purchases = conn.execute('SELECT * FROM purchases WHERE listing_id = ? ORDER BY purchase_date DESC', (listing_id,)).fetchall()
    conn.close()
    return [dict(row) for row in purchases]
