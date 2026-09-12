from abc import ABC, abstractmethod
from typing import Dict, List, Any
import zipfile

class BasePlatformParser(ABC):
    """
    Abstract Base Class for all Social Media Archive Parsers.
    Ensures modularity: new platforms (Instagram, WhatsApp, Telegram, Twitter, TikTok, etc.)
    can be added without altering the core pipeline.
    """
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Name of the platform handled by this parser."""
        pass

    @abstractmethod
    def can_parse(self, file_list: List[str]) -> bool:
        """
        Determines whether this parser can handle the provided archive structure.
        """
        pass

    @abstractmethod
    def parse(self, zip_ref: zipfile.ZipFile, file_list: List[str]) -> Dict[str, Any]:
        """
        Extracts, parses, and normalizes archive data into a standard schema dictionary.
        Returns:
            Dict containing normalized profile, posts, messages, interactions, media, etc.
        """
        pass
