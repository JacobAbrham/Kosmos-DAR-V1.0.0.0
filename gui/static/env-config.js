// Environment Configuration Functions for KOSMOS Web Setup

async function showEnvModal() {
    // Load environment variables
    const response = await fetch('/api/env-variables');
    const variables = await response.json();
    
    const container = document.getElementById('env-vars-container');
    container.innerHTML = '';
    
    variables.forEach(varConfig => {
        const group = document.createElement('div');
        group.className = 'env-var-group';
        
        const badge = varConfig.required ? 
            '<span class="required-badge">REQUIRED</span>' : 
            '<span class="optional-badge">OPTIONAL</span>';
        
        const inputType = varConfig.name.includes('PASSWORD') || 
                          varConfig.name.includes('KEY') || 
                          varConfig.name.includes('TOKEN') ? 'password' : 'text';
        
        group.innerHTML = `
            <div class="env-var-label">
                <strong>${varConfig.name}</strong>
                ${badge}
            </div>
            <div class="env-var-description">${varConfig.description}</div>
            <input 
                type="${inputType}" 
                class="env-var-input" 
                data-var-name="${varConfig.name}"
                value="${varConfig.current || ''}"
                placeholder="${varConfig.default || 'Enter value...'}"
                ${varConfig.required ? 'required' : ''}
            >
        `;
        
        container.appendChild(group);
    });
    
    // Show modal
    document.getElementById('env-modal').classList.add('active');
}

function closeEnvModal() {
    document.getElementById('env-modal').classList.remove('active');
}

async function loadExistingEnv() {
    // Reload variables (will include existing values)
    const response = await fetch('/api/env-variables');
    const variables = await response.json();
    
    // Update inputs
    variables.forEach(varConfig => {
        const input = document.querySelector(`[data-var-name="${varConfig.name}"]`);
        if (input && varConfig.current) {
            input.value = varConfig.current;
        }
    });
    
    updateStatus('success', 'Loaded existing .env configuration');
}

async function saveAndContinue() {
    // Collect all values
    const inputs = document.querySelectorAll('.env-var-input');
    const variables = {};
    let hasError = false;
    
    inputs.forEach(input => {
        const varName = input.dataset.varName;
        const value = input.value.trim();
        
        // Check required fields
        if (input.required && !value) {
            input.style.borderColor = '#dc3545';
            hasError = true;
        } else {
            input.style.borderColor = '#ddd';
            variables[varName] = value;
        }
    });
    
    if (hasError) {
        alert('Please fill in all required fields (marked in red).');
        return;
    }
    
    // Save to .env file
    try {
        const response = await fetch('/api/save-env', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({variables})
        });
        
        const result = await response.json();
        
        if (result.success) {
            closeEnvModal();
            updateStatus('success', 'Environment variables saved');
            
            // Now proceed with setup
            proceedWithSetup();
        } else {
            alert('Failed to save environment variables: ' + result.error);
        }
    } catch (error) {
        alert('Error saving environment variables: ' + error.message);
    }
}

async function proceedWithSetup() {
    // Confirm
    if (!confirm(`Start setup for ${selectedEnvironment.name}?\n\nThis may take ${selectedEnvironment.setup_time}.`)) {
        return;
    }
    
    // Update UI
    document.getElementById('start-btn').disabled = true;
    document.getElementById('spinner').classList.add('active');
    document.getElementById('output-panel').classList.add('active');
    updateStatus('running', 'Setup running...');
    
    // Start setup
    const response = await fetch('/api/start-setup', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({environment_id: selectedEnvironment.id})
    });
    
    const data = await response.json();
    
    if (!socket) {
        initializeSocket();
    }
}

// Modified startSetup to show env modal first
async function startSetup() {
    if (!selectedEnvironment) return;
    
    // Show environment configuration modal first
    await showEnvModal();
}
