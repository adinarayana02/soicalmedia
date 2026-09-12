import zipfile
from typing import List, Dict, Any, Optional
from zip_processor.parsers.base import BasePlatformParser
from zip_processor.parsers.instagram import InstagramParser
from zip_processor.parsers.whatsapp import WhatsAppParser
from zip_processor.parsers.telegram import TelegramParser

class ParserRegistry:
    def __init__(self):
        self.parsers: List[BasePlatformParser] = [
            InstagramParser(),
            WhatsAppParser(),
            TelegramParser()
        ]
        
    def register_parser(self, parser: BasePlatformParser):
        """Allows new third-party or custom platform parsers to be registered dynamically."""
        self.parsers.append(parser)

    def detect_and_parse(self, zip_ref: zipfile.ZipFile) -> Dict[str, Any]:
        file_list = [info.filename for info in zip_ref.infolist()]
        
        for parser in self.parsers:
            if parser.can_parse(file_list):
                print(f"[ParserRegistry] Auto-detected archive platform: {parser.platform_name}")
                return parser.parse(zip_ref, file_list)
                
        # Default fallback parser (Instagram parser handles basic file formats)
        print("[ParserRegistry] Platform default fallback to InstagramParser")
        return InstagramParser().parse(zip_ref, file_list)

default_registry = ParserRegistry()
