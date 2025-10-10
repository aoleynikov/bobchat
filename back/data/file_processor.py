from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any, List
import io
import zipfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

class FileProcessor(ABC):
    def __init__(self, chunk_size: int = 8192, **kwargs):
        self.chunk_size = chunk_size
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @abstractmethod
    def process_file(self, file: BinaryIO) -> List[str]:
        pass
    
    @abstractmethod
    def process(self, obj) -> List[str]:
        pass

class FileProcessorFactory:
    def __init__(self, processors: Dict[str, FileProcessor] = None):
        self.processors = processors or {}
        self.file_type_mapping = {
            '.epub': 'epub',
            '.html': 'html',
            '.htm': 'html',
            '.txt': 'text',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.bmp': 'image'
        }
    
    def create(self, processor_type: str, chunk_size: int = 8192, **config) -> FileProcessor:
        if processor_type not in self.processors:
            raise ValueError(f'Unknown processor type: {processor_type}')
        
        processor = self.processors[processor_type]
        if config:
            processor_class = type(processor)
            return processor_class(chunk_size=chunk_size, **config)
        return processor
    
    def get_processor_for_file(self, file_path: str) -> FileProcessor:
        from pathlib import Path
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.file_type_mapping:
            raise ValueError(f'Unsupported file type: {file_extension}')
        
        processor_type = self.file_type_mapping[file_extension]
        return self.create(processor_type)

class TextFileProcessor(FileProcessor):
    def process_file(self, file: BinaryIO) -> List[str]:
        content = file.read()
        return [content.decode('utf-8')]
    
    def process(self, text: str) -> List[str]:
        return [text]

class HTMLFileProcessor(FileProcessor):
    def process_file(self, file: BinaryIO) -> List[str]:
        content = file.read()
        html_text = content.decode('utf-8')
        return self.process(html_text)
    
    def process(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        return [soup.get_text(separator=' ', strip=True)]

class PDFFileProcessor(FileProcessor):
    def process_file(self, file: BinaryIO) -> List[str]:
        return ["PDF processing not implemented"]
    
    def process(self, pdf_content: str) -> List[str]:
        return [pdf_content]

class ImageFileProcessor(FileProcessor):
    def process_file(self, file: BinaryIO) -> List[str]:
        return ["Image processing not implemented"]
    
    def process(self, image_data: bytes) -> List[str]:
        return ["Image processing not implemented"]

class EPUBFileProcessor(FileProcessor):
    def __init__(self, chunk_size: int, text_processor: FileProcessor, html_processor: FileProcessor, image_processor: FileProcessor):
        super().__init__(chunk_size)
        self.text_processor = text_processor
        self.html_processor = html_processor
        self.image_processor = image_processor
    
    def process_file(self, file: BinaryIO) -> List[str]:
        file.seek(0)
        
        with zipfile.ZipFile(file, 'r') as epub_zip:
            # Read the container.xml to find the OPF file
            container_xml = epub_zip.read('META-INF/container.xml')
            container_root = ET.fromstring(container_xml)
            
            # Find the OPF file path
            opf_path = None
            for rootfile in container_root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile'):
                if rootfile.get('media-type') == 'application/oebps-package+xml':
                    opf_path = rootfile.get('full-path')
                    break
            
            if not opf_path:
                return ["Could not find OPF file in EPUB"]
            
            # Read the OPF file to get manifest
            opf_content = epub_zip.read(opf_path)
            opf_root = ET.fromstring(opf_content)
            
            # Extract content from all files
            all_content = []
            
            # Find all manifest items
            items = opf_root.findall('.//{http://www.idpf.org/2007/opf}item')
            
            for item in items:
                href = item.get('href')
                media_type = item.get('media-type')
                
                if media_type in ['application/xhtml+xml', 'text/html']:
                    # Dispatch to HTML processor
                    try:
                        # Try the href as-is first, then with OPS/ prefix
                        try:
                            html_content = epub_zip.read(href)
                        except KeyError:
                            # Try with OPS/ prefix (common in EPUB files)
                            html_content = epub_zip.read(f"OPS/{href}")
                        
                        html_io = io.BytesIO(html_content)
                        processed_texts = self.html_processor.process_file(html_io)
                        all_content.extend(processed_texts)
                    except Exception:
                        continue
                
                elif media_type == 'text/plain':
                    # Dispatch to text processor
                    try:
                        text_content = epub_zip.read(href)
                        text_io = io.BytesIO(text_content)
                        processed_texts = self.text_processor.process_file(text_io)
                        all_content.extend(processed_texts)
                    except Exception:
                        continue
                
                elif media_type and media_type.startswith('image/'):
                    # Dispatch to image processor
                    try:
                        image_data = epub_zip.read(href)
                        image_io = io.BytesIO(image_data)
                        processed_images = self.image_processor.process_file(image_io)
                        for processed_image in processed_images:
                            all_content.append(f"[Image: {href}] {processed_image}")
                    except Exception:
                        continue
            
            return all_content
    
    def process(self, epub_content: List[str]) -> List[str]:
        return epub_content
