"""Comprehensive validation tests for FASE 2 - Plotly Charts Implementation."""

import json
from pathlib import Path
import re


class TestFase2Validation:
    """Validate FASE 2 implementation completeness."""

    def test_charts_js_exists_and_exports_initCharts(self):
        """Verify charts.js exists and exports initCharts function."""
        charts_file = Path("web/js/charts.js")
        assert charts_file.exists(), "web/js/charts.js does not exist"
        
        content = charts_file.read_text()
        assert "export async function initCharts" in content, "initCharts function not exported"
        assert "function createPriceChart" in content, "createPriceChart function missing"
        assert "function createValuationsChart" in content, "createValuationsChart function missing"
        assert "function createPerformanceChart" in content, "createPerformanceChart function missing"

    def test_report_html_includes_plotly_cdn(self):
        """Verify report.html includes Plotly CDN script."""
        report_file = Path("web/report.html")
        assert report_file.exists(), "web/report.html does not exist"
        
        content = report_file.read_text(encoding="utf-8")
        assert 'https://cdn.plot.ly/plotly-latest.min.js' in content, "Plotly CDN not found"

    def test_report_html_has_chart_containers(self):
        """Verify report.html has all three chart containers."""
        report_file = Path("web/report.html")
        content = report_file.read_text(encoding="utf-8")
        
        assert 'id="priceChart"' in content, "priceChart container not found"
        assert 'id="valuationChart"' in content, "valuationChart container not found"
        assert 'id="performanceChart"' in content, "performanceChart container not found"

    def test_css_has_charts_grid_styles(self):
        """Verify CSS includes charts-grid and chart-container styles."""
        css_file = Path("web/css/styles.css")
        assert css_file.exists(), "web/css/styles.css does not exist"
        
        content = css_file.read_text()
        assert ".charts-grid" in content, ".charts-grid class not found"
        assert ".chart-container" in content, ".chart-container class not found"
        assert "repeat(auto-fit, minmax(500px, 1fr))" in content, "Responsive grid template not found"

    def test_css_responsive_media_queries(self):
        """Verify CSS has responsive media queries for mobile."""
        css_file = Path("web/css/styles.css")
        content = css_file.read_text()
        
        assert "@media (max-width: 768px)" in content, "Mobile media query not found"
        assert "grid-template-columns: 1fr" in content, "Mobile single column layout not found"

    def test_report_js_imports_charts_module(self):
        """Verify report.js imports initCharts from charts.js."""
        report_js = Path("web/js/report.js")
        assert report_js.exists(), "web/js/report.js does not exist"
        
        content = report_js.read_text()
        assert "import { initCharts } from './charts.js'" in content, "Charts module import not found"

    def test_no_emojis_in_javascript(self):
        """Verify no emojis in JavaScript files."""
        js_files = list(Path("web/js").glob("*.js"))
        
        # Common emoji Unicode ranges
        emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\u2600-\u27BF]|[\u2B50]|[\u2714]|[\u2717]|[\u26A0]'
        
        for js_file in js_files:
            content = js_file.read_text()
            matches = re.findall(emoji_pattern, content)
            assert not matches, f"Emojis found in {js_file.name}: {matches}"

    def test_no_emojis_in_css(self):
        """Verify no emojis in CSS files."""
        css_files = list(Path("web/css").glob("*.css"))
        
        emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\u2600-\u27BF]|[\u2B50]|[\u2714]|[\u2717]|[\u26A0]'
        
        for css_file in css_files:
            content = css_file.read_text()
            matches = re.findall(emoji_pattern, content)
            assert not matches, f"Emojis found in {css_file.name}: {matches}"

    def test_metrics_json_structure_nvda(self):
        """Verify metrics.json has correct structure."""
        metrics_file = Path("evaluaciones/NVDA/raw-search/metrics.json")
        
        if metrics_file.exists():
            with open(metrics_file) as f:
                data = json.load(f)
            
            # Validate required fields
            assert "ticker" in data, "ticker field missing"
            assert "precios_historicos" in data, "precios_historicos field missing"
            assert "valuations" in data, "valuations field missing"
            assert "performance" in data, "performance field missing"
            assert "sector_comparison" in data, "sector_comparison field missing"
            
            # Validate nested structure
            assert "ultimos_12m" in data["precios_historicos"], "ultimos_12m field missing"
            assert isinstance(data["precios_historicos"]["ultimos_12m"], list), "ultimos_12m not a list"

    def test_api_endpoint_exists(self):
        """Verify API endpoint for charts data exists."""
        reports_file = Path("app/routes/reports.py")
        content = reports_file.read_text()
        
        assert "@router.get(\"/{ticker}/charts-data\")" in content, "charts-data endpoint not found"
        assert "get_charts_data" in content, "get_charts_data function not found"

    def test_charts_integration_tests_exist(self):
        """Verify test file exists."""
        test_file = Path("tests/test_charts_integration.py")
        assert test_file.exists(), "test_charts_integration.py does not exist"
        
        content = test_file.read_text()
        assert "TestMetricsDataStructure" in content, "TestMetricsDataStructure class not found"
        assert "TestChartsDataIntegration" in content, "TestChartsDataIntegration class not found"

    def test_no_javascript_syntax_errors(self):
        """Basic validation of JavaScript syntax (no nested strings check)."""
        charts_file = Path("web/js/charts.js")
        content = charts_file.read_text()
        
        # Check for balanced braces
        assert content.count('{') == content.count('}'), "Unbalanced braces in charts.js"
        assert content.count('[') == content.count(']'), "Unbalanced brackets in charts.js"
        assert content.count('(') == content.count(')'), "Unbalanced parentheses in charts.js"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
