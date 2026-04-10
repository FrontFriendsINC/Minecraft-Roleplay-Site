// Load all listings for admin management
async function loadAdminListings() {
    try {
        const response = await fetch('/admin/api/listings');
        const listings = await response.json();
        displayAdminListings(listings);
    } catch (error) {
        console.error('Error loading listings:', error);
        showMessage('Error loading listings', 'error', 'addListingMessage');
    }
}

// Display listings in admin table
function displayAdminListings(listings) {
    const table = document.getElementById('listingsTable');

    if (listings.length === 0) {
        table.innerHTML = '<p style="text-align: center; color: #777; padding: 30px;">No listings yet. Create your first listing!</p>';
        return;
    }

    let tableHtml = `
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Builder</th>
                    <th>Price (💎)</th>
                    <th>Location</th>
                    <th>Difficulty</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    listings.forEach(listing => {
        tableHtml += `
            <tr>
                <td>${listing.title}</td>
                <td>${listing.builder_name}</td>
                <td>💎 ${listing.price.toLocaleString()}</td>
                <td>${listing.location || '—'}</td>
                <td>${listing.difficulty}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-edit" onclick="openEditModal(${listing.id})">Edit</button>
                        <button class="btn-delete" onclick="confirmDelete(${listing.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `;
    });

    tableHtml += `
            </tbody>
        </table>
    `;

    table.innerHTML = tableHtml;
}

// Add new listing
async function addListing(e) {
    e.preventDefault();

    const formData = new FormData(document.getElementById('addListingForm'));

    try {
        const response = await fetch('/api/listings/create', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            showMessage('Listing added successfully!', 'success', 'addListingMessage');
            document.getElementById('addListingForm').reset();
            document.getElementById('imagePreview').innerHTML = '';
            loadAdminListings();
        } else {
            const error = await response.json();
            showMessage(error.error || 'Error creating listing', 'error', 'addListingMessage');
        }
    } catch (error) {
        console.error('Error adding listing:', error);
        showMessage('Error creating listing', 'error', 'addListingMessage');
    }
}

// Open edit modal
async function openEditModal(listingId) {
    try {
        const response = await fetch(`/api/listings/${listingId}`);
        const listing = await response.json();

        document.getElementById('editListingId').value = listing.id;
        document.getElementById('editTitle').value = listing.title;
        document.getElementById('editBuilder').value = listing.builder_name;
        document.getElementById('editDescription').value = listing.description;
        document.getElementById('editPrice').value = listing.price;
        document.getElementById('editDifficulty').value = listing.difficulty;
        document.getElementById('editStyleTags').value = listing.style_tags;
        document.getElementById('editLocation').value = listing.location || '';

        const modal = document.getElementById('editModal');
        modal.classList.add('active');
    } catch (error) {
        console.error('Error loading listing:', error);
    }
}

// Close edit modal
function closeEditModal() {
    const modal = document.getElementById('editModal');
    modal.classList.remove('active');
}

// Save listing changes
async function saveListing(e) {
    e.preventDefault();

    const listingId = document.getElementById('editListingId').value;
    const formData = new FormData(document.getElementById('editListingForm'));

    try {
        const response = await fetch(`/api/listings/${listingId}/update`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            showMessage('Listing updated successfully!', 'success', 'addListingMessage');
            closeEditModal();
            loadAdminListings();
        } else {
            const error = await response.json();
            showMessage(error.error || 'Error updating listing', 'error', 'addListingMessage');
        }
    } catch (error) {
        console.error('Error updating listing:', error);
        showMessage('Error updating listing', 'error', 'addListingMessage');
    }
}

// Confirm and delete listing
async function confirmDelete(listingId) {
    if (confirm('Are you sure you want to delete this listing?')) {
        try {
            const response = await fetch(`/api/listings/${listingId}/delete`, {
                method: 'POST'
            });

            if (response.ok) {
                showMessage('Listing deleted successfully!', 'success', 'addListingMessage');
                loadAdminListings();
            } else {
                showMessage('Error deleting listing', 'error', 'addListingMessage');
            }
        } catch (error) {
            console.error('Error deleting listing:', error);
            showMessage('Error deleting listing', 'error', 'addListingMessage');
        }
    }
}

// Show message (success or error)
function showMessage(message, type, elementId) {
    const messageElement = document.getElementById(elementId);
    messageElement.textContent = message;
    messageElement.className = `message ${type}`;

    setTimeout(() => {
        messageElement.textContent = '';
        messageElement.className = 'message';
    }, 5000);
}

// Preview image before upload
function previewImage() {
    const file = document.getElementById('image').files[0];
    const preview = document.getElementById('imagePreview');

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const editModal = document.getElementById('editModal');
    if (event.target == editModal) {
        closeEditModal();
    }
};
