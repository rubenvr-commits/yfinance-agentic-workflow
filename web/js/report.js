// Report page JavaScript

// Import charts module
import { initCharts } from './charts.js';
import { renderMarkdown, filterEmptySections } from './markdown-renderer.js';

const md = window.markdownit({
    html: true,
    linkify: true,
    typographer: true
});

let currentTicker = '';

// Get ticker from URL parameters
function getTicker() {
    const params = new URLSearchParams(window.location.search);
    return params.get('ticker');
}

// Initialize page
async function initializePage() {
    currentTicker = getTicker();
    
    if (!currentTicker) {
        showError('No se especificó un ticker. Redirigiéndolo a la página de inicio...');
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
        return;
    }
    
    document.getElementById('tickerTitle').textContent = currentTicker;
    
    showLoading(true);
    
    try {
        await loadReport();
    } catch (error) {
        console.error('Error:', error);
        showError('Error al cargar el informe');
    }
}

// Load report data
async function loadReport() {
    try {
        const response = await fetch(`/api/reports/${currentTicker}`);
        
        if (response.ok) {
            const data = await response.json();
            displayReport(data);
            loadChartData(data.metrics);
        } else {
            showError('No se encontró el informe. Por favor, intente de nuevo.');
        }
    } catch (error) {
        console.error('Error loading report:', error);
        showError('Error al cargar el informe del servidor');
    } finally {
        showLoading(false);
    }
}

// Display report content
function displayReport(data) {
    // Update metadata
    if (data.generated_date) {
        document.getElementById('generatedDate').textContent = 
            `Actualizado: ${formatDate(data.generated_date)}`;
        
        const nextReview = addDays(parseDate(data.generated_date), 30);
        document.getElementById('nextReview').textContent = 
            `Próxima revisión: ${formatDate(nextReview)}`;
    }
    
    // Render markdown content with filtering for empty sections
    if (data.content) {
        const filtered = filterEmptySections(data.content);
        const htmlContent = md.render(filtered);
        document.getElementById('reportContent').innerHTML = htmlContent;
        document.getElementById('contentSection').style.display = 'block';
    }
    
    // Show detailed reports section
    document.getElementById('detailedReportsSection').style.display = 'block';
    setupDetailedReportsLinks();
}

// Load chart data and initialize Plotly charts
async function loadChartData(metrics) {
    if (metrics) {
        document.getElementById('chartsSection').style.display = 'block';
        
        try {
            // Initialize Plotly charts with metrics data
            await initCharts(metrics);
            console.log('Charts initialized successfully');
        } catch (error) {
            console.error('Error initializing charts:', error);
            // Show error message but don't break the page
            const chartsSection = document.getElementById('chartsSection');
            if (chartsSection) {
                chartsSection.innerHTML = '<div class="error-message">Error al cargar los gráficos</div>';
            }
        }
    }
}

// Setup detailed reports links
function setupDetailedReportsLinks() {
    const modal = document.getElementById('detailModal');
    const closeModal = document.querySelector('.close-modal');
    
    // Technical report
    document.getElementById('technicalLink').addEventListener('click', (e) => {
        e.preventDefault();
        loadDetailedReport('informe-tecnico');
    });
    
    // Fundamental report
    document.getElementById('fundamentalLink').addEventListener('click', (e) => {
        e.preventDefault();
        loadDetailedReport('informe-fundamentales');
    });
    
    // Berkshire report
    document.getElementById('berkshireLink').addEventListener('click', (e) => {
        e.preventDefault();
        loadDetailedReport('informe-berkshire');
    });
    
    // Close modal
    closeModal.addEventListener('click', () => {
        modal.classList.remove('show');
    });
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });
}

// Load detailed report in modal
async function loadDetailedReport(reportType) {
    const modal = document.getElementById('detailModal');
    const modalBody = document.getElementById('modalBody');
    
    showLoading(true);
    
    try {
        // Try API endpoint first (Phase 3)
        const response = await fetch(`/api/reports/${currentTicker}/${reportType}.md`);
        
        if (response.ok) {
            const markdown = await response.text();
            const filtered = filterEmptySections(markdown);
            const html = renderMarkdown(markdown);
            modalBody.innerHTML = html;
            modal.classList.add('show');
        } else {
            // Fallback to file path (Phase 1/2)
            const fileResponse = await fetch(`/detailed-reports/${currentTicker}/${reportType}.md`);
            if (fileResponse.ok) {
                const markdown = await fileResponse.text();
                const filtered = filterEmptySections(markdown);
                const html = md.render(filtered);
                modalBody.innerHTML = html;
                modal.classList.add('show');
            } else {
                showError(`No se encontró el informe ${reportType}`);
            }
        }
    } catch (error) {
        console.error(`Error loading ${reportType}:`, error);
        showError(`Error al cargar el informe ${reportType}`);
    } finally {
        showLoading(false);
    }
}

// Download CSV
document.getElementById('downloadBtn').addEventListener('click', async () => {
    try {
        const response = await fetch(`/api/reports/${currentTicker}/precios.csv`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentTicker}_precios.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            alert('No hay datos de precios disponibles');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al descargar los precios');
    }
});

// Utility functions
function showLoading(show) {
    document.getElementById('loadingIndicator').style.display = show ? 'flex' : 'none';
}

function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    document.getElementById('errorText').textContent = message;
    errorEl.style.display = 'flex';
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    } catch {
        return dateString;
    }
}

function parseDate(dateString) {
    return new Date(dateString);
}

function addDays(date, days) {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializePage);
