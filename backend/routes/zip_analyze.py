from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import tempfile
import os
import shutil
import json
import hashlib
from datetime import datetime

from database.db import get_db
from database.models import (
    User, Profile, Upload, Archive, Post, Comment, Story, Reel, Message, Conversation,
    Follower, Following, Media, Like, SearchHistory, Notification, Analytics, Behavior, Timeline,
    AnalysisResult, AccountProfile, Preference, UrlData, Interaction
)
from routes.auth import get_current_user
from zip_processor.extractor import process_social_zip
from services.analytics_engine import default_analytics_engine
from agents.observer_agent import ObserverAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.advisor_agent import AdvisorAgent

router = APIRouter()

observer_agent = ObserverAgent()
evaluator_agent = EvaluatorAgent()
advisor_agent = AdvisorAgent()

@router.post("/api/analyze-zip")
async def analyze_zip(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a valid ZIP archive.")
        
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, file.filename)
    
    try:
        content_bytes = await file.read()
        file_size = len(content_bytes)
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # Record Upload
        new_upload = Upload(
            user_id=current_user.id,
            file_name=file.filename,
            upload_type="zip",
            sha256_hash=sha256_hash,
            file_size_bytes=file_size,
            status="completed",
            progress_percentage=100.0
        )
        db.add(new_upload)
        db.commit()
        db.refresh(new_upload)
        
        with open(zip_path, "wb") as f:
            f.write(content_bytes)
            
        # 1. Execute Direct ZIP Extraction Pipeline
        extracted = process_social_zip(zip_path)
        platform_name = extracted.get("platform", "instagram")
        
        # 2. Clear old platform data for fresh state
        db.query(Follower).filter(Follower.user_id == current_user.id).delete()
        db.query(Following).filter(Following.user_id == current_user.id).delete()
        db.query(Post).filter(Post.user_id == current_user.id).delete()
        db.query(Message).filter(Message.user_id == current_user.id).delete()
        db.query(Conversation).filter(Conversation.user_id == current_user.id).delete()
        db.query(Comment).filter(Comment.user_id == current_user.id).delete()
        db.query(Like).filter(Like.user_id == current_user.id).delete()
        db.query(SearchHistory).filter(SearchHistory.user_id == current_user.id).delete()
        db.query(Timeline).filter(Timeline.user_id == current_user.id).delete()

        # 3. Record Archive Metadata
        new_archive = Archive(
            upload_id=new_upload.id,
            user_id=current_user.id,
            platform=platform_name,
            extracted_files_count=len(extracted.get("messages", [])) + len(extracted.get("searches", [])),
            total_uncompressed_size=file_size,
            detected_format="json"
        )
        db.add(new_archive)
        
        # 4. Store Profile & Account Info
        acc = extracted.get("account_info", {})
        uname = acc.get("username") or current_user.name.lower().replace(" ", "_")
        fname = acc.get("full_name") or current_user.name
        bio_str = acc.get("bio") or "Social Media Archive User"
        pic_str = acc.get("profile_photo")

        db.query(Profile).filter(Profile.user_id == current_user.id).delete()
        db.add(Profile(
            user_id=current_user.id,
            platform=platform_name,
            username=uname,
            full_name=fname,
            bio=bio_str,
            profile_picture=pic_str,
            privacy_status="public"
        ))
        
        db.query(AccountProfile).filter(AccountProfile.user_id == current_user.id).delete()
        db.add(AccountProfile(
            user_id=current_user.id,
            username=uname,
            full_name=fname,
            bio=bio_str,
            profile_photo=pic_str
        ))
        
        # 5. Store Posts & Reels
        for post in extracted.get("posts", []):
            cap = post.get("caption", "Post/Reel media content")
            ts = post.get("timestamp", datetime.utcnow())
            db.add(Post(user_id=current_user.id, platform=platform_name, caption=cap, posted_at=ts))

        # 6. Store Messages & Conversations
        timeline_events = []
        conversation_map = {}
        for msg in extracted.get("messages", []):
            contact = msg.get("contact_name", "Unknown Contact")
            txt = msg.get("message_text", "")
            ts = msg.get("timestamp", datetime.utcnow())
            mtype = msg.get("message_type", "received")
            
            if contact not in conversation_map:
                conv = Conversation(
                    user_id=current_user.id,
                    platform=platform_name,
                    contact_name=contact,
                    messages_count=1,
                    last_message_at=ts
                )
                db.add(conv)
                db.flush()
                conversation_map[contact] = conv.id
            else:
                conv_id = conversation_map[contact]
                
            db.add(Message(
                user_id=current_user.id,
                conversation_id=conversation_map[contact],
                platform=platform_name,
                contact_name=contact,
                sender_name=msg.get("sender_name", contact),
                message_text=txt,
                message_type=mtype,
                timestamp=ts
            ))
            
            if txt:
                timeline_events.append({"text": txt, "timestamp": ts, "type": "message", "source": platform_name})
                db.add(Timeline(
                    user_id=current_user.id,
                    platform=platform_name,
                    event_category="message",
                    title=f"Message with {contact}",
                    content=txt[:250],
                    icon="💬",
                    timestamp=ts
                ))

        # 7. Store Comments, Likes, Saved
        for comment in extracted.get("comments", []):
            txt = comment.get("text_content", "")
            ts = comment.get("timestamp", datetime.utcnow())
            db.add(Comment(user_id=current_user.id, platform=platform_name, comment_text=txt, commented_at=ts))
            db.add(Interaction(user_id=current_user.id, engagement_type="comment", text_content=txt, platform=platform_name, timestamp=ts))

        for like in extracted.get("liked_posts", []):
            txt = like.get("text_content", "Liked post")
            ts = like.get("timestamp", datetime.utcnow())
            db.add(Like(user_id=current_user.id, platform=platform_name, target_content=txt, liked_at=ts))
            db.add(Interaction(user_id=current_user.id, engagement_type="like", text_content=txt, platform=platform_name, timestamp=ts))

        # 8. Store Searches & Preferences
        for search in extracted.get("searches", []):
            q = search.get("query", "")
            ts = search.get("timestamp", datetime.utcnow())
            db.add(SearchHistory(user_id=current_user.id, platform=platform_name, query=q, timestamp=ts))

        for pref in extracted.get("preferences", []):
            t = pref.get("topic", "")
            db.add(Preference(user_id=current_user.id, topic=t))

        # 9. Store Followers / Following
        for follower in extracted.get("followers", []):
            u = follower.get("username", "")
            if u:
                db.add(Follower(user_id=current_user.id, platform=platform_name, follower_username=u))

        for following in extracted.get("following", []):
            u = following.get("username", "")
            if u:
                db.add(Following(user_id=current_user.id, platform=platform_name, following_username=u))

        # 10. Compute Analytics Engine Metrics
        analytics_res = default_analytics_engine.compute_analytics(extracted)
        db.query(Analytics).filter(Analytics.user_id == current_user.id).delete()
        growth_trend = analytics_res.get("growth_analytics") or analytics_res.get("monthly_activity", {})
        db.add(Analytics(
            user_id=current_user.id,
            engagement_rate=analytics_res.get("engagement_rate", 0.0),
            most_active_day=analytics_res.get("most_active_day", "Sunday"),
            most_active_hour=analytics_res.get("most_active_hour", 12),
            media_distribution=analytics_res.get("media_distribution", {}),
            language_distribution=analytics_res.get("language_distribution", {}),
            activity_heatmap_matrix=analytics_res.get("heatmap_matrix", []),
            growth_analytics=growth_trend,
            word_cloud_frequencies=analytics_res.get("word_cloud", [])
        ))

        # 11. AI Agents Pipeline
        recent_events = sorted(timeline_events, key=lambda x: x["timestamp"])[:100]
        observed = observer_agent.process_timeline(recent_events)
        eval_metrics = evaluator_agent.evaluate_session(observed)
        advice = advisor_agent.generate_advice(eval_metrics)

        db.query(Behavior).filter(Behavior.user_id == current_user.id).delete()
        db.add(Behavior(
            user_id=current_user.id,
            wellbeing_score=advice.get("wellbeing_score", 100.0),
            risk_score=advice.get("risk_score", 0.0),
            risk_level=advice.get("risk_level", "Low"),
            behavioral_instability=eval_metrics.get("behavioral_instability", 0.0),
            temporal_risk_index=eval_metrics.get("temporal_risk_index", 0.0),
            distress_probability=eval_metrics.get("distress_probability", 0.0),
            insights=advice.get("insights", "{}"),
            recommendations=advice.get("recommendations", ""),
            evidence=advice.get("evidence", ""),
            confidence=advice.get("confidence", 1.0)
        ))

        db.commit()

        return {
            "status": "success",
            "message": "ZIP Archive parsed and stored successfully.",
            "summary": extracted.get("metrics", {}),
            "analytics": analytics_res,
            "behavior": advice
        }

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
