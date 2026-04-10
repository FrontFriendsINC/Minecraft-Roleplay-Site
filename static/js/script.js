// Fetch and load all listings
async function loadListings() {
    try {
        const response = await fetch('/api/listings');
        const listings = await response.json();
        displayListings(listings);
    } catch (error) {
        console.error('Error loading listings:', error);
    }
}

// Display listings in the grid
function displayListings(listings) {
    const grid = document.getElementById('listingsGrid');
    grid.innerHTML = '';

    if (listings.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #777; padding: 40px;">No listings found. Try adjusting your filters!</p>';
        return;
    }

    listings.forEach(listing => {
        const card = document.createElement('div');
        card.className = 'listing-card';
        card.onclick = () => openListing(listing.id);

        const imageHtml = listing.image_path
            ? `<img src="${listing.image_path}" alt="${listing.title}">`
            : '';

        const tags = listing.style_tags.split(',').map(tag => tag.trim()).slice(0, 3);
        const tagsHtml = tags.map(tag => `<span class="tag">${tag}</span>`).join('');

        const difficultyStars = {
            'Easy': '⭐',
            'Medium': '⭐⭐',
            'Hard': '⭐⭐⭐'
        };

        const difficulty = difficultyStars[listing.difficulty] || listing.difficulty;

        card.innerHTML = `
            <div class="listing-image ${!imageHtml ? 'no-image' : ''}">
                ${imageHtml}
                <div class="listing-overlay">
                    <span class="listing-difficulty">${difficulty}</span>
                </div>
            </div>
            <div class="listing-content">
                <h3 class="listing-title">${listing.title}</h3>
                <p class="listing-builder">by ${listing.builder_name}</p>
                ${listing.location ? `<p class="listing-location">📍 ${listing.location}</p>` : ''}
                <div class="listing-tags">${tagsHtml}</div>
                <div class="listing-price">
                    💎 ${listing.price.toLocaleString()}
                </div>
            </div>
        `;

        grid.appendChild(card);
    });
}

// Open listing detail modal
async function openListing(listingId) {
    try {
        const response = await fetch(`/api/listings/${listingId}`);
        const listing = await response.json();

        const modal = document.getElementById('listingModal');
        const body = document.getElementById('modalBody');

        const imageHtml = listing.image_path
            ? `<img src="${listing.image_path}" alt="${listing.title}">`
            : '<div style="width: 100%; height: 300px; background: #2d2d2d; display: flex; align-items: center; justify-content: center; font-size: 64px; border-radius: 4px;">🏠</div>';

        const difficultyEmoji = {
            'Easy': '⭐',
            'Medium': '⭐⭐',
            'Hard': '⭐⭐⭐'
        };

        const difficulty = difficultyEmoji[listing.difficulty] || listing.difficulty;

        body.innerHTML = `
            <h2>${listing.title}</h2>
            ${imageHtml}
            <div class="listing-info">
                <p><strong>Builder:</strong> ${listing.builder_name}</p>
                <p><strong>Price:</strong> 💎 ${listing.price.toLocaleString()} Diamonds</p>
                <p><strong>Difficulty:</strong> ${difficulty}</p>
                <p><strong>Style:</strong> ${listing.style_tags}</p>
                ${listing.location ? `<p><strong>Location:</strong> 📍 ${listing.location}</p>` : ''}
            </div>
            <h3 style="color: #4CAF50; margin-top: 20px;">Description</h3>
            <p>${listing.description}</p>
            <div class="purchase-section">
                <label style="color: #b0b0b0; font-size: 13px; margin-bottom: 5px;">Minecraft Username</label>
                <input type="text" id="buyerName" placeholder="Enter your Minecraft name..." class="purchase-input" maxlength="16">
                <label style="color: #b0b0b0; font-size: 13px; margin-bottom: 5px; margin-top: 10px;">Discord Username</label>
                <input type="text" id="discordUsername" placeholder="Enter your Discord username..." class="purchase-input">
                <button onclick="purchaseHouse(${listing.id})" class="btn btn-primary btn-large">Purchase House</button>
            </div>
        `;

        modal.classList.add('active');
    } catch (error) {
        console.error('Error loading listing:', error);
    }
}

// Purchase a house
async function purchaseHouse(listingId) {
    const buyerName = document.getElementById('buyerName').value.trim();
    const discordUsername = document.getElementById('discordUsername').value.trim();

    if (!buyerName) {
        alert('Please enter your Minecraft name!');
        return;
    }

    if (!discordUsername) {
        alert('Please enter your Discord username!');
        return;
    }

    try {
        const response = await fetch(`/api/listings/${listingId}/purchase`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                buyer_name: buyerName,
                discord_username: discordUsername
            })
        });

        if (response.ok) {
            const data = await response.json();
            alert(`🎉 Congratulations! ${data.message}`);
            closeModal();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.error || 'Purchase failed'));
        }
    } catch (error) {
        console.error('Error purchasing house:', error);
        alert('Error processing purchase');
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('listingModal');
    modal.classList.remove('active');
}

// Apply filters
function applyFilters() {
    const minPrice = parseInt(document.getElementById('minPrice').value) || 0;
    const maxPrice = parseInt(document.getElementById('maxPrice').value) || 100000;
    const style = document.getElementById('styleFilter').value;
    const difficulty = document.getElementById('difficultyFilter').value;

    fetchFilteredListings(minPrice, maxPrice, style, difficulty);
}

// Fetch filtered listings
async function fetchFilteredListings(minPrice, maxPrice, style, difficulty) {
    try {
        const params = new URLSearchParams();
        params.append('minPrice', minPrice);
        params.append('maxPrice', maxPrice);
        if (style) params.append('style', style);
        if (difficulty) params.append('difficulty', difficulty);

        const response = await fetch(`/api/listings?${params}`);
        const listings = await response.json();
        displayListings(listings);
    } catch (error) {
        console.error('Error fetching listings:', error);
    }
}

// Search listings
function searchListings() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();

    if (!searchTerm) {
        loadListings();
        return;
    }

    const params = new URLSearchParams();
    params.append('search', searchTerm);

    fetch(`/api/listings?${params}`)
        .then(response => response.json())
        .then(listings => displayListings(listings))
        .catch(error => console.error('Error searching:', error));
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('listingModal');
    if (event.target == modal) {
        modal.classList.remove('active');
    }
};
