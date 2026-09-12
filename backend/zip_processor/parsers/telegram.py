import json
import zipfile
from typing import Dict, List, Any
from datetime import datetime
from zip_processor.parsers.base import BasePlatformParser

class TelegramParser(BasePlatformParser):
    @property
    def platform_name(self) -> str:
        return "telegram"

    def can_parse(self, file_list: List[str]) -> bool:
        lowered = [f.lower() for f in file_list]
        return any("result.json" in f or "chats" in f for f in lowered)

    def parse(self, zip_ref: zipfile.ZipFile, file_list: List[str]) -> Dict[str, Any]:
        data = {
            "platform": "telegram",
            "account_info": {"username": "Telegram User"},
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
        
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.json'):
                try:
                    with zip_ref.open(file_info) as f:
                        obj = json.load(f)
                        if isinstance(obj, dict) and "chats" in obj:
                            chats = obj["chats"].get("list", [])
                            for chat in chats:
                                name = chat.get("name", "Unknown Contact")
                                msgs = chat.get("messages", [])
                                for m in msgs:
                                    txt = m.get("text", "")
                                    if isinstance(txt, list):
                                        txt = "".join([t.get("text", "") if isinstance(t, dict) else str(t) for t in txt])
                                    if txt:
                                        data["metrics"]["total_messages_count"] += 1
                                        data["messages"].append({
                                            "contact_name": name,
                                            "sender_name": m.get("from", name),
                                            "message_text": txt,
                                            "message_type": "received",
                                            "timestamp": datetime.utcnow()
                                        })
                except Exception:
                    pass

        return data
