// Request form fields from the content script
function getFormFields() {
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'getFormFields' }, function(response) {
            if (response && response.fields) {
                renderFields(response.fields);
            }
        });
    });
}

function renderFields(fields) {
    const form = document.getElementById('fieldsForm');
    form.innerHTML = '';
    fields.forEach((field, idx) => {
        const row = document.createElement('div');
        row.className = 'field-row';
        const label = document.createElement('label');
        label.textContent = field.name || field.placeholder || field.type || `Field ${idx+1}`;
        const input = document.createElement('input');
        input.type = 'text';
        input.name = field.name;
        input.placeholder = field.placeholder || '';
        input.value = field.value || '';
        row.appendChild(label);
        row.appendChild(input);
        form.appendChild(row);
    });
}

document.getElementById('autofillBtn').addEventListener('click', function() {
    const form = document.getElementById('fieldsForm');
    const inputs = form.querySelectorAll('input');
    const values = Array.from(inputs).map(input => input.value);
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'autofill', values: values });
    });
});

document.addEventListener('DOMContentLoaded', getFormFields);