import json
import zipfile
import re
from typing import Dict, List, Any
from datetime import datetime
from zip_processor.parsers.base import BasePlatformParser

class InstagramParser(BasePlatformParser):
    @property
    def platform_name(self) -> str:
        return "instagram"

    def can_parse(self, file_list: List[str]) -> bool:
        lowered = [f.lower() for f in file_list]
        return any(
            "personal_information" in f or 
            "your_instagram_activity" in f or 
            "messages/inbox" in f or 
            "followers_and_following" in f
            for f in lowered
        )

    def parse(self, zip_ref: zipfile.ZipFile, file_list: List[str]) -> Dict[str, Any]:
        data = {
            "platform": "instagram",
            "account_info": {},
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
            filename = file_info.filename
            if filename.endswith('/') or file_info.is_dir():
                continue
                
            path_lower = filename.lower()
            if not (filename.endswith('.json') or filename.endswith('.html') or filename.endswith('.txt')):
                continue
                
            try:
                with zip_ref.open(file_info) as f:
                    raw_bytes = f.read()
                    try:
                        content_str = raw_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        content_str = raw_bytes.decode('latin1', errors='ignore')
                        
                    if filename.endswith('.json'):
                        try:
                            json_obj = json.loads(content_str)
                            self._parse_json_file(filename, path_lower, json_obj, data)
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                print(f"Skipping {filename}: {e}")
                
        return data

    def _parse_json_file(self, filename: str, path_lower: str, json_obj: Any, master: Dict[str, Any]):
        if "personal_information" in path_lower or "profile" in path_lower:
            self._extract_profile(json_obj, master)
        elif "messages" in path_lower or "inbox" in path_lower:
            self._extract_messages(json_obj, master)
        elif "comments" in path_lower:
            self._extract_comments(json_obj, master)
        elif "likes" in path_lower:
            self._extract_likes(json_obj, master)
        elif "saved" in path_lower:
            self._extract_saved(json_obj, master)
        elif "recent_searches" in path_lower or "search" in path_lower:
            self._extract_searches(json_obj, master)
        elif "preferences" in path_lower or "topic" in path_lower:
            self._extract_preferences(json_obj, master)
        elif "followers" in path_lower or "following" in path_lower:
            self._extract_connections(json_obj, master, path_lower)

    def _extract_profile(self, json_obj: Any, master: Dict[str, Any]):
        info = master["account_info"]
        items = json_obj if isinstance(json_obj, list) else [json_obj]
        if isinstance(json_obj, dict):
            for k in ["profile_user", "account_details", "personal_information"]:
                if k in json_obj and isinstance(json_obj[k], list):
                    items = json_obj[k]
                    break

        for item in items:
            if not isinstance(item, dict): continue
            smap = item.get("string_map_data", item)
            for k, v in smap.items():
                val = v.get("value") if isinstance(v, dict) else str(v)
                if not val: continue
                kl = k.lower()
                if "username" in kl: info["username"] = str(val)
                elif "name" in kl and "user" not in kl: info["full_name"] = str(val)
                elif "bio" in kl: info["bio"] = str(val)
                elif "pic" in kl or "photo" in kl: info["profile_photo"] = str(val)

    def _extract_messages(self, json_obj: Any, master: Dict[str, Any]):
        if not isinstance(json_obj, dict): return
        msgs = json_obj.get("messages", [])
        participants = json_obj.get("participants", [])
        contact = "Unknown"
        if participants and isinstance(participants, list):
            p0 = participants[0]
            contact = p0.get("name", "Unknown") if isinstance(p0, dict) else str(p0)
            
        master["conversations"].append({
            "contact_name": contact,
            "messages_count": len(msgs)
        })
        
        for m in msgs:
            if not isinstance(m, dict): continue
            master["metrics"]["total_messages_count"] += 1
            txt = m.get("content", m.get("text", ""))
            sender = m.get("sender_name", contact)
            ts_ms = m.get("timestamp_ms", 0)
            ts = datetime.fromtimestamp(ts_ms / 1000.0) if ts_ms > 0 else datetime.utcnow()
            
            m_type = "sent" if sender and "user" in sender.lower() else "received"
            if txt:
                master["messages"].append({
                    "contact_name": contact,
                    "sender_name": sender,
                    "message_text": txt,
                    "message_type": m_type,
                    "timestamp": ts
                })

    def _extract_comments(self, json_obj: Any, master: Dict[str, Any]):
        items = json_obj if isinstance(json_obj, list) else [json_obj]
        for it in items:
            txt = self._find_str(it)
            if txt:
                master["comments"].append({"text_content": txt, "timestamp": datetime.utcnow()})
                master["metrics"]["total_comments"] += 1

    def _extract_likes(self, json_obj: Any, master: Dict[str, Any]):
        items = json_obj if isinstance(json_obj, list) else [json_obj]
        for it in items:
            txt = self._find_str(it) or "Liked a post/story"
            master["liked_posts"].append({"engagement_type": "like", "text_content": txt, "timestamp": datetime.utcnow()})
            master["metrics"]["total_likes"] += 1

    def _extract_saved(self, json_obj: Any, master: Dict[str, Any]):
        items = json_obj if isinstance(json_obj, list) else [json_obj]
        for it in items:
            txt = self._find_str(it) or "Saved post"
            master["saved_posts"].append({"text_content": txt, "timestamp": datetime.utcnow()})

    def _extract_searches(self, json_obj: Any, master: Dict[str, Any]):
        items = json_obj if isinstance(json_obj, list) else [json_obj]
        for it in items:
            q = self._find_str(it)
            if q:
                master["searches"].append({"query": q, "timestamp": datetime.utcnow()})

    def _extract_preferences(self, json_obj: Any, master: Dict[str, Any]):
        items = json_obj if isinstance(json_obj, list) else [json_obj]
        for it in items:
            t = self._find_str(it)
            if t:
                master["preferences"].append({"topic": t})

    def _extract_connections(self, json_obj: Any, master: Dict[str, Any], path_lower: str):
        items = json_obj if isinstance(json_obj, list) else [json_obj]
        target = master["followers"] if "follower" in path_lower else master["following"]
        for it in items:
            u = self._find_str(it)
            if u:
                target.append({"username": u, "timestamp": datetime.utcnow()})

    def _find_str(self, obj: Any) -> str:
        if isinstance(obj, str): return obj
        if isinstance(obj, dict):
            for k in ["value", "text", "comment", "query", "title", "string"]:
                if k in obj and isinstance(obj[k], str):
                    return obj[k]
            for v in obj.values():
                res = self._find_str(v)
                if res: return res
        if isinstance(obj, list) and obj:
            return self._find_str(obj[0])
        return ""
