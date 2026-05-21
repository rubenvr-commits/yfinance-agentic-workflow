// Charts Module - Plotly.js Integration
// Renders interactive financial charts from metrics data

/**
 * Initialize and render all three charts
 * @param {Object} metrics - The metrics data object from API
 */
export async function initCharts(metrics) {
    try {
        if (!metrics) {
            console.warn('No metrics data available for charts');
            showChartError('No se disponibiliza datos para los gráficos');
            return;
        }

        // Render each chart
        createPriceChart(metrics);
        createValuationsChart(metrics);
        createPerformanceChart(metrics);

        // Add responsive resize listener
        window.addEventListener('resize', () => {
            Plotly.Plots.resize('priceChart');
            Plotly.Plots.resize('valuationChart');
            Plotly.Plots.resize('performanceChart');
        });

    } catch (error) {
        console.error('Charts initialization error:', error);
        showChartError('Error al cargar los gráficos');
    }
}

/**
 * Create Price Historical Chart (Line Chart)
 * @param {Object} metrics - Metrics data containing price history
 */
function createPriceChart(metrics) {
    const container = document.getElementById('priceChart');
    if (!container) return;

    try {
        // Validate and extract price data
        if (!metrics.precios_historicos || !metrics.precios_historicos.ultimos_12m) {
            container.innerHTML = '<p class="chart-error">Datos de precios no disponibles</p>';
            return;
        }

        const priceData = metrics.precios_historicos.ultimos_12m;
        const dates = priceData.map(p => p.date);
        const closes = priceData.map(p => p.close);

        // Create trace for price line
        const trace = {
            x: dates,
            y: closes,
            type: 'scatter',
            mode: 'lines',
            name: 'Precio de Cierre',
            line: {
                color: '#035AA6',
                width: 2
            },
            fill: 'tozeroy',
            fillcolor: 'rgba(3, 90, 166, 0.1)',
            hovertemplate: '<b>%{x}</b><br>$%{y:.2f}<extra></extra>'
        };

        // Configure layout
        const layout = {
            title: 'Precio Histórico (12 meses)',
            xaxis: {
                title: 'Fecha',
                showgrid: true,
                gridcolor: '#E8E8E8'
            },
            yaxis: {
                title: 'Precio (USD)',
                showgrid: true,
                gridcolor: '#E8E8E8'
            },
            hovermode: 'x unified',
            plot_bgcolor: '#FAFAFA',
            paper_bgcolor: '#FFFFFF',
            margin: { l: 40, r: 20, t: 40, b: 40 },
            font: { family: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto' },
            autosize: true,
            height: 440
        };

        // Configure responsive config
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d']
        };

        Plotly.newPlot('priceChart', [trace], layout, config);

    } catch (error) {
        console.error('Error creating price chart:', error);
        container.innerHTML = '<p class="chart-error">Error al renderizar gráfico de precios</p>';
    }
}

/**
 * Create Valuations Comparison Chart (Horizontal Bar Chart)
 * @param {Object} metrics - Metrics data containing valuations
 */
function createValuationsChart(metrics) {
    const container = document.getElementById('valuationChart');
    if (!container) return;

    try {
        // Validate data
        const valuations = metrics.valuations || {};
        const sectorComp = metrics.sector_comparison || {};

        // Extract metrics
        const peRatio = valuations.pe_ratio;
        const pbRatio = valuations.pb_ratio;
        const psRatio = valuations.ps_ratio;
        const priceToFcf = valuations.price_to_fcf;

        // Extract sector comparisons
        const peSector = sectorComp.pe_sector;
        const peSp500 = sectorComp.pe_sp500;
        const pbSector = sectorComp.pb_sector;
        const pbSp500 = sectorComp.pb_sp500;
        const psSector = sectorComp.ps_sector;
        const psSp500 = sectorComp.ps_sp500;

        // Create traces for each metric
        const tickerTrace = {
            y: ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'Price to FCF'],
            x: [peRatio, pbRatio, psRatio, priceToFcf],
            type: 'bar',
            orientation: 'h',
            name: 'Ticker',
            marker: { color: '#049DD9' },
            text: [
                peRatio?.toFixed(2),
                pbRatio?.toFixed(2),
                psRatio?.toFixed(2),
                priceToFcf?.toFixed(2)
            ],
            textposition: 'auto',
            hovertemplate: '<b>%{y}</b><br>%{x:.2f}<extra></extra>'
        };

        const sectorTrace = {
            y: ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'Price to FCF'],
            x: [peSector, pbSector, psSector, null],
            type: 'bar',
            orientation: 'h',
            name: 'Sector',
            marker: { color: '#04B2D9' },
            text: [
                peSector?.toFixed(2),
                pbSector?.toFixed(2),
                psSector?.toFixed(2),
                ''
            ],
            textposition: 'auto',
            hovertemplate: '<b>%{y}</b><br>%{x:.2f}<extra></extra>'
        };

        const sp500Trace = {
            y: ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'Price to FCF'],
            x: [peSp500, pbSp500, psSp500, null],
            type: 'bar',
            orientation: 'h',
            name: 'S&P 500',
            marker: { color: '#F2C438' },
            text: [
                peSp500?.toFixed(2),
                pbSp500?.toFixed(2),
                psSp500?.toFixed(2),
                ''
            ],
            textposition: 'auto',
            hovertemplate: '<b>%{y}</b><br>%{x:.2f}<extra></extra>'
        };

        // Configure layout
        const layout = {
            title: 'Comparación de Valuaciones',
            xaxis: {
                title: 'Múltiplo',
                showgrid: true,
                gridcolor: '#E8E8E8'
            },
            yaxis: {
                title: '',
                showgrid: false
            },
            barmode: 'group',
            hovermode: 'y unified',
            plot_bgcolor: '#FAFAFA',
            paper_bgcolor: '#FFFFFF',
            margin: { l: 50, r: 20, t: 40, b: 40 },
            font: { family: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto' },
            legend: {
                orientation: 'v',
                x: 1.02,
                y: 1,
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                bordercolor: '#E0E0E0',
                borderwidth: 1
            },
            autosize: true,
            height: 460
        };

        // Configure responsive config
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d']
        };

        Plotly.newPlot('valuationChart', [tickerTrace, sectorTrace, sp500Trace], layout, config);

    } catch (error) {
        console.error('Error creating valuations chart:', error);
        container.innerHTML = '<p class="chart-error">Error al renderizar gráfico de valuaciones</p>';
    }
}

/**
 * Create Performance Metrics Chart (Grouped Bar Chart)
 * @param {Object} metrics - Metrics data containing performance indicators
 */
function createPerformanceChart(metrics) {
    const container = document.getElementById('performanceChart');
    if (!container) return;

    try {
        // Validate data
        const performance = metrics.performance || {};

        // Extract metrics
        const roe = performance.roe;
        const roa = performance.roa;
        const fcf = performance.fcf_billions;
        const dividendYield = performance.dividend_yield;

        // Format values with appropriate units
        const roeValue = roe ? (roe * 100).toFixed(2) : null;
        const roaValue = roa ? (roa * 100).toFixed(2) : null;
        const fcfValue = fcf ? fcf.toFixed(2) : null;
        const dividendValue = dividendYield ? (dividendYield * 100).toFixed(2) : null;

        // Create trace for performance metrics
        const trace = {
            x: ['ROE', 'ROA', 'FCF', 'Dividend Yield'],
            y: [roeValue, roaValue, fcfValue, dividendValue],
            type: 'bar',
            marker: {
                color: [
                    '#035AA6',
                    '#049DD9',
                    '#04B2D9',
                    '#F2C438'
                ]
            },
            text: [
                roeValue !== null ? `${roeValue}%` : '-',
                roaValue !== null ? `${roaValue}%` : '-',
                fcfValue !== null ? `$${fcfValue}B` : '-',
                dividendValue !== null ? `${dividendValue}%` : '-'
            ],
            textposition: 'auto',
            hovertemplate: '<b>%{x}</b><br>%{text}<extra></extra>'
        };

        // Configure layout
        const layout = {
            title: 'Métricas de Desempeño',
            xaxis: {
                title: 'Métrica',
                showgrid: false
            },
            yaxis: {
                title: 'Valor',
                showgrid: true,
                gridcolor: '#E8E8E8'
            },
            hovermode: 'x unified',
            plot_bgcolor: '#FAFAFA',
            paper_bgcolor: '#FFFFFF',
            margin: { l: 40, r: 20, t: 40, b: 40 },
            font: { family: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto' },
            autosize: true,
            height: 460
        };

        // Configure responsive config
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d']
        };

        Plotly.newPlot('performanceChart', [trace], layout, config);

    } catch (error) {
        console.error('Error creating performance chart:', error);
        container.innerHTML = '<p class="chart-error">Error al renderizar gráfico de desempeño</p>';
    }
}

/**
 * Display error message when charts fail to load
 * @param {string} message - Error message to display
 */
function showChartError(message) {
    const chartsSection = document.getElementById('chartsSection');
    if (chartsSection) {
        chartsSection.innerHTML = `
            <div class="error-message" style="grid-column: 1 / -1;">
                <p>${message}</p>
            </div>
        `;
    }
}
