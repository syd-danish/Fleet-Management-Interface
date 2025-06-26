function handleImagePreview(input, previewId) {
    const previewContainer = document.getElementById(previewId);
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

    document.querySelector('#vehicle-images input').addEventListener('change', function () {
    handleImagePreview(this, 'vehicle-preview');
  });
    document.querySelector('#registration-card input').addEventListener('change', function () {
    handleImagePreview(this, 'card-preview');
  });
    function showEditForm(fleetId, section) {
  document.getElementById(section + '-info-display-' + fleetId).style.display = 'none';
  document.getElementById(section + '-info-form-' + fleetId).style.display = 'block';
}
function filterFleet(button, type) {
  const rows = document.querySelectorAll("tbody tr");
  rows.forEach(row => {
    const vehicleType = row.getAttribute("data-type");
    row.style.display = (type === "All" || vehicleType === type) ? "" : "none";
  });
  const allButtons = document.querySelectorAll('.filter-btn');
  allButtons.forEach(btn => btn.classList.remove('active'));
  button.classList.add('active');}