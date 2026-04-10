from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from dotenv import load_dotenv
from database import init_db, get_all_listings, get_listing, add_listing, delete_listing, update_listing, add_purchase, get_purchases
from werkzeug.utils import secure_filename
import requests
import json
import threading

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'blockmarket_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'static/images/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ADMIN_PASSWORD = 'admin123'  # Change this in production!
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize database on startup
init_db()

def send_discord_notification(discord_username, property_title, price):
    """Send a Discord notification via webhook."""
    if not DISCORD_WEBHOOK_URL:
        print("Warning: DISCORD_WEBHOOK_URL not set. Skipping Discord notification.")
        return False

    try:
        # Create a nice embed message
        embed = {
            "title": "🏠 New Property Purchase!",
            "description": f"A new buyer is interested in **{property_title}**",
            "color": 0x4CAF50,
            "fields": [
                {
                    "name": "Discord Buyer",
                    "value": discord_username,
                    "inline": True
                },
                {
                    "name": "Property Price",
                    "value": f"💎 {price:,} Diamonds",
                    "inline": True
                },
                {
                    "name": "Next Steps",
                    "value": "Contact the buyer to arrange payment and delivery.",
                    "inline": False
                }
            ]
        }

        payload = {
            "embeds": [embed],
            "content": f"@here New purchase inquiry for {property_title}!"
        }

        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code in [200, 204]:
            print(f"Discord notification sent for {discord_username}")
            return True
        else:
            print(f"Discord webhook error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Error sending Discord notification: {e}")
        return False

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the homepage/marketplace."""
    return render_template('index.html')

@app.route('/api/listings')
def api_listings():
    """Get all listings with optional filtering."""
    listings = get_all_listings()

    # Client-side filtering parameters
    min_price = request.args.get('minPrice', type=int, default=0)
    max_price = request.args.get('maxPrice', type=int, default=100000)
    style = request.args.get('style', '').lower()
    difficulty = request.args.get('difficulty', '').lower()
    search = request.args.get('search', '').lower()

    # Filter listings
    filtered = []
    for listing in listings:
        # Price filter
        if listing['price'] < min_price or listing['price'] > max_price:
            continue

        # Style filter
        if style and style not in listing['style_tags'].lower():
            continue

        # Difficulty filter
        if difficulty and difficulty not in listing['difficulty'].lower():
            continue

        # Search filter
        if search and search not in listing['title'].lower() and search not in listing['description'].lower():
            continue

        filtered.append(listing)

    return jsonify(filtered)

@app.route('/api/listings/<int:listing_id>')
def api_listing(listing_id):
    """Get a single listing by ID."""
    listing = get_listing(listing_id)
    if listing:
        return jsonify(listing)
    return jsonify({'error': 'Listing not found'}), 404

@app.route('/admin')
def admin():
    """Serve the admin panel (password protected)."""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and login handler."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logout from admin panel."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/api/listings/create', methods=['POST'])
def create_listing():
    """Create a new listing (admin only)."""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.form
    file = request.files.get('image')

    # Validate required fields
    if not data.get('title') or not data.get('description') or not data.get('builder_name') or not data.get('price'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Handle image upload
    image_path = None
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid overwrites
        import time
        filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_path = filepath

    try:
        listing_id = add_listing(
            title=data.get('title'),
            description=data.get('description'),
            builder_name=data.get('builder_name'),
            price=int(data.get('price', 0)),
            style_tags=data.get('style_tags', ''),
            image_path=image_path,
            difficulty=data.get('difficulty', 'Medium'),
            location=data.get('location', '')
        )
        return jsonify({'success': True, 'id': listing_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/listings/<int:listing_id>/update', methods=['POST'])
def update_listing_route(listing_id):
    """Update a listing (admin only)."""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.form
    file = request.files.get('image')

    # Get current listing
    listing = get_listing(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    # Handle new image upload
    image_path = listing['image_path']
    if file and file.filename != '' and allowed_file(file.filename):
        # Delete old image
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass

        # Save new image
        filename = secure_filename(file.filename)
        import time
        filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_path = filepath

    try:
        update_listing(
            listing_id=listing_id,
            title=data.get('title', listing['title']),
            description=data.get('description', listing['description']),
            builder_name=data.get('builder_name', listing['builder_name']),
            price=int(data.get('price', listing['price'])),
            style_tags=data.get('style_tags', listing['style_tags']),
            difficulty=data.get('difficulty', listing['difficulty']),
            location=data.get('location', '')
        )
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/listings/<int:listing_id>/delete', methods=['POST', 'DELETE'])
def delete_listing_route(listing_id):
    """Delete a listing (admin only)."""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if delete_listing(listing_id):
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Failed to delete listing'}), 400

@app.route('/api/listings/<int:listing_id>/purchase', methods=['POST'])
def purchase_listing(listing_id):
    """Purchase a house listing."""
    data = request.get_json()
    buyer_name = data.get('buyer_name', '').strip()
    discord_username = data.get('discord_username', '').strip()

    if not buyer_name:
        return jsonify({'error': 'Minecraft username is required'}), 400

    if not discord_username:
        return jsonify({'error': 'Discord username is required'}), 400

    listing = get_listing(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    try:
        purchase_id = add_purchase(listing_id, buyer_name, discord_username)

        # Send Discord notification in a background thread (non-blocking)
        if DISCORD_WEBHOOK_URL:
            threading.Thread(
                target=send_discord_notification,
                args=(discord_username, listing['title'], listing['price']),
                daemon=True
            ).start()

        return jsonify({
            'success': True,
            'purchase_id': purchase_id,
            'message': f'House purchased by {buyer_name}! Seller notified on Discord.'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/listings/<int:listing_id>/purchases', methods=['GET'])
def listing_purchases(listing_id):
    """Get all purchases for a listing."""
    purchases = get_purchases(listing_id)
    return jsonify(purchases)

@app.route('/admin/api/listings')
def admin_api_listings():
    """Get all listings for admin panel."""
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    listings = get_all_listings()
    return jsonify(listings)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
