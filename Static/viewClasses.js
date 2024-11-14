document.addEventListener('DOMContentLoaded', function() {
    var addClassBtn = document.getElementById('addClassBtn');
    var classForm = document.getElementById('classForm');
    var cancelBtn = document.getElementById('cancelBtn');
    var editFormContainer = document.getElementById('editFormContainer');
    var cancelEditBtn = document.getElementById('cancelEditBtn');

    if (addClassBtn && classForm && cancelBtn) {
        addClassBtn.addEventListener('click', function() {
            classForm.style.display = 'block';
        });

        cancelBtn.addEventListener('click', function() {
            classForm.style.display = 'none';
        });
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', function() {
            editFormContainer.style.display = 'none';
        });
    }
});

// Function to display a confirmation prompt before deleting a class
function confirmDelete() {
    return confirm('Are you sure you want to delete this class?');
}

// Function to display a confirmation prompt before editing a class
function confirmEdit() {
    return confirm('Are you sure you want to edit this class?');
}

// Function to show the edit form and populate it with the class data
function editClass(id, title, description, date, time) {
    document.getElementById('editClassId').value = id;
    document.getElementById('editTitle').value = title;
    document.getElementById('editDescription').value = description;
    document.getElementById('editDate').value = date;
    document.getElementById('editTime').value = time;
    document.getElementById('editDuration').value = duration;
    document.getElementById('editForm').action = '/update_class/' + id;
    document.getElementById('editFormContainer').style.display = 'block';
}


function showSummary() {
    alert("Total Classes: " + document.querySelectorAll("#classTable tbody tr").length);
}

function showTotalHours() {
    let totalHours = 0;
    document.querySelectorAll("#classTable tbody tr").forEach(row => {
    totalHours += parseInt(row.children[5].textContent);
    });
    alert("Total Class Hours: " + totalHours);
}
    