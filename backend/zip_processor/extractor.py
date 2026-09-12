import json
import os
import zipfile
import shutil
import tempfile
import re
from typing import Dict, List, Any
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    import lxml
except ImportError:
    pass

def process_social_zip(zip_path: str) -> Dict[str, Any]:
    extracted_data = {
        "platform": "instagram",
        "account_info": {},
        "comments": [],
        "liked_posts": [],
        "messages": [],
        "posts": [],
        "urls": [],
        "saved_posts": [],
        "searches": [],
        "preferences": [],
        "followers": [],
        "following": [],
        "contacts": [],
        "metrics": {
            "total_messages_count": 0,
            "shared_links_count": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_saved": 0
        }
    }
    
    print(f"Opening ZIP: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        print(f"ZIP contains {len(file_list)} files.")
        
        for file_info in zip_ref.infolist():
            filename = file_info.filename
            if filename.endswith('/') or file_info.is_dir():
                continue
                
            path_lower = filename.lower()
            if filename.endswith('.json') or filename.endswith('.html') or filename.endswith('.txt'):
                try:
                    with zip_ref.open(file_info) as f:
                        content_bytes = f.read()
                        try:
                            content_str = content_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            content_str = content_bytes.decode('latin1', errors='ignore')
                            
                        base_name = os.path.basename(filename)
                        
                        if filename.endswith('.json'):
                            try:
                                data = json.loads(content_str)
                                parse_and_merge(base_name, filename, data, extracted_data, 'json')
                            except json.JSONDecodeError:
                                pass
                        elif filename.endswith('.html'):
                            parse_html(base_name, filename, content_str, extracted_data)
                        elif filename.endswith('.txt'):
                            parse_txt(base_name, filename, content_str, extracted_data)
                except Exception as e:
                    print(f"Skipping {filename} due to error: {e}")
                    
    return extracted_data

# HTML Parser Logic
def parse_html(filename: str, filepath: str, html_content: str, master_dict: Dict[str, Any]):
    try:
        soup = BeautifulSoup(html_content, 'lxml')
    except:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except:
            return
        
    path_lower = filepath.lower()
    fname = filename.lower()
    
    if 'personal_information' in path_lower or 'profile' in fname:
        username_el = soup.find('h1') or soup.find('h2') or soup.find(class_='_aamv')
        if username_el and not master_dict["account_info"].get("username"):
            master_dict["account_info"]["username"] = username_el.text.strip()
            
        img = soup.find('img')
        if img and img.get('src') and not master_dict["account_info"].get("profile_photo"):
            master_dict["account_info"]["profile_photo"] = img['src']
            
    if 'messages' in path_lower or 'inbox' in path_lower:
        contact_name = "Unknown"
        parts = filepath.split('/')
        for part in parts:
            if len(part) > 2 and part not in ['messages', 'inbox', 'json', 'your_instagram_activity']:
                contact_name = part.replace('_', ' ').strip()
                if contact_name and len(contact_name) > 2:
                    break
        
        message_divs = soup.find_all(['div', 'span'], class_=['_a6-i', 'message', 'pam', '_a6-o', '_a6-p', '_a6-q'])
        if not message_divs:
            message_divs = soup.find_all('div')
        
        last_text = ""
        for div in message_divs:
            sender = ""
            for cls in ['_a708', 'sender', 'name', '_a6-h', '_a6-i', '_a6-j']:
                possible = div.find(class_=cls)
                if possible:
                    sender = possible.get_text(separator=' ', strip=True)
                    if sender: break
            
            t = div.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in t.split('\n') if line.strip()]
            for line in lines:
                if 2 < len(line) < 2000 and line != last_text:
                    if any(x in line.lower() for x in ['liked a message', 'sent a message', 'shared a']):
                        continue
                    last_text = line
                    msg_type = "received" if sender and sender.lower() == contact_name.lower() else "sent"
                    master_dict["messages"].append({
                        "contact_name": contact_name,
                        "sender_name": sender or contact_name,
                        "message_text": line,
                        "message_type": msg_type,
                        "timestamp": datetime.utcnow()
                    })
                    master_dict["metrics"]["total_messages_count"] += 1

    if 'comments' in path_lower:
        comment_els = soup.find_all(['div', 'li'], class_=['_a6-i', 'comment'])
        for el in comment_els:
            t = el.get_text(separator=" ", strip=True)
            if t:
                master_dict["comments"].append({"text_content": t, "timestamp": datetime.utcnow(), "platform": "instagram"})
                master_dict["metrics"]["total_comments"] += 1

    if 'likes' in path_lower or 'liked' in path_lower:
        like_els = soup.find_all(['div', 'li', 'a'])
        for el in like_els:
            t = el.get_text(separator=" ", strip=True)
            if "liked" in t.lower() or "like" in t.lower():
                master_dict["liked_posts"].append({"text_content": t, "timestamp": datetime.utcnow(), "platform": "instagram"})
                master_dict["metrics"]["total_likes"] += 1

    if 'search' in path_lower:
        search_els = soup.find_all(['div', 'span', 'a'])
        for el in search_els:
            t = el.get_text(separator=" ", strip=True)
            if 2 < len(t) < 100:
                master_dict["searches"].append({"query": t, "timestamp": datetime.utcnow()})

# TXT Parser Logic
def parse_txt(filename: str, filepath: str, text: str, master_dict: Dict[str, Any]):
    path_lower = filepath.lower()
    if 'search' in path_lower:
        for line in text.split('\n'):
            line = line.strip()
            if len(line) > 2 and len(line) < 100:
                master_dict["searches"].append({"query": line, "timestamp": datetime.utcnow()})

# Core JSON Dispatcher
def parse_and_merge(filename: str, filepath: str, data: Any, master_dict: Dict[str, Any], fmt: str):
    path_lower = filepath.lower()

    if 'personal_information' in path_lower or 'account_details' in path_lower or 'profile' in path_lower:
        _parse_profile(data, master_dict)
        return

    if 'following' in filename.lower() or 'follower' in filename.lower() or 'connections' in path_lower:
        _parse_connections(data, master_dict, path_lower)
        return

    if 'posts' in path_lower or 'stories' in path_lower or 'reels' in path_lower or 'content' in path_lower:
        _parse_posts(data, master_dict)
        return

    if 'recent_searches' in path_lower or 'search' in path_lower:
        _parse_searches(data, master_dict)
        return

    if 'preferences' in path_lower or 'topic' in path_lower:
        _parse_preferences(data, master_dict)
        return

    if 'comments' in path_lower:
        _parse_interactions(data, master_dict, "comments", "comment")
        return

    if ('likes' in path_lower or 'liked' in path_lower) and 'story' not in path_lower:
        _parse_interactions(data, master_dict, "liked_posts", "like")
        return

    if 'saved' in path_lower:
        _parse_interactions(data, master_dict, "saved_posts", "saved")
        return

    if 'messages' in path_lower or 'inbox' in path_lower:
        _parse_messages(data, master_dict)
        return

def _parse_profile(data: Any, master_dict: Dict[str, Any]):
    info = master_dict["account_info"]
    items = []
    if isinstance(data, dict):
        for k in ["profile_user", "account_details", "personal_information", "profile"]:
            if k in data:
                v = data[k]
                items = v if isinstance(v, list) else [v]
                break
        if not items:
            items = [data]
    elif isinstance(data, list):
        items = data

    for block in items:
        if not isinstance(block, dict): continue
        smap = block.get("string_map_data", block)
        if isinstance(smap, dict):
            for k, v in smap.items():
                val = ""
                if isinstance(v, dict) and "value" in v:
                    val = str(v["value"])
                elif isinstance(v, (str, int, float)):
                    val = str(v)
                
                if not val: continue
                kl = k.lower()
                if "username" in kl and not info.get("username"):
                    info["username"] = val
                elif ("name" in kl and "user" not in kl) or "full_name" in kl:
                    info["full_name"] = val
                elif "bio" in kl:
                    info["bio"] = val
                elif "photo" in kl or "pic" in kl or "avatar" in kl:
                    info["profile_photo"] = val

def _parse_connections(data: Any, master_dict: Dict[str, Any], path_lower: str):
    filename = os.path.basename(path_lower)
    if "following" in filename or (isinstance(data, dict) and "relationships_following" in data):
        rel_type = "following"
    elif "follower" in filename or (isinstance(data, dict) and "relationships_followers" in data):
        rel_type = "follower"
    else:
        rel_type = "following" if "following" in path_lower else "follower"

    target_list = master_dict["following"] if rel_type == "following" else master_dict["followers"]

    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for k in ["relationships_followers", "relationships_following", "followers", "following"]:
            if k in data and isinstance(data[k], list):
                items = data[k]
                break
        if not items:
            for v in data.values():
                if isinstance(v, list):
                    items = v
                    break

    for item in items:
        username = ""
        ts = datetime.utcnow()
        if isinstance(item, dict):
            if "string_list_data" in item and isinstance(item["string_list_data"], list):
                for sld in item["string_list_data"]:
                    if isinstance(sld, dict):
                        username = sld.get("value") or sld.get("name") or ""
                        if not username and "href" in sld:
                            username = sld["href"].split("/")[-1]
                        if "timestamp" in sld:
                            ts = datetime.fromtimestamp(sld["timestamp"])
                        if username: break
            if not username:
                username = item.get("title", item.get("username", item.get("value", "")))
        elif isinstance(item, str):
            username = item

        clean_u = _clean_string(username)
        if clean_u and len(clean_u) > 1:
            target_list.append({"username": clean_u, "timestamp": ts})
            master_dict["contacts"].append({"name": clean_u, "relationship": rel_type})

def _parse_posts(data: Any, master_dict: Dict[str, Any]):
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for k in ["photos", "videos", "stories", "reels"]:
            if k in data and isinstance(data[k], list):
                items.extend(data[k])
        if not items:
            for v in data.values():
                if isinstance(v, list):
                    items.extend(v)

    for item in items:
        if not isinstance(item, dict): continue
        caption = ""
        ts = datetime.utcnow()

        if "media" in item and isinstance(item["media"], list):
            for m in item["media"]:
                if isinstance(m, dict):
                    caption = m.get("title", m.get("caption", ""))
                    if "creation_timestamp" in m:
                        ts = datetime.fromtimestamp(m["creation_timestamp"])
                    elif "timestamp" in m:
                        ts = datetime.fromtimestamp(m["timestamp"])
        else:
            caption = item.get("title", item.get("caption", ""))
            ts = _extract_timestamp(item)

        master_dict["posts"].append({
            "caption": _clean_string(caption) or "Post/Reel media content",
            "timestamp": ts
        })

def _parse_searches(data: Any, master_dict: Dict[str, Any]):
    items = _extract_list(data)
    for item in items:
        text = _clean_string(_find_text_value(item))
        if text and len(text) > 1:
            ts = _extract_timestamp(item)
            master_dict["searches"].append({"query": text, "timestamp": ts})

def _parse_preferences(data: Any, master_dict: Dict[str, Any]):
    items = _extract_list(data)
    for item in items:
        text = _clean_string(_find_text_value(item))
        if text:
            text = re.sub(r'http[s]?://[^\s]+', '', text).strip()
            if text and len(text) < 60:
                master_dict["preferences"].append({"topic": text})

def _parse_messages(data: Any, master_dict: Dict[str, Any]):
    if isinstance(data, dict):
        messages = data.get("messages", [])
        participants = data.get("participants", [])
        contact_name = "Unknown"
        if participants and isinstance(participants, list):
            for p in participants:
                if isinstance(p, dict) and "name" in p:
                    contact_name = _clean_string(p["name"])
                    break
                elif isinstance(p, str):
                    contact_name = _clean_string(p)
                    break

        for msg in messages:
            if not isinstance(msg, dict): continue
            master_dict["metrics"]["total_messages_count"] += 1
            text = _clean_string(msg.get("content", msg.get("text", "")))
            sender = _clean_string(msg.get("sender_name", ""))
            ts = _extract_timestamp(msg)
            msg_type = "received" if sender and sender == contact_name else "sent"
            
            if text:
                master_dict["messages"].append({
                    "contact_name": contact_name,
                    "sender_name": sender,
                    "message_text": text,
                    "message_type": msg_type,
                    "timestamp": ts
                })

def _parse_interactions(data: Any, master_dict: Dict[str, Any], category: str, interaction_type: str):
    items = _extract_list(data)
    for item in items:
        text = _clean_string(_find_text_value(item)) or "Interacted post"
        ts = _extract_timestamp(item)
        master_dict[category].append({
            "engagement_type": interaction_type,
            "text_content": text,
            "timestamp": ts,
            "platform": "instagram"
        })
        if interaction_type == "like": master_dict["metrics"]["total_likes"] += 1
        elif interaction_type == "comment": master_dict["metrics"]["total_comments"] += 1
        elif interaction_type == "saved": master_dict["metrics"]["total_saved"] += 1

def _extract_list(data: Any) -> List[Any]:
    if isinstance(data, list): return data
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list): return v
    return []

def _clean_string(raw: Any) -> str:
    if not raw: return ""
    try:
        if isinstance(raw, str):
            try:
                raw = raw.encode('latin1').decode('utf-8')
            except:
                pass
            return re.sub(r'<[^>]+>', '', raw).strip()
        return str(raw).strip()
    except:
        return ""

def _find_text_value(item: Any, depth: int = 0) -> str:
    if depth > 5: return ""
    if isinstance(item, str): return item
    if isinstance(item, dict):
        for key in ["string_map_data", "string_list_data"]:
            if key in item and isinstance(item[key], (dict, list)):
                vals = item[key].values() if isinstance(item[key], dict) else item[key]
                for v2 in vals:
                    if isinstance(v2, dict) and ("value" in v2 or "name" in v2):
                        return str(v2.get("value") or v2.get("name"))
        for key in ["text", "title", "comment", "query", "value", "content", "name"]:
            if key in item and isinstance(item[key], str):
                return item[key]
        for v in item.values():
            res = _find_text_value(v, depth+1)
            if res: return res
    if isinstance(item, list) and item:
        return _find_text_value(item[0], depth+1)
    return ""

def _extract_timestamp(item: Any) -> datetime:
    if isinstance(item, dict):
        for key in ["timestamp", "timestamp_ms", "creation_timestamp"]:
            if key in item:
                val = item[key]
                if isinstance(val, (int, float)):
                    if val > 1e11: return datetime.fromtimestamp(val/1000.0)
                    return datetime.fromtimestamp(val)
    return datetime.utcnow()
