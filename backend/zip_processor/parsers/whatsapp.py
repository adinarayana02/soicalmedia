import zipfile
import re
from typing import Dict, List, Any
from datetime import datetime
from zip_processor.parsers.base import BasePlatformParser

class WhatsAppParser(BasePlatformParser):
    @property
    def platform_name(self) -> str:
        return "whatsapp"

    def can_parse(self, file_list: List[str]) -> bool:
        lowered = [f.lower() for f in file_list]
        return any("_chat.txt" in f or "whatsapp chat" in f for f in lowered)

    def parse(self, zip_ref: zipfile.ZipFile, file_list: List[str]) -> Dict[str, Any]:
        data = {
            "platform": "whatsapp",
            "account_info": {"username": "WhatsApp User"},
            "posts": [],
            "stories": [],
            "reels": [],
            "comments": [],
            "liked_posts": [],
            "messages": [],
            "conversations": [],
            "followers": [],
            "following": [],
            "media": [],
            "saved_posts": [],
            "searches": [],
            "preferences": [],
            "metrics": {
                "total_messages_count": 0,
                "shared_links_count": 0,
                "total_likes": 0,
                "total_comments": 0
            }
        }
        
        pattern = re.compile(r'\[?(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)?)\]?\s*([^:]+):\s*(.*)')

        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.txt'):
                with zip_ref.open(file_info) as f:
                    lines = f.read().decode('utf-8', errors='ignore').splitlines()
                    for line in lines:
                        match = pattern.match(line)
                        if match:
                            dt_str, sender, msg = match.groups()
                            data["metrics"]["total_messages_count"] += 1
                            data["messages"].append({
                                "contact_name": sender,
                                "sender_name": sender,
                                "message_text": msg,
                                "message_type": "received",
                                "timestamp": datetime.utcnow()
                            })

        return data
