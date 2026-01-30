document.addEventListener('DOMContentLoaded', () => {
    loadContent();
    checkAdminMode();
});

async function loadContent() {
    try {
        const response = await fetch('/api/content');
        if (!response.ok) return; // Fail silently
        const content = await response.json();

        document.querySelectorAll('[data-content-key]').forEach(el => {
            const key = el.getAttribute('data-content-key');
            if (content[key]) {
                // Determine if we should use innerText (safer) or innerHTML (if formatting needed)
                // For now, innerText to prevent XSS, but allow newlines
                el.innerText = content[key];
            }
        });
    } catch (err) {
        console.error('CMS Load Error:', err);
    }
}

function checkAdminMode() {
    const token = localStorage.getItem('authToken');
    if (token) {
        enableEditMode(token);
    }
}

function enableEditMode(token) {
    // Inject CSS for edit buttons
    const style = document.createElement('style');
    style.innerHTML = `
        .cms-editable-wrapper { position: relative; display: inline-block; width: 100%; transition: outline 0.2s; }
        .cms-editable-wrapper:hover { outline: 2px dashed #d4894a; cursor: default; }
        .cms-edit-btn {
            position: absolute; top: -10px; right: -10px;
            background: #d4894a; color: white; border: none;
            border-radius: 50%; width: 24px; height: 24px;
            cursor: pointer; font-size: 14px; display: none;
            z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            align-items: center; justify-content: center;
        }
        .cms-editable-wrapper:hover .cms-edit-btn { display: flex; }
        
        /* Modal */
        .cms-modal {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 2000;
            display: flex; justify-content: center; align-items: center;
        }
        .cms-modal-content {
            background: white; padding: 20px; border-radius: 8px;
            width: 90%; max-width: 500px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .cms-modal textarea {
            width: 100%; height: 150px; margin: 10px 0; padding: 8px;
            border: 1px solid #ddd; border-radius: 4px; font-family: inherit;
        }
        .cms-modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
        .cms-btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        .cms-btn-save { background: #28a745; color: white; }
        .cms-btn-cancel { background: #dc3545; color: white; }
    `;
    document.head.appendChild(style);

    document.querySelectorAll('[data-content-key]').forEach(el => {
        // Wrap element to position button
        // Note: Simple wrapping might break complex layouts (flex/grid parents).
        // Alternative: Append button to body and position absolute relative to element,
        // but wrapper is usually safer for simple text blocks.
        // Let's try appending button strictly inside logic without breaking layout?
        // Actually, wrapper is best for hover effect.

        const key = el.getAttribute('data-content-key');

        // Skip if already wrapped (idempotency)
        if (el.parentNode.classList.contains('cms-editable-wrapper')) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'cms-editable-wrapper';

        // This is tricky: replacing el with wrapper can break CSS selectors targeting el.
        // Better strategy: Add class to el directly and append button as sibling if position allows, 
        // or just absolute position the button relative to el if el is relative.

        el.style.position = 'relative';
        el.classList.add('cms-editable-wrapper'); // Re-using class for hover style on the element itself

        const btn = document.createElement('button');
        btn.className = 'cms-edit-btn';
        btn.innerHTML = '✎';
        btn.title = 'Inhalt bearbeiten';
        btn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            openEditModal(key, el.innerText);
        };

        el.appendChild(btn);
    });
}

function openEditModal(key, currentText) {
    const modal = document.createElement('div');
    modal.className = 'cms-modal';
    modal.innerHTML = `
        <div class="cms-modal-content">
            <h3>Inhalt bearbeiten</h3>
            <textarea id="cms-editor">${currentText}</textarea>
            <div class="cms-modal-actions">
                <button class="cms-btn cms-btn-cancel" onclick="closeCmsModal()">Abbrechen</button>
                <button class="cms-btn cms-btn-save" onclick="saveCmsContent('${key}')">Speichern</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function closeCmsModal() {
    document.querySelector('.cms-modal').remove();
}

async function saveCmsContent(key) {
    const newValue = document.getElementById('cms-editor').value;
    const token = localStorage.getItem('authToken');

    try {
        const response = await fetch(`/api/admin/content/${key}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ value: newValue })
        });

        if (response.ok) {
            // Update DOM immediately
            const el = document.querySelector(`[data-content-key="${key}"]`);
            if (el) {
                // Preserve the button!
                const btn = el.querySelector('.cms-edit-btn');
                el.innerText = newValue;
                if (btn) el.appendChild(btn); // Re-append button
            }
            closeCmsModal();
        } else {
            alert('Fehler beim Speichern');
        }
    } catch (err) {
        console.error(err);
        alert('Verbindungsfehler');
    }
}
