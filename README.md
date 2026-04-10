#  BlockMarket - Minecraft House Marketplace

A modern, beautiful marketplace for buying and selling stunning Minecraft houses! Built with Python Flask backend and an elegant HTML/CSS frontend with a Minecraft-inspired dark theme.

## ✨ Features

- **Beautiful Marketplace**: Browse Minecraft houses with a modern, responsive design
- **Advanced Filtering**: Filter by price range, building style, and difficulty level
- **Search Functionality**: Quickly find houses by name or description
- **Admin Panel**: Password-protected admin interface to manage listings
- **Easy Listing Management**: Add, edit, and delete house listings with images
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Minecraft Theme**: Stylish dark theme with green accents inspired by Minecraft

## 🛠️ Tech Stack

- **Backend**: Python Flask 2.3.2
- **Database**: SQLite3 (built-in, no setup needed)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Total Dependencies**: 2 packages (Flask, Werkzeug)

## 📦 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Discord Bot Token

1. Create a `.env` file in the project root (copy from `.env.example`)
2. Add your Discord bot token:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```
3. **Get your token:**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Go to "Bot" → "Add Bot"
   - Under TOKEN, click "Copy" to copy your bot token
   - Paste it in the `.env` file
4. **Important:** Never share your bot token publicly or commit `.env` to git!

### 3. Run the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

## 🎮 Usage

### Marketplace Home Page
1. Open `http://localhost:5000` in your browser
2. Browse all available Minecraft house listings
3. Use filters to find houses by:
   - **Price Range**: Set min and max price
   - **Building Style**: Modern, Fantasy, Medieval, Futuristic, etc.
   - **Difficulty Level**: Easy, Medium, Hard
4. Click on any listing to see full details and download links
5. Use the search bar to quickly find houses

### Admin Panel

#### Login
1. Click "Admin Panel" in the navigation bar
2. Enter the admin password: `admin123`
3. You'll be redirected to the admin dashboard

#### Add a New Listing
1. Fill in the listing details:
   - **Title**: Name of the house
   - **Builder Name**: Your name
   - **Description**: Detailed description of the house
   - **Price**: Price in USD
   - **Difficulty**: Easy/Medium/Hard
   - **Style Tags**: Comma-separated tags (Modern, Fantasy, etc.)
   - **Download Link**: URL to download the world file
   - **Image**: Upload a screenshot of the house
2. Click "Add Listing"

#### Edit a Listing
1. Find the listing in the "Manage Listings" table
2. Click the "Edit" button
3. Update any fields and save changes

#### Delete a Listing
1. Find the listing in the "Manage Listings" table
2. Click the "Delete" button
3. Confirm the deletion

## 🔑 Admin Password

Default admin password: `admin123`

**IMPORTANT**: Change this password in `app.py` (line 17) before deploying to production!

```python
ADMIN_PASSWORD = 'your_secure_password_here'
```

## 📁 Project Structure

```
BlockMarket/
├── app.py                      # Flask application & routes
├── database.py                 # Database setup & helpers
├── listings.db                 # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
├── static/
│   ├── css/
│   │   └── styles.css         # All CSS styling
│   ├── js/
│   │   ├── script.js          # Marketplace functionality
│   │   └── admin.js           # Admin panel functionality
│   └── images/
│       └── uploads/           # Uploaded listing images
└── templates/
    ├── index.html             # Marketplace home page
    ├── login.html             # Admin login page
    └── admin.html             # Admin panel
```

## 🎨 Customization

### Change Admin Password
Edit `app.py` line 17:
```python
ADMIN_PASSWORD = 'your_new_password'
```

### Customize Colors
Edit `static/css/styles.css` to modify the color scheme. Key colors:
- `--primary-color: #4CAF50` (Green)
- `--secondary-color: #FF9800` (Orange)
- `--dark-bg: #1a1a1a` (Dark background)

### Add Sample Images
Place image files in `static/images/` and reference them in the image_path field when creating listings.

## 🚀 Deployment

### For Production:

1. **Change the admin password** to something secure
2. **Set Flask debug mode to False** in `app.py` (line 37):
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```
3. **Use a production server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 app:app
   ```
4. **Set up HTTPS** with a reverse proxy like Nginx
5. **Back up your database** regularly (listings.db)

## 📝 License

This project is open source and available for personal and commercial use.

## 🎯 Future Features (Ideas)

- User accounts and authentication
- Ratings and reviews system
- Favorites/wishlist feature
- Image gallery with multiple images per listing
- Built-in world creator integration
- Payment processing
- Category-based filtering
- Advanced search with full-text search
- Email notifications for new listings
- Social sharing features

## 🐛 Troubleshooting

### Port 5000 already in use
Change the port in `app.py` line 37:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Images not showing
Make sure uploaded images are in the correct directory:
`static/images/uploads/`

### Admin login not working
Check the password in `app.py` line 17 matches what you're entering.

### Database errors
Delete `listings.db` and restart the server to reinitialize the database.

---

**Enjoy your Minecraft marketplace! 🎮✨**
