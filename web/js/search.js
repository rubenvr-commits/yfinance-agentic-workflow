// Search page JavaScript

const tickerInput = document.getElementById('tickerInput');
const searchBtn = document.getElementById('searchBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// Validate ticker format
function validateTicker(ticker) {
    const pattern = /^[A-Z0-9.]{1,6}$/;
    return pattern.test(ticker.toUpperCase());
}

// Handle search
async function handleSearch() {
    const ticker = tickerInput.value.trim().toUpperCase();
    
    if (!ticker) {
        showError('Por favor, ingrese un ticker');
        return;
    }
    
    if (!validateTicker(ticker)) {
        showError('Formato de ticker inválido. Use símbolos como NVDA, AAPL, o REP.MC');
        return;
    }
    
    showLoading(true, 'Buscando informe...');
    
    try {
        // Check if report exists
        const response = await fetch(`/api/reports/${ticker}/status`);
        
        if (response.ok) {
            const status = await response.json();
            
            if (status.exists) {
                showLoading(false);
                // Redirect to report page
                window.location.href = `/report.html?ticker=${ticker}`;
            } else {
                showLoading(false);
                handleReportNotFound(ticker);
            }
        } else {
            showLoading(false);
            showError('Error al consultar el servidor');
        }
    } catch (error) {
        showLoading(false);
        console.error('Error:', error);
        showError('Error de conexión. Verifique su conexión a internet.');
    }
}

// Handle report not found
async function handleReportNotFound(ticker) {
    const result = await showConfirmation(
        `No se encontró informe para ${ticker}. ¿Desea generarlo ahora?`
    );
    
    if (result) {
        generateReport(ticker);
    }
}

// Generate new report
async function generateReport(ticker) {
    showLoading(true, 'Iniciando generación de informe...');
    
    try {
        const response = await fetch(`/api/reports/${ticker}/generate`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();

            // Accept several server-side status tokens as start of generation
            const acceptedStartStatuses = ['started', 'in_progress', 'metrics_generated', 'awaiting_reports'];
            if (acceptedStartStatuses.includes(result.status)) {
                showLoading(true, 'Generando reportes...\nEsta operación puede tomar varios minutos.');

                // Start polling for progress
                pollGenerationProgress(ticker);
            } else {
                showLoading(false);
                showError('Error iniciando la generación');
            }
        } else {
            showLoading(false);
            showError('Error al contactar el servidor de generación');
        }
    } catch (error) {
        showLoading(false);
        console.error('Error:', error);
        showError('Error de conexión');
    }
}

// Poll for generation progress
async function pollGenerationProgress(ticker) {
    const maxAttempts = 120; // 2 minutes with 1 second interval
    let attempts = 0;
    
    const pollInterval = setInterval(async () => {
        attempts++;
        
        if (attempts > maxAttempts) {
            clearInterval(pollInterval);
            showLoading(false);
            showError('La generación está tomando más tiempo de lo esperado. Intente más tarde.');
            return;
        }
        
        try {
            const response = await fetch(`/api/reports/${ticker}/generate/progress`);
            
            if (response.ok) {
                const progress = await response.json();
                
                let message = `Generando: ${progress.current_phase || 'procesando'}\nProgreso: ${progress.progress_percent}%`;
                document.getElementById('loadingMessage').textContent = message;
                
                // Check if complete
                const checkResponse = await fetch(`/api/reports/${ticker}/status`);
                if (checkResponse.ok) {
                    const status = await checkResponse.json();
                    if (status.exists) {
                        clearInterval(pollInterval);
                        showLoading(false);
                        window.location.href = `/report.html?ticker=${ticker}`;
                        return;
                    }
                }
            }
        } catch (error) {
            console.error('Error checking progress:', error);
        }
    }, 1000);
}

// Show loading indicator
function showLoading(show, message = 'Cargando...') {
    loadingIndicator.style.display = show ? 'flex' : 'none';
    if (show && message) {
        document.getElementById('loadingMessage').textContent = message;
    }
}

// Show error message
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 6000);
}

// Show confirmation dialog
function showConfirmation(message) {
    return new Promise(resolve => {
        const confirmed = confirm(message);
        resolve(confirmed);
    });
}

// Event listeners
searchBtn.addEventListener('click', handleSearch);
tickerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

// Focus on input on page load
tickerInput.focus();
