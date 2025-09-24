"""
Processador para documentos Open Document Format (ODF)
Suporta: ODT (texto), ODS (planilhas), ODP (apresentações)
"""
import logging
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class ODFProcessor:
    """Processador para documentos Open Document Format"""
    
    def __init__(self):
        self.supported_extensions = ['.odt', '.ods', '.odp']
        self.namespaces = {
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
            'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
            'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
            'presentation': 'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0',
            'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
            'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'
        }
    
    def can_process(self, file_path: str) -> bool:
        """Verifica se o arquivo pode ser processado"""
        return Path(file_path).suffix.lower() in self.supported_extensions
    
    def extract_text_from_odt(self, file_path: str) -> str:
        """Extrai texto de documentos ODT (LibreOffice Writer)"""
        try:
            with zipfile.ZipFile(file_path, 'r') as odt_file:
                # ODT é um arquivo ZIP que contém content.xml
                if 'content.xml' not in odt_file.namelist():
                    logger.warning(f"content.xml não encontrado em {file_path}")
                    return ""
                
                content_xml = odt_file.read('content.xml')
                root = ET.fromstring(content_xml)
                
                # Extrai todo o texto do documento
                text_content = []
                self._extract_text_recursive(root, text_content)
                
                return '\n'.join(text_content)
                
        except Exception as e:
            logger.error(f"Erro ao processar ODT {file_path}: {e}")
            return ""
    
    def extract_text_from_ods(self, file_path: str) -> str:
        """Extrai texto de planilhas ODS (LibreOffice Calc)"""
        try:
            with zipfile.ZipFile(file_path, 'r') as ods_file:
                if 'content.xml' not in ods_file.namelist():
                    logger.warning(f"content.xml não encontrado em {file_path}")
                    return ""
                
                content_xml = ods_file.read('content.xml')
                root = ET.fromstring(content_xml)
                
                # Extrai dados das células da planilha
                text_content = []
                self._extract_spreadsheet_data(root, text_content)
                
                return '\n'.join(text_content)
                
        except Exception as e:
            logger.error(f"Erro ao processar ODS {file_path}: {e}")
            return ""
    
    def extract_text_from_odp(self, file_path: str) -> str:
        """Extrai texto de apresentações ODP (LibreOffice Impress)"""
        try:
            with zipfile.ZipFile(file_path, 'r') as odp_file:
                if 'content.xml' not in odp_file.namelist():
                    logger.warning(f"content.xml não encontrado em {file_path}")
                    return ""
                
                content_xml = odp_file.read('content.xml')
                root = ET.fromstring(content_xml)
                
                # Extrai texto dos slides
                text_content = []
                self._extract_presentation_data(root, text_content)
                
                return '\n'.join(text_content)
                
        except Exception as e:
            logger.error(f"Erro ao processar ODP {file_path}: {e}")
            return ""
    
    def _extract_text_recursive(self, element: ET.Element, text_content: List[str]) -> None:
        """Extrai texto recursivamente de elementos XML"""
        if element.text and element.text.strip():
            text_content.append(element.text.strip())
        
        for child in element:
            self._extract_text_recursive(child, text_content)
            if child.tail and child.tail.strip():
                text_content.append(child.tail.strip())
    
    def _extract_spreadsheet_data(self, root: ET.Element, text_content: List[str]) -> None:
        """Extrai dados de planilhas"""
        # Procura por células de tabela
        for table in root.findall('.//table:table', self.namespaces):
            table_name = table.get('table:name', 'Tabela')
            text_content.append(f"\n=== {table_name} ===")
            
            for row in table.findall('.//table:table-row', self.namespaces):
                row_data = []
                for cell in row.findall('.//table:table-cell', self.namespaces):
                    cell_text = self._get_cell_text(cell)
                    if cell_text:
                        row_data.append(cell_text)
                
                if row_data:
                    text_content.append(' | '.join(row_data))
    
    def _extract_presentation_data(self, root: ET.Element, text_content: List[str]) -> None:
        """Extrai dados de apresentações"""
        slide_count = 0
        
        # Procura por slides
        for slide in root.findall('.//draw:page', self.namespaces):
            slide_count += 1
            text_content.append(f"\n=== Slide {slide_count} ===")
            
            # Extrai texto dos elementos do slide
            for text_element in slide.findall('.//text:p', self.namespaces):
                slide_text = self._get_element_text(text_element)
                if slide_text:
                    text_content.append(slide_text)
    
    def _get_cell_text(self, cell: ET.Element) -> str:
        """Extrai texto de uma célula de planilha"""
        text_parts = []
        
        # Procura por parágrafos de texto na célula
        for p in cell.findall('.//text:p', self.namespaces):
            cell_text = self._get_element_text(p)
            if cell_text:
                text_parts.append(cell_text)
        
        return ' '.join(text_parts)
    
    def _get_element_text(self, element: ET.Element) -> str:
        """Extrai texto de um elemento XML"""
        text_parts = []
        
        if element.text:
            text_parts.append(element.text)
        
        for child in element:
            child_text = self._get_element_text(child)
            if child_text:
                text_parts.append(child_text)
        
        if element.tail:
            text_parts.append(element.tail)
        
        return ''.join(text_parts).strip()
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrai metadados do documento ODF"""
        metadata = {
            'file_type': 'ODF',
            'file_extension': Path(file_path).suffix.lower(),
            'title': '',
            'author': '',
            'subject': '',
            'keywords': '',
            'creation_date': '',
            'modification_date': '',
            'page_count': 0,
            'word_count': 0
        }
        
        try:
            with zipfile.ZipFile(file_path, 'r') as odf_file:
                # Tenta extrair metadados do meta.xml
                if 'meta.xml' in odf_file.namelist():
                    meta_xml = odf_file.read('meta.xml')
                    root = ET.fromstring(meta_xml)
                    
                    # Extrai metadados básicos
                    for meta in root.findall('.//meta:user-defined', self.namespaces):
                        name = meta.get('meta:name', '')
                        value = meta.text or ''
                        
                        if name.lower() in ['title', 'author', 'subject', 'keywords']:
                            metadata[name.lower()] = value
                
                # Conta páginas e palavras baseado no conteúdo
                if 'content.xml' in odf_file.namelist():
                    content_xml = odf_file.read('content.xml')
                    root = ET.fromstring(content_xml)
                    
                    # Conta parágrafos (aproximação de páginas)
                    paragraphs = root.findall('.//text:p', self.namespaces)
                    metadata['page_count'] = len(paragraphs) // 20  # Aproximação
                    
                    # Conta palavras
                    all_text = []
                    self._extract_text_recursive(root, all_text)
                    full_text = ' '.join(all_text)
                    metadata['word_count'] = len(full_text.split())
        
        except Exception as e:
            logger.error(f"Erro ao extrair metadados de {file_path}: {e}")
        
        return metadata
    
    def process_odf_document(self, file_path: str) -> Dict[str, Any]:
        """Processa um documento ODF completo"""
        file_extension = Path(file_path).suffix.lower()
        
        # Extrai texto baseado no tipo de arquivo
        if file_extension == '.odt':
            text_content = self.extract_text_from_odt(file_path)
        elif file_extension == '.ods':
            text_content = self.extract_text_from_ods(file_path)
        elif file_extension == '.odp':
            text_content = self.extract_text_from_odp(file_path)
        else:
            logger.warning(f"Tipo de arquivo ODF não suportado: {file_extension}")
            text_content = ""
        
        # Extrai metadados
        metadata = self.extract_metadata(file_path)
        
        # Limpa e processa o texto
        cleaned_text = self._clean_text(text_content)
        
        return {
            'file_path': file_path,
            'file_type': 'ODF',
            'file_extension': file_extension,
            'content': {
                'text': cleaned_text,
                'raw_text': text_content,
                'word_count': len(cleaned_text.split()),
                'char_count': len(cleaned_text)
            },
            'metadata': metadata,
            'processing_info': {
                'processor': 'ODFProcessor',
                'success': bool(cleaned_text),
                'error': None if cleaned_text else 'Falha ao extrair texto'
            }
        }
    
    def _clean_text(self, text: str) -> str:
        """Limpa e formata o texto extraído"""
        if not text:
            return ""
        
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text)
        
        # Remove quebras de linha desnecessárias
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        return text.strip()
    
    def get_supported_extensions(self) -> List[str]:
        """Retorna lista de extensões suportadas"""
        return self.supported_extensions.copy()
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o processador"""
        return {
            'name': 'ODFProcessor',
            'version': '1.0.0',
            'description': 'Processador para documentos Open Document Format',
            'supported_formats': {
                '.odt': 'LibreOffice Writer (Documento de texto)',
                '.ods': 'LibreOffice Calc (Planilha)',
                '.odp': 'LibreOffice Impress (Apresentação)'
            },
            'features': [
                'Extração de texto de documentos ODT',
                'Extração de dados de planilhas ODS',
                'Extração de texto de apresentações ODP',
                'Extração de metadados',
                'Limpeza e formatação de texto',
                'Contagem de palavras e caracteres'
            ]
        }
