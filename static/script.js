function handleImagePreview(input, previewId) {
    const previewContainer = document.getElementById(previewId);
    if (!previewContainer) return;

    previewContainer.innerHTML = ''; // Clear existing
    const files = input.files;
    if (files.length > 3) {
        alert("You can only upload a maximum of 3 images.");
        input.value = '';
        return;
    }
    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = e => {
            const img = document.createElement("img");
            img.src = e.target.result;
            previewContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
    });
}

// Image preview handlers - add safety checks
document.addEventListener('DOMContentLoaded', function() {
    const vehicleImageInput = document.querySelector('#vehicle-images input');
    const registrationImageInput = document.querySelector('#registration-card input');

    if (vehicleImageInput) {
        vehicleImageInput.addEventListener('change', function () {
            handleImagePreview(this, 'vehicle-preview');
        });
    }

    if (registrationImageInput) {
        registrationImageInput.addEventListener('change', function () {
            handleImagePreview(this, 'card-preview');
        });
    }
});

function showEditForm(fleetId, section) {
    const displayElement = document.getElementById(section + '-info-display-' + fleetId);
    const formElement = document.getElementById(section + '-info-form-' + fleetId);

    if (displayElement && formElement) {
        displayElement.style.display = 'none';
        formElement.style.display = 'block';
    }
}

function filterFleet(button, type) {
    const rows = document.querySelectorAll("tbody tr");
    rows.forEach(row => {
        const vehicleType = row.getAttribute("data-type");
        row.style.display = (type === "All" || vehicleType === type) ? "" : "none";
    });
    const allButtons = document.querySelectorAll('.filter-btn');
    allButtons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
}

function confirmLogout() {
    if (confirm("Are you sure you want to logout?")) {
        const logoutLink = document.getElementById("logoutLink");
        if (logoutLink) {
            logoutLink.click();
        } else {
            // If no logout link, redirect to login page
            window.location.href = '/login';
        }
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) {
        sidebar.style.width = sidebar.style.width === "200px" ? "0" : "200px";
    }
}

// Close sidebar when clicking outside
document.addEventListener('click', function (e) {
    const sidebar = document.getElementById("sidebar");
    const toggle = document.getElementById("sidebarToggle");

    if (sidebar && toggle && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.style.width = "0";
    }
});

// Dashboard modal functionality
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
}

// Maintenance modal functionality
function viewMaintenanceDetails(data) {
    window.lastViewedMaintenance = data;

    // Populate modal fields safely
    const fields = [
        'maintenance_no', 'fleet_id', 'vehicle_name', 'vehicle_type',
        'maintenance_type', 'remarks', 'start_date', 'expected_end_date',
        'job_no', 'maintenance_status', 'odometer', 'region'
    ];

    fields.forEach(field => {
        const element = document.getElementById("detail_" + field);
        if (element) {
            element.innerText = data[field] || '';
        }
    });

    // Ensure view mode is shown and edit mode is hidden
    const viewMode = document.getElementById("view-mode");
    const editMode = document.getElementById("edit-mode");
    if (viewMode) viewMode.style.display = 'block';
    if (editMode) editMode.style.display = 'none';

    // Show the modal
    const viewModal = document.getElementById("viewModal");
    if (viewModal) {
        viewModal.style.display = "block";
        document.body.style.overflow = 'hidden';
    }
}

function showEditMode() {
    const data = window.lastViewedMaintenance;
    if (!data) return;

    // Hide view mode and show edit mode
    const viewMode = document.getElementById("view-mode");
    const editMode = document.getElementById("edit-mode");
    if (viewMode) viewMode.style.display = 'none';
    if (editMode) editMode.style.display = 'block';

    // Populate edit form fields
    const editFields = {
        'edit_maintenance_no': data.maintenance_no || '',
        'edit_fleet_id': data.fleet_id || '',
        'edit_vehicle_name': data.vehicle_name || '',
        'edit_vehicle_type': data.vehicle_type || '',
        'edit_job_no': data.job_no || '',
        'edit_region': data.region || ''
    };

    // Set text content for non-editable fields
    Object.keys(editFields).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerText = editFields[id];
        }
    });

    // Set form input values
    const formFields = {
        'edit_maintenance_type': data.maintenance_type,
        'edit_remarks': data.remarks,
        'edit_start_date': data.start_date,
        'edit_expected_end_date': data.expected_end_date,
        'edit_maintenance_status': data.maintenance_status,
        'edit_odometer': data.odometer
    };

    Object.keys(formFields).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.value = formFields[id] || '';
        }
    });

    // Set form action
    const form = document.getElementById("editMaintenanceForm");
    if (form && data._id) {
        form.action = `/edit_maintenance/${data._id}`;
    }
}

