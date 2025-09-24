"""
Markdown generator for creating and managing RAG notes
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import re

from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkdownGenerator:
    """Generate and manage markdown notes from RAG system"""
    
    def __init__(self, rag_agent=None):
        self.rag_agent = rag_agent
        self.ragfiles_dir = RAGFILES_DIR
        self.ragfiles_dir.mkdir(exist_ok=True)
    
    def generate_document_notes(self, documents: List[Dict[str, Any]], 
                             language: str = 'pt') -> List[Dict[str, Any]]:
        """Generate markdown notes for processed documents"""
        generated_notes = []
        
        for doc in documents:
            try:
                note = self._create_document_note(doc, language)
                if note:
                    generated_notes.append(note)
            except Exception as e:
                logger.error(f"Error generating note for document: {e}")
                continue
        
        logger.info(f"Generated {len(generated_notes)} markdown notes")
        return generated_notes
    
    def _create_document_note(self, doc: Dict[str, Any], language: str) -> Optional[Dict[str, Any]]:
        """Create a markdown note for a single document"""
        try:
            # Extract document information
            file_path = doc.get('file_path', '')
            file_type = doc.get('file_type', '')
            content = doc.get('content', {})
            metadata = doc.get('metadata', {})
            
            # Create note filename
            note_filename = self._create_note_filename(file_path, file_type)
            note_path = self.ragfiles_dir / note_filename
            
            # Generate note content
            note_content = self._generate_note_content(doc, language)
            
            # Write note to file
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            return {
                'note_path': str(note_path),
                'source_document': file_path,
                'file_type': file_type,
                'language': language,
                'created_at': datetime.now().isoformat(),
                'word_count': len(note_content.split())
            }
            
        except Exception as e:
            logger.error(f"Error creating document note: {e}")
            return None
    
    def _create_note_filename(self, file_path: str, file_type: str) -> str:
        """Create filename for markdown note"""
        # Extract base name from file path
        base_name = Path(file_path).stem
        
        # Clean filename
        clean_name = re.sub(r'[^\w\-_\.]', '_', base_name)
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{clean_name}_{file_type}_{timestamp}.md"
    
    def _generate_note_content(self, doc: Dict[str, Any], language: str) -> str:
        """Generate markdown content for document note"""
        file_path = doc.get('file_path', '')
        file_type = doc.get('file_type', '')
        content = doc.get('content', {})
        metadata = doc.get('metadata', {})
        
        # Start building markdown content
        lines = []
        
        # Header
        if language == 'pt':
            lines.append(f"# Notas do Documento: {Path(file_path).name}")
            lines.append("")
            lines.append("## Informações do Arquivo")
        else:
            lines.append(f"# Document Notes: {Path(file_path).name}")
            lines.append("")
            lines.append("## File Information")
        
        # File metadata
        lines.append(f"- **Caminho do arquivo:** {file_path}")
        lines.append(f"- **Tipo de arquivo:** {file_type}")
        lines.append(f"- **Tamanho:** {metadata.get('size_mb', 0)} MB")
        lines.append(f"- **Modificado em:** {metadata.get('modified_at', 'N/A')}")
        lines.append(f"- **Hash do arquivo:** {metadata.get('file_hash', 'N/A')}")
        lines.append("")
        
        # Content sections
        if content.get('text'):
            if language == 'pt':
                lines.append("## Conteúdo Extraído")
            else:
                lines.append("## Extracted Content")
            
            text = content['text']
            # Truncate if too long
            if len(text) > 2000:
                text = text[:2000] + "\n\n... (conteúdo truncado)"
            
            lines.append("")
            lines.append(text)
            lines.append("")
        
        # Code content
        if content.get('code_structure'):
            if language == 'pt':
                lines.append("## Análise de Código")
            else:
                lines.append("## Code Analysis")
            
            code_structure = content['code_structure']
            if code_structure.get('functions'):
                lines.append("### Funções encontradas:")
                for func in code_structure['functions']:
                    lines.append(f"- {func}")
                lines.append("")
            
            if code_structure.get('classes'):
                lines.append("### Classes encontradas:")
                for cls in code_structure['classes']:
                    lines.append(f"- {cls}")
                lines.append("")
        
        # Tables
        if content.get('tables'):
            if language == 'pt':
                lines.append("## Tabelas Extraídas")
            else:
                lines.append("## Extracted Tables")
            
            for i, table in enumerate(content['tables'], 1):
                lines.append(f"### Tabela {i} (Página {table.get('page', 'N/A')})")
                lines.append("")
                
                # Create markdown table
                table_data = table.get('data', [])
                if table_data:
                    # Header row
                    if table_data[0]:
                        header = "| " + " | ".join(str(cell) for cell in table_data[0]) + " |"
                        lines.append(header)
                        lines.append("| " + " | ".join("---" for _ in table_data[0]) + " |")
                        
                        # Data rows
                        for row in table_data[1:]:
                            if row:
                                row_str = "| " + " | ".join(str(cell) for cell in row) + " |"
                                lines.append(row_str)
                        lines.append("")
        
        # Statistics
        if content.get('statistics'):
            if language == 'pt':
                lines.append("## Estatísticas")
            else:
                lines.append("## Statistics")
            
            stats = content['statistics']
            lines.append(f"- **Número de palavras:** {stats.get('word_count', 0)}")
            lines.append(f"- **Número de caracteres:** {stats.get('character_count', 0)}")
            lines.append(f"- **Idioma detectado:** {stats.get('language', 'N/A')}")
            lines.append("")
        
        # Processing information
        if language == 'pt':
            lines.append("## Informações de Processamento")
        else:
            lines.append("## Processing Information")
        
        lines.append(f"- **Processado em:** {doc.get('processed_at', 'N/A')}")
        lines.append(f"- **Gerado em:** {datetime.now().isoformat()}")
        lines.append("")
        
        # Footer
        if language == 'pt':
            lines.append("---")
            lines.append("*Nota gerada automaticamente pelo sistema RAG Local*")
        else:
            lines.append("---")
            lines.append("*Note automatically generated by Local RAG system*")
        
        return "\n".join(lines)
    
    def generate_summary_notes(self, documents: List[Dict[str, Any]], 
                            language: str = 'pt') -> Dict[str, Any]:
        """Generate summary notes for a collection of documents"""
        try:
            # Create summary filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_filename = f"resumo_geral_{timestamp}.md"
            summary_path = self.ragfiles_dir / summary_filename
            
            # Generate summary content
            summary_content = self._generate_summary_content(documents, language)
            
            # Write summary to file
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            return {
                'summary_path': str(summary_path),
                'documents_count': len(documents),
                'language': language,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating summary notes: {e}")
            return None
    
    def _generate_summary_content(self, documents: List[Dict[str, Any]], language: str) -> str:
        """Generate summary content for document collection"""
        lines = []
        
        # Header
        if language == 'pt':
            lines.append("# Resumo Geral dos Documentos")
            lines.append("")
            lines.append(f"**Total de documentos processados:** {len(documents)}")
            lines.append(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            lines.append("")
        else:
            lines.append("# General Document Summary")
            lines.append("")
            lines.append(f"**Total processed documents:** {len(documents)}")
            lines.append(f"**Generated on:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            lines.append("")
        
        # Document list
        if language == 'pt':
            lines.append("## Lista de Documentos")
        else:
            lines.append("## Document List")
        
        lines.append("")
        
        # Group by file type
        file_types = {}
        for doc in documents:
            file_type = doc.get('file_type', 'unknown')
            if file_type not in file_types:
                file_types[file_type] = []
            file_types[file_type].append(doc)
        
        for file_type, docs in file_types.items():
            if language == 'pt':
                lines.append(f"### {file_type.upper()} ({len(docs)} arquivos)")
            else:
                lines.append(f"### {file_type.upper()} ({len(docs)} files)")
            
            lines.append("")
            
            for doc in docs:
                file_path = doc.get('file_path', '')
                metadata = doc.get('metadata', {})
                content = doc.get('content', {})
                
                lines.append(f"- **{Path(file_path).name}**")
                lines.append(f"  - Caminho: {file_path}")
                lines.append(f"  - Tamanho: {metadata.get('size_mb', 0)} MB")
                
                if content.get('statistics'):
                    stats = content['statistics']
                    lines.append(f"  - Palavras: {stats.get('word_count', 0)}")
                
                lines.append("")
        
        # Statistics
        if language == 'pt':
            lines.append("## Estatísticas Gerais")
        else:
            lines.append("## General Statistics")
        
        lines.append("")
        
        total_words = sum(
            doc.get('content', {}).get('statistics', {}).get('word_count', 0)
            for doc in documents
        )
        total_size = sum(
            doc.get('metadata', {}).get('size_mb', 0)
            for doc in documents
        )
        
        lines.append(f"- **Total de palavras:** {total_words:,}")
        lines.append(f"- **Tamanho total:** {total_size:.2f} MB")
        lines.append(f"- **Tipos de arquivo:** {len(file_types)}")
        lines.append("")
        
        # Footer
        if language == 'pt':
            lines.append("---")
            lines.append("*Resumo gerado automaticamente pelo sistema RAG Local*")
        else:
            lines.append("---")
            lines.append("*Summary automatically generated by Local RAG system*")
        
        return "\n".join(lines)
    
    def generate_query_notes(self, query_results: List[Dict[str, Any]], 
                           language: str = 'pt') -> Dict[str, Any]:
        """Generate notes from query results"""
        try:
            # Create query notes filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            query_filename = f"consulta_{timestamp}.md"
            query_path = self.ragfiles_dir / query_filename
            
            # Generate query content
            query_content = self._generate_query_content(query_results, language)
            
            # Write query notes to file
            with open(query_path, 'w', encoding='utf-8') as f:
                f.write(query_content)
            
            return {
                'query_path': str(query_path),
                'queries_count': len(query_results),
                'language': language,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating query notes: {e}")
            return None
    
    def _generate_query_content(self, query_results: List[Dict[str, Any]], language: str) -> str:
        """Generate content for query results"""
        lines = []
        
        # Header
        if language == 'pt':
            lines.append("# Notas de Consultas RAG")
            lines.append("")
            lines.append(f"**Total de consultas:** {len(query_results)}")
            lines.append(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            lines.append("")
        else:
            lines.append("# RAG Query Notes")
            lines.append("")
            lines.append(f"**Total queries:** {len(query_results)}")
            lines.append(f"**Generated on:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            lines.append("")
        
        # Query results
        for i, result in enumerate(query_results, 1):
            question = result.get('question', '')
            answer = result.get('answer', '')
            sources = result.get('sources', [])
            confidence = result.get('confidence', 0)
            
            if language == 'pt':
                lines.append(f"## Consulta {i}")
            else:
                lines.append(f"## Query {i}")
            
            lines.append("")
            lines.append(f"**Pergunta:** {question}")
            lines.append("")
            lines.append(f"**Resposta:** {answer}")
            lines.append("")
            lines.append(f"**Confiança:** {confidence:.2f}")
            lines.append("")
            
            if sources:
                if language == 'pt':
                    lines.append("### Fontes")
                else:
                    lines.append("### Sources")
                
                lines.append("")
                
                for j, source in enumerate(sources, 1):
                    file_path = source.get('file_path', '')
                    similarity = source.get('similarity', 0)
                    preview = source.get('text_preview', '')
                    
                    lines.append(f"{j}. **{Path(file_path).name}** (similaridade: {similarity:.2f})")
                    lines.append(f"   - Caminho: {file_path}")
                    if preview:
                        lines.append(f"   - Preview: {preview[:100]}...")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Footer
        if language == 'pt':
            lines.append("*Notas de consulta geradas automaticamente pelo sistema RAG Local*")
        else:
            lines.append("*Query notes automatically generated by Local RAG system*")
        
        return "\n".join(lines)
    
    def update_note(self, note_path: str, new_content: str) -> bool:
        """Update an existing markdown note"""
        try:
            note_file = Path(note_path)
            if not note_file.exists():
                logger.error(f"Note file not found: {note_path}")
                return False
            
            # Backup original
            backup_path = note_file.with_suffix('.md.backup')
            note_file.rename(backup_path)
            
            # Write new content
            with open(note_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Updated note: {note_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            return False
    
    def get_note_list(self) -> List[Dict[str, Any]]:
        """Get list of all markdown notes"""
        notes = []
        
        try:
            for note_file in self.ragfiles_dir.glob("*.md"):
                stat = note_file.stat()
                notes.append({
                    'filename': note_file.name,
                    'path': str(note_file),
                    'size_bytes': stat.st_size,
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
            
            # Sort by modification time (newest first)
            notes.sort(key=lambda x: x['modified_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting note list: {e}")
        
        return notes
    
    def delete_note(self, note_path: str) -> bool:
        """Delete a markdown note"""
        try:
            note_file = Path(note_path)
            if note_file.exists():
                note_file.unlink()
                logger.info(f"Deleted note: {note_path}")
                return True
            else:
                logger.warning(f"Note file not found: {note_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            return False
