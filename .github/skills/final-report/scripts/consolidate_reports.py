#!/usr/bin/env python3
"""
consolidate_reports.py - Consolida 3 informes en un informe final ejecutivo
Uso: python consolidate_reports.py <path_a_directorio_ticker>
Ejemplo: python consolidate_reports.py evaluaciones/NVDA
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ReportConsolidator:
    def __init__(self, ticker_dir: str):
        self.ticker_dir = Path(ticker_dir)
        self.ticker = self.ticker_dir.name.upper()
        self.technical_file = self.ticker_dir / "informe-tecnico.md"
        self.fundamental_file = self.ticker_dir / "informe-fundamentales.md"
        self.berkshire_file = self.ticker_dir / "informe-berkshire.md"
        self.output_file = self.ticker_dir / "informe-final.md"
        self.data = {}

    def validate_files(self) -> bool:
        """Verifica que existan los 3 informes."""
        missing = []
        for file in [self.technical_file, self.fundamental_file, self.berkshire_file]:
            if not file.exists():
                missing.append(file.name)
        
        if missing:
            print(f"ERROR: Faltan archivos en {self.ticker_dir}:")
            for f in missing:
                print(f"  - {f}")
            return False
        return True

    def extract_from_technical(self) -> Dict[str, Any]:
        """Extrae datos del informe técnico."""
        data = {}
        try:
            with open(self.technical_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Función auxiliar para extraer de tablas (manejo más robusto)
            def extract_from_table(content: str, field_name: str) -> Optional[str]:
                """Extrae un valor de una tabla markdown."""
                # Buscar en formato: | **Campo** | Valor |
                patterns = [
                    rf'\|\s*\*\*{re.escape(field_name)}\*\*\s*\|\s*([^|\n]+)',
                    rf'\|\s*{re.escape(field_name)}\s*\|\s*([^|\n]+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        value = match.group(1).strip()
                        return value if value and value != '---' else None
                return None
            
            # Identificación del activo
            data['ticker'] = extract_from_table(content, 'Ticker') or self.ticker
            data['nombre_empresa'] = extract_from_table(content, 'Nombre Completo') or "N/D"
            data['sector'] = extract_from_table(content, 'Sector') or "N/D"
            data['industria'] = extract_from_table(content, 'Industria') or "N/D"
            
            # Datos de precio
            precio = extract_from_table(content, 'Precio Actual')
            if precio:
                precio = precio.replace('$', '').strip()
            data['precio_actual'] = precio or "N/D"
            
            cambio = extract_from_table(content, 'Cambio (%)')
            if cambio:
                cambio = cambio.replace('%', '').strip()
            data['cambio_porcentual'] = cambio or "0"
            
            # Capitalización
            cap_str = extract_from_table(content, 'Capitalización de Mercado')
            if cap_str:
                try:
                    cap_val = float(cap_str.replace('$', '').replace(',', ''))
                    data['market_cap_b'] = f"{cap_val/1e12:.2f}"
                except:
                    data['market_cap_b'] = cap_str
            else:
                data['market_cap_b'] = "N/D"
            
            # Múltiplos
            data['pe_trailing'] = extract_from_table(content, 'P/E Trailing') or "N/D"
            data['pe_forward'] = extract_from_table(content, 'P/E Forward') or "N/D"
            data['peg_ratio'] = extract_from_table(content, 'Ratio PEG') or "N/D"
            data['price_to_book'] = extract_from_table(content, 'Precio/Libro') or "N/D"
            
            # Dividendos
            div = extract_from_table(content, 'Rendimiento de Dividendos')
            if div:
                div = div.replace('%', '').strip()
            data['dividend_yield'] = div or "0"
            
            print(f"DEBUG: Extractor técnico - ticker={data['ticker']}, empresa={data['nombre_empresa']}")
            
        except Exception as e:
            print(f"Advertencia al extraer del técnico: {e}")
            import traceback
            traceback.print_exc()
        
        return data

    def extract_from_fundamental(self) -> Dict[str, Any]:
        """Extrae datos del informe fundamental."""
        data = {}
        try:
            with open(self.fundamental_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Visión estratégica (primeros 200 chars)
            match = re.search(r'## Visión Estratégica a Largo Plazo\n\n(.+?)(?=\n##|\n---)', 
                            content, re.DOTALL)
            if match:
                vision_text = match.group(1).strip()
                # Tomar los primeros 150 caracteres aproximadamente
                data['vision_resumen'] = vision_text[:200] + "..." if len(vision_text) > 200 else vision_text
            else:
                data['vision_resumen'] = "N/D"
            
            # Ventajas competitivas (bullet points)
            match = re.search(r'## Ventajas Competitivas.*?\n\n(.+?)(?=\n##|\n---)', 
                            content, re.DOTALL)
            if match:
                ventures_text = match.group(1).strip()
                # Extraer primeras 3 líneas con guiones
                lines = [l.strip() for l in ventures_text.split('\n') if l.strip().startswith('-')][:3]
                data['ventajas_key'] = lines
            else:
                data['ventajas_key'] = []
            
            # Valores corporativos (buscar sección de cultura)
            match = re.search(r'## Valores Corporativos.*?\n\n(.+?)(?=\n##|\n---)', 
                            content, re.DOTALL)
            if match:
                valores_text = match.group(1).strip()[:150]
                data['valores'] = valores_text
            else:
                data['valores'] = "N/D"
                
        except Exception as e:
            print(f"Advertencia al extraer del fundamental: {e}")
        
        return data

    def extract_from_berkshire(self) -> Dict[str, Any]:
        """Extrae datos del informe Berkshire."""
        data = {}
        try:
            with open(self.berkshire_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Recomendación
            match = re.search(r'\*\*Recomendación:\*\*\s*([A-Z]+)', content)
            data['recomendacion'] = match.group(1) if match else "N/D"
            
            # Valuación objetivo
            match = re.search(r'\*\*Valoración Objetiva Range:\*\*\s*\$?([\d.,]+)\s*-\s*\$?([\d.,]+)', 
                            content)
            if match:
                data['precio_objetivo_min'] = match.group(1).strip()
                data['precio_objetivo_max'] = match.group(2).strip()
            else:
                data['precio_objetivo_min'] = "N/D"
                data['precio_objetivo_max'] = "N/D"
            
            # Margen de seguridad
            match = re.search(r'\*\*Margen de Seguridad Actual:\*\*\s*([^\n]+)', content)
            data['margen_seguridad'] = match.group(1).strip() if match else "N/D"
            
            # Moat rating (buscar en tabla o texto)
            match = re.search(r'Moat Económico:\s*([A-Z]+)\s*\(Fortaleza\s*(\d+)/10\)', content)
            if match:
                data['moat_rating'] = f"{match.group(2)}/10"
                data['tipo_moat'] = "Económico - Extraordinario"
            else:
                data['moat_rating'] = "N/D"
                data['tipo_moat'] = "N/D"
            
            # Defensas principales (buscar tabla de moat)
            defensas = []
            match = re.search(r'## Análisis del Moat Competitivo.*?\n+.*?\|\s*Factor\s*\|(.+?)(?=\n##|\Z)', 
                            content, re.DOTALL)
            if match:
                table_content = match.group(1)
                rows = table_content.split('\n')[2:]  # Saltar header
                for row in rows[:3]:
                    if '|' in row:
                        parts = [p.strip() for p in row.split('|')]
                        if len(parts) > 1 and parts[1]:
                            defensas.append(parts[1])
            
            data['defensas_principales'] = defensas[:3] if defensas else ["N/D"]
            
            # Cuota de mercado
            match = re.search(r'Cuota de Mercado.*?(\d+)%', content)
            data['market_share'] = match.group(1) if match else "N/D"
            
            # Track record de gestión (buscar decisiones críticas)
            decisions = []
            match = re.search(r'### Pivot.*?\n\n(.+?)(?=\n###|\n##)', content, re.DOTALL)
            if match:
                decision_text = match.group(1).strip().split('\n')[0]
                decisions.append(decision_text[:80])
            
            data['decisiones_clave'] = decisions if decisions else ["N/D"]
            
            # Tesis de inversión (buscar resumen ejecutivo)
            match = re.search(r'## Resumen Ejecutivo\n\n(.+?)(?=\*\*|###)', 
                            content, re.DOTALL)
            if match:
                data['tesis_ejecutiva'] = match.group(1).strip()[:200]
            else:
                data['tesis_ejecutiva'] = "N/D"
                
        except Exception as e:
            print(f"Advertencia al extraer del Berkshire: {e}")
        
        return data

    def consolidate(self) -> str:
        """Consolida todos los datos en el informe final."""
        if not self.validate_files():
            sys.exit(1)
        
        print(f"Extrayendo datos para {self.ticker}...")
        
        technical = self.extract_from_technical()
        fundamental = self.extract_from_fundamental()
        berkshire = self.extract_from_berkshire()
        
        self.data = {**technical, **fundamental, **berkshire}
        
        # Generar fecha
        from datetime import datetime
        self.data['fecha_analisis'] = datetime.now().strftime("%Y-%m-%d")
        
        # Generar resumen ejecutivo integrado
        self.data['resumen_ejecutivo'] = self._generate_executive_summary()
        
        # Generar contextos para cada sección
        self.data['mercado_posicion'] = f"Top {self.data.get('market_cap_b', 'N/D')}B"
        self.data['valoracion_vs_sector'] = self._interpret_pe()
        self.data['moat_description'] = self._moat_description()
        
        print(f"DEBUG: self.data keys = {list(self.data.keys())}")
        print(f"DEBUG: nombre_empresa = {self.data.get('nombre_empresa', 'NOT FOUND')}")
        
        return self.data

    def _generate_executive_summary(self) -> str:
        """Genera un resumen ejecutivo integrado."""
        empresa = self.data.get('nombre_empresa', 'Empresa')
        recomendacion = self.data.get('recomendacion', 'N/D')
        tesis = self.data.get('tesis_ejecutiva', '')
        
        summary = f"{empresa} presenta una propuesta de inversión {recomendacion}. "
        summary += f"Con valuación actual de ${ self.data.get('precio_actual', 'N/D')}, "
        summary += f"P/E Forward de {self.data.get('pe_forward', 'N/D')} y PEG de {self.data.get('peg_ratio', 'N/D')}, "
        summary += f"la empresa muestra {self._moat_description() if self._moat_description() != 'N/D' else 'defensas competitivas sólidas'}. "
        summary += f"Objetivo a 12-24 meses: ${self.data.get('precio_objetivo_min', 'N/D')} - "
        summary += f"${self.data.get('precio_objetivo_max', 'N/D')}."
        
        return summary

    def _interpret_pe(self) -> str:
        """Interpreta el P/E Forward."""
        try:
            pe = float(self.data.get('pe_forward', '0').replace(',', ''))
            if pe < 15:
                return "Valuación atractiva vs crecimiento esperado"
            elif pe < 25:
                return "Valuación moderada con prima de crecimiento justificada"
            else:
                return "Valuación premium, requiere ejecución excepcional"
        except:
            return "Valuación por determinar"

    def _moat_description(self) -> str:
        """Describe el moat competitivo."""
        defensas = self.data.get('defensas_principales', [])
        if defensas and defensas[0] != "N/D":
            return f"moat {self.data.get('moat_rating', 'N/D')} apoyado en {len(defensas)} defensas principales"
        return "N/D"

    def generate_final_report(self, template_file: Optional[str] = None) -> str:
        """Genera el informe final usando la plantilla."""
        if not template_file:
            template_file = Path(__file__).parent.parent / "references" / "plantilla.md"
        
        if not Path(template_file).exists():
            print(f"ERROR: Plantilla no encontrada en {template_file}")
            sys.exit(1)
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        print(f"DEBUG: Plantilla cargada de {template_file}")
        
        # Mapeo de placeholders de plantilla a keys de self.data
        placeholder_mapping = {
            'TICKER': 'ticker',
            'NOMBRE_EMPRESA': 'nombre_empresa',
            'SECTOR': 'sector',
            'INDUSTRIA': 'industria',
            'FECHA_ANÁLISIS': 'fecha_analisis',
            'RECOMENDACIÓN': 'recomendacion',
            'PRECIO_ACTUAL': 'precio_actual',
            'CAMBIO_PORCENTUAL': 'cambio_porcentual',
            'MARKET_CAP_B': 'market_cap_b',
            'PE_TRAILING': 'pe_trailing',
            'PE_FORWARD': 'pe_forward',
            'PEG_RATIO': 'peg_ratio',
            'PRICE_TO_BOOK': 'price_to_book',
            'DIVIDEND_YIELD': 'dividend_yield',
            'MOAT_RATING': 'moat_rating',
            'TIPO_MOAT': 'tipo_moat',
            'MARKET_SHARE': 'market_share',
            'PRECIO_OBJETIVO_MIN': 'precio_objetivo_min',
            'PRECIO_OBJETIVO_MAX': 'precio_objetivo_max',
            'MARGEN_SEGURIDAD': 'margen_seguridad',
        }
        
        # Reemplazar cada placeholder
        report = template
        replaced_count = 0
        for placeholder, data_key in placeholder_mapping.items():
            value = self.data.get(data_key, "N/D")
            
            # Si es una lista, unir con saltos de línea
            if isinstance(value, list):
                value_str = "\n".join([f"- {v}" for v in value if v != "N/D"])
            else:
                value_str = str(value) if value else "N/D"
            
            # Reemplazar el placeholder (sin espacios adicionales)
            pattern = f"{{{{{placeholder}}}}}"  # {{ PLACEHOLDER }}
            old_report = report
            report = report.replace(pattern, value_str)
            if report != old_report:
                replaced_count += 1
                if len(value_str) > 50:
                    print(f"DEBUG: Reemplazado {placeholder} -> {value_str[:50]}...")
                else:
                    print(f"DEBUG: Reemplazado {placeholder} -> {value_str}")
        
        print(f"DEBUG: Total placeholders reemplazados: {replaced_count}/{len(placeholder_mapping)}")
        
        # Reemplazar variables restantes que no se hayan mapificado con N/D
        report = re.sub(r'\{\{\s*[A-Z_]+\s*\}\}', 'N/D', report)
        
        return report

    def save_report(self, report_content: str) -> None:
        """Guarda el informe final."""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Informe guardado en: {self.output_file}")

    def run(self, template_file: Optional[str] = None) -> None:
        """Ejecuta el proceso completo de consolidación."""
        print(f"Consolidando informes para {self.ticker}...")
        
        # Extraer y consolidar datos
        self.consolidate()
        
        # Generar informe final
        report = self.generate_final_report(template_file)
        
        # Guardar
        self.save_report(report)
        print(f"Consolidación completada exitosamente para {self.ticker}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python consolidate_reports.py <path_a_directorio_ticker>")
        print("Ejemplo: python consolidate_reports.py evaluaciones/NVDA")
        sys.exit(1)
    
    ticker_dir = sys.argv[1]
    template_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    consolidator = ReportConsolidator(ticker_dir)
    consolidator.run(template_file)


if __name__ == "__main__":
    main()