function cancelEdit() {
    // Hide edit mode and show view mode
    const viewMode = document.getElementById("view-mode");
    const editMode = document.getElementById("edit-mode");
    if (viewMode) viewMode.style.display = 'block';
    if (editMode) editMode.style.display = 'none';
}

function deleteMaintenance() {
    const data = window.lastViewedMaintenance;
    if (!data || !data._id) {
        alert("Error: No maintenance record selected");
        return;
    }

    if (confirm("Are you sure you want to delete this maintenance record? This action cannot be undone.")) {
        // Create a form and submit it
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/delete_maintenance/${data._id}`;
        document.body.appendChild(form);
        form.submit();
    }
}

function closeMaintenanceModal() {
    const viewModal = document.getElementById("viewModal");
    if (viewModal) {
        viewModal.style.display = "none";
        document.body.style.overflow = 'auto';
    }

    // Reset modal to view mode
    const viewMode = document.getElementById("view-mode");
    const editMode = document.getElementById("edit-mode");
    if (viewMode) viewMode.style.display = 'block';
    if (editMode) editMode.style.display = 'none';
}

function showAddMaintenanceModal() {
    const modal = document.getElementById("maintenanceModal");
    if (!modal) {
        console.error("Modal element with ID 'maintenanceModal' not found.");
        return;
    }

    // Clear any previously filled values
    const form = modal.querySelector("form");
    if (form) form.reset();

    // Clear read-only fields manually
    const vehicleName = document.getElementById("vehicleName");
    const vehicleType = document.getElementById("vehicleType");
    if (vehicleName) vehicleName.value = "";
    if (vehicleType) vehicleType.value = "";

    // Display the modal
    modal.style.display = "block";
    document.body.style.overflow = 'hidden';
}

function populateVehicleDetails() {
    const select = document.getElementById('fleetIdSelect');
    if (!select) return;

    const selected = select.options[select.selectedIndex];
    const name = selected.getAttribute('data-name') || '';
    const type = selected.getAttribute('data-type') || '';

    const vehicleName = document.getElementById('vehicleName');
    const vehicleType = document.getElementById('vehicleType');

    if (vehicleName) vehicleName.value = name;
    if (vehicleType) vehicleType.value = type;
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Dashboard fleet links
    document.querySelectorAll('.fleet-link').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href && href.startsWith('#modal-')) {
                const modalId = href.substring(1); // Remove the #
                openModal(modalId);
            }
        });
    });

    // Dashboard modal close buttons
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    });

    // Maintenance links
    document.querySelectorAll('.maintenance-link').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            try {
                const data = JSON.parse(this.dataset.maintenance);
                viewMaintenanceDetails(data);
            } catch (error) {
                console.error('Error parsing maintenance data:', error);
            }
        });
    });

    // Close maintenance modal
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            closeMaintenanceModal();
        });
    });

    // Close modals when clicking outside
    window.addEventListener('click', function (e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
            document.body.style.overflow = 'auto';

            // Reset maintenance modal to view mode if it's the maintenance modal
            if (e.target.id === 'viewModal') {
                const viewMode = document.getElementById("view-mode");
                const editMode = document.getElementById("edit-mode");
                if (viewMode) viewMode.style.display = 'block';
                if (editMode) editMode.style.display = 'none';
            }
        }
    });

    // Initialize filter buttons
    const firstFilterBtn = document.querySelector('.filter-btn');
    if (firstFilterBtn) {
        firstFilterBtn.classList.add('active');
    }

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// Global click handler for closing modals with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Close any open modals
        document.querySelectorAll('.modal').forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';

                // Reset maintenance modal to view mode
                if (modal.id === 'viewModal') {
                    const viewMode = document.getElementById("view-mode");
                    const editMode = document.getElementById("edit-mode");
                    if (viewMode) viewMode.style.display = 'block';
                    if (editMode) editMode.style.display = 'none';
                }
            }
        });
    }
});
