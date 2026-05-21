#!/usr/bin/env python3
"""
Test para consolidate_reports.py (skill final-report)

Verifica:
1. Validación de archivos existentes
2. Extracción correcta de datos del informe técnico
"""

import sys
import unittest
from pathlib import Path

# Agregar path al importar consolidate_reports
sys.path.insert(0, str(Path(__file__).parent.parent / '.github' / 'skills' / 'final-report' / 'scripts'))

from consolidate_reports import ReportConsolidator


class TestConsolidateReports(unittest.TestCase):
    """Tests para ReportConsolidator"""

    def test_validate_files_missing(self):
        """Test: Detecta archivos faltantes"""
        consolidator = ReportConsolidator('evaluaciones/TEST')
        result = consolidator.validate_files()
        self.assertFalse(result, "validate_files() debe retornar False cuando faltan archivos")

    def test_validate_files_exists(self):
        """Test: Detecta archivos existentes"""
        ticker_dir = Path('evaluaciones/NVDA')
        
        if ticker_dir.exists():
            consolidator = ReportConsolidator(str(ticker_dir))
            result = consolidator.validate_files()
            self.assertTrue(result, f"validate_files() debe retornar True para {ticker_dir}")
    
    def test_extract_technical_data(self):
        """Test: Extrae datos correctos del informe técnico"""
        ticker_dir = Path('evaluaciones/NVDA')
        
        if ticker_dir.exists():
            consolidator = ReportConsolidator(str(ticker_dir))
            data = consolidator.extract_from_technical()
            
            self.assertIn('ticker', data, "Debe extraer 'ticker'")
            self.assertEqual(data['ticker'].upper(), 'NVDA', f"Ticker debe ser NVDA, recibido: {data['ticker']}")
            self.assertIn('nombre_empresa', data, "Debe extraer 'nombre_empresa'")
            self.assertIn('sector', data, "Debe extraer 'sector'")
            self.assertIn('precio_actual', data, "Debe extraer 'precio_actual'")


if __name__ == '__main__':
    unittest.main()
