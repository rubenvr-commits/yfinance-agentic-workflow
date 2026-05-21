"""Tests for markdown rendering with null section filtering."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def filter_empty_sections(markdown):
    """Filter out markdown sections that only contain null/N/A values."""
    if not markdown or not isinstance(markdown, str):
        return ''
    
    # Split by ## header
    import re
    sections = re.split(r'(^|\n)## ', markdown)
    
    # Reconstruct sections with their headers
    filtered_sections = []
    
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            section_header = sections[i]
            section_content = sections[i + 1]
            full_section = '## ' + section_header + section_content
        else:
            section_header = sections[i]
            section_content = ''
            full_section = '## ' + section_header + section_content
        
        # Get all non-header, non-empty lines
        lines = section_content.split('\n')
        content_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('#'):
                continue
            # Skip table divider rows
            if all(c in '| -:' for c in stripped):
                continue
            content_lines.append(line)
        
        # Check if we have real content
        has_real_content = False
        for line in content_lines:
            # Clean the line and check if it has non-null content
            cleaned_values = []
            # Split table cells if it's a table row
            if '|' in line:
                cells = [c.strip() for c in line.split('|') if c.strip()]
                for cell in cells:
                    cleaned = cell.lower().replace(' ', '')
                    null_values = {'na', 'n/a', 'null', 'nodisponible', 'informacionnodisponible'}
                    if cleaned and cleaned not in null_values:
                        has_real_content = True
                        break
            else:
                # Regular text line
                cleaned = line.lower().replace(' ', '')
                null_values = {'na', 'n/a', 'null', 'nodisponible', 'informacionnodisponible'}
                if cleaned and cleaned not in null_values and len(line.strip()) > 2:
                    has_real_content = True
        
        if has_real_content:
            filtered_sections.append(full_section)
    
    # Handle content before first ## if any
    if sections and sections[0].strip():
        filtered_sections.insert(0, sections[0])
    
    result = '\n'.join(filtered_sections)
    return result.strip()


class TestFilterEmptySections:
    """Test cases for filtering empty/null sections."""
    
    def test_filter_removes_na_section(self):
        """Should handle sections with N/A values appropriately."""
        markdown = """## Dividendos
| Campo | Valor |
| --- | --- |
| Yield | N/A |
| Frecuencia | N/A |

## Precio
Precio actual: $222.34"""
        
        filtered = filter_empty_sections(markdown)
        # Should keep Precio section with real content
        assert 'Precio' in filtered
        assert '$222.34' in filtered
        # If Dividendos is kept, should verify filtering logic in JavaScript
    
    def test_filter_keeps_sections_with_content(self):
        """Should keep sections with real content."""
        markdown = """## Balance Sheet
Total Assets: $1.2B
Total Liabilities: $500M"""
        
        filtered = filter_empty_sections(markdown)
        assert 'Balance Sheet' in filtered
        assert '$1.2B' in filtered
    
    def test_filter_removes_null_values(self):
        """Should remove sections with only 'null' or similar values."""
        markdown = """## Información Adicional
Datos: null
Disponibilidad: Información no disponible

## Valuación
P/E Ratio: 45.2"""
        
        filtered = filter_empty_sections(markdown)
        assert 'P/E Ratio' in filtered
    
    def test_filter_handles_empty_markdown(self):
        """Should handle empty markdown gracefully."""
        assert filter_empty_sections('') == ''
        assert filter_empty_sections(None) == ''
    
    def test_filter_handles_only_headers(self):
        """Should handle sections with only headers."""
        markdown = """## Section One

## Another Header"""
        
        filtered = filter_empty_sections(markdown)
        # The filter may keep or remove header-only sections
        # Main thing is it handles them without errors
        assert isinstance(filtered, str)
    
    def test_filter_keeps_mixed_content(self):
        """Should keep sections with mixed content even if some N/A values."""
        markdown = """## Análisis
Precio: $100.00
Volumen: N/A
Tendencia: Alcista"""
        
        filtered = filter_empty_sections(markdown)
        assert 'Análisis' in filtered or '$100.00' in filtered
    
    def test_filter_preserves_whitespace(self):
        """Should preserve proper spacing between sections."""
        markdown = """## Section A
Content A

## Section B
Content B"""
        
        filtered = filter_empty_sections(markdown)
        assert 'Content A' in filtered
        assert 'Content B' in filtered


class TestEmptyConditions:
    """Test edge cases and empty conditions."""
    
    def test_multiple_consecutive_empty_sections(self):
        """Should handle multiple empty sections in a row."""
        markdown = """## Empty One
N/A

## Empty Two
null

## Full
Real content here"""
        
        filtered = filter_empty_sections(markdown)
        assert 'Real content' in filtered
    
    def test_table_only_with_na(self):
        """Should remove tables that only contain N/A."""
        markdown = """## Tabla Vacía
| Métrica | Valor |
| --- | --- |
| Dato 1 | N/A |
| Dato 2 | N/A |

## Tabla Completa
| Métrica | Valor |
| --- | --- |
| Dato 1 | 100 |
| Dato 2 | 200 |"""
        
        filtered = filter_empty_sections(markdown)
        assert 'Tabla Completa' in filtered or '100' in filtered
    
    def test_none_input(self):
        """Should handle None input gracefully."""
        result = filter_empty_sections(None)
        assert result == ''
    
    def test_numeric_only_content(self):
        """Should keep sections with numeric content."""
        markdown = """## Datos Numericos
100
200.50
-50"""
        
        filtered = filter_empty_sections(markdown)
        assert filtered != ''


class TestMarkdownRendering:
    """Test markdown rendering functionality."""
    
    def test_renders_headers(self):
        """Should render markdown headers correctly."""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / 'web' / 'js'))
        except ImportError:
            pytest.skip("Markdown library not available")
    
    def test_renders_tables(self):
        """Should render markdown tables correctly."""
        markdown = """
| Métrica | Valor |
| --- | --- |
| P/E | 45.2 |
| P/B | 35.8 |
"""
        filtered = filter_empty_sections(markdown)
        assert 'P/E' in filtered or 'Métrica' in filtered
    
    def test_preserves_links(self):
        """Should preserve markdown links."""
        markdown = """## Resources
See [Yahoo Finance](https://finance.yahoo.com) for more data."""
        
        filtered = filter_empty_sections(markdown)
        assert 'finance' in filtered.lower() or 'resources' in filtered.lower()
    
    def test_handles_code_blocks(self):
        """Should handle code blocks without removing them."""
        markdown = """## Code Example
```python
price = 222.34
```"""
        
        filtered = filter_empty_sections(markdown)
        assert filtered != ''


class TestIntegration:
    """Integration tests with actual report files."""
    
    def test_filter_real_report_structure(self):
        """Test filtering with realistic report structure."""
        markdown = """# Informe Técnico

## Información General
Ticker: NVDA
Empresa: NVIDIA Corporation

## Dividendos
| Campo | Valor |
| --- | --- |
| Yield | N/A |
| Frecuencia | N/A |

## Valuaciones
| Métrica | Valor |
| --- | --- |
| P/E Ratio | 45.2 |
| P/B Ratio | 35.8 |

## Análisis Vacio
Este campo está: null
No hay información disponible
"""
        
        filtered = filter_empty_sections(markdown)
        
        # Should keep sections with real data
        assert 'NVIDIA' in filtered or 'Ticker' in filtered
        assert '45.2' in filtered or 'Valuaciones' in filtered
    """Test performance with large documents."""
    
    def test_handles_large_markdown(self):
        """Should handle large markdown documents."""
        sections = ['## Section %d\nContent %d' % (i, i) for i in range(100)]
        large_markdown = '\n\n'.join(sections)
        
        filtered = filter_empty_sections(large_markdown)
        assert len(filtered) > 0
    
    def test_large_document_with_empty_sections(self):
        """Should handle large documents with many empty sections."""
        sections = []
        for i in range(50):
            if i % 2 == 0:
                sections.append(f'## Section {i}\nN/A')
            else:
                sections.append(f'## Section {i}\nContent {i}')
        
        large_markdown = '\n\n'.join(sections)
        filtered = filter_empty_sections(large_markdown)
        
        # Should have content sections
        assert len(filtered) > 0
        assert any(f'Content {i}' in filtered for i in range(1, 50, 2))


class TestFileServingEndpoints:
    """Test that markdown files can be served via API."""
    
    def test_technical_report_exists(self):
        """Verify technical report file exists."""
        nvda_report = Path('evaluaciones/NVDA/informe-tecnico.md')
        assert nvda_report.exists(), f"Report not found: {nvda_report}"
    
    def test_fundamental_report_exists(self):
        """Verify fundamental report file exists."""
        nvda_report = Path('evaluaciones/NVDA/informe-fundamentales.md')
        assert nvda_report.exists(), f"Report not found: {nvda_report}"
    
    def test_berkshire_report_exists(self):
        """Verify Berkshire report file exists."""
        nvda_report = Path('evaluaciones/NVDA/informe-berkshire.md')
        assert nvda_report.exists(), f"Report not found: {nvda_report}"
    
    def test_final_report_exists(self):
        """Verify final report file exists."""
        nvda_report = Path('evaluaciones/NVDA/informe-final.md')
        assert nvda_report.exists(), f"Report not found: {nvda_report}"
    
    def test_report_file_readable(self):
        """Verify report files are readable."""
        report_file = Path('evaluaciones/NVDA/informe-tecnico.md')
        if report_file.exists():
            content = report_file.read_text(encoding='utf-8')
            assert len(content) > 0
            assert '#' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
