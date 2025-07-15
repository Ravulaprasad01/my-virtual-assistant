// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getFormFields') {
        // Get all visible input fields
        const inputs = Array.from(document.querySelectorAll('input, textarea')).filter(el => el.offsetParent !== null);
        const fields = inputs.map(input => ({
            name: input.name,
            placeholder: input.placeholder,
            type: input.type,
            value: input.value
        }));
        sendResponse({ fields });
        return true;
    }
    if (request.action === 'autofill') {
        const inputs = Array.from(document.querySelectorAll('input, textarea')).filter(el => el.offsetParent !== null);
        request.values.forEach((val, idx) => {
            if (inputs[idx]) {
                inputs[idx].focus();
                inputs[idx].value = val;
                inputs[idx].dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
    }
});