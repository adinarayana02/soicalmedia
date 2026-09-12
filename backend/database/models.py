from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")
    uploads = relationship("Upload", back_populates="owner", cascade="all, delete-orphan")
    archives = relationship("Archive", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    reels = relationship("Reel", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="owner", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    followers = relationship("Follower", back_populates="user", cascade="all, delete-orphan")
    followings = relationship("Following", back_populates="user", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    searches = relationship("SearchHistory", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="user", cascade="all, delete-orphan")
    behaviors = relationship("Behavior", back_populates="user", cascade="all, delete-orphan")
    timelines = relationship("Timeline", back_populates="user", cascade="all, delete-orphan")
    
    # Backwards compatibility relationships
    analyses = relationship("AnalysisResult", back_populates="owner", cascade="all, delete-orphan")
    urls = relationship("UrlData", back_populates="owner", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="owner", cascade="all, delete-orphan")
    account_profile = relationship("AccountProfile", back_populates="owner", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("Preference", back_populates="owner", cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    username = Column(String, index=True)
    full_name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String, nullable=True)
    website = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    account_creation_date = Column(DateTime, nullable=True)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    privacy_status = Column(String, default="public")
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profiles")

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    file_name = Column(String, nullable=False)
    upload_type = Column(String, default="zip") # zip or media
    sha256_hash = Column(String, index=True, nullable=True)
    file_size_bytes = Column(Integer, default=0)
    status = Column(String, default="completed", index=True)
    progress_percentage = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="uploads")
    archives = relationship("Archive", back_populates="upload", cascade="all, delete-orphan")

class Archive(Base):
    __tablename__ = "archives"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, index=True, nullable=False)
    extracted_files_count = Column(Integer, default=0)
    total_uncompressed_size = Column(Integer, default=0)
    detected_format = Column(String, default="json")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    upload = relationship("Upload", back_populates="archives")
    user = relationship("User", back_populates="archives")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    post_type = Column(String, default="post") # post, photo, video
    caption = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    posted_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="posts")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="SET NULL"), nullable=True, index=True)
    platform = Column(String, default="instagram", index=True)
    comment_text = Column(Text, nullable=False)
    target_author = Column(String, nullable=True)
    commented_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="comments")

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    media_url = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    views_count = Column(Integer, default=0)
    posted_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="stories")

class Reel(Base):
    __tablename__ = "reels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    title = Column(String, nullable=True)
    caption = Column(Text, nullable=True)
    audio_track = Column(String, nullable=True)
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    is_saved = Column(Boolean, default=False)
    posted_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reels")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    contact_name = Column(String, index=True, nullable=False)
    messages_count = Column(Integer, default=0)
    last_message_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    platform = Column(String, default="instagram", index=True)
    contact_name = Column(String, index=True)
    sender_name = Column(String, nullable=True)
    message_text = Column(Text)
    message_type = Column(String, default="received") # sent/received
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")

class Follower(Base):
    __tablename__ = "followers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    follower_username = Column(String, index=True, nullable=False)
    followed_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="followers")

class Following(Base):
    __tablename__ = "followings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    following_username = Column(String, index=True, nullable=False)
    followed_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="followings")

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(Text, nullable=True)
    mime_type = Column(String, index=True)
    file_size_bytes = Column(Integer, default=0)
    media_category = Column(String, default="photo") # photo, video, audio
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="media")

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    target_type = Column(String, default="post") # post, story, comment
    target_content = Column(Text, nullable=True)
    liked_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="likes")

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    query = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="searches")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    engagement_rate = Column(Float, default=0.0)
    posting_frequency_per_week = Column(Float, default=0.0)
    messaging_frequency_per_day = Column(Float, default=0.0)
    most_active_day = Column(String, default="Sunday")
    most_active_hour = Column(Integer, default=12)
    sentiment_distribution = Column(JSON, nullable=True)
    language_distribution = Column(JSON, nullable=True)
    media_distribution = Column(JSON, nullable=True)
    activity_heatmap_matrix = Column(JSON, nullable=True)
    growth_analytics = Column(JSON, nullable=True)
    word_cloud_frequencies = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="analytics")

class Behavior(Base):
    __tablename__ = "behavior"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    wellbeing_score = Column(Float, default=100.0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default="Low", index=True)
    behavioral_instability = Column(Float, default=0.0)
    temporal_risk_index = Column(Float, default=0.0)
    distress_probability = Column(Float, default=0.0)
    insights = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="behaviors")

class Timeline(Base):
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    platform = Column(String, default="instagram", index=True)
    event_category = Column(String, index=True) # message, comment, like, search, post
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    icon = Column(String, default="📌")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="timelines")

# Backwards compatibility classes
class UrlData(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    url = Column(Text)
    platform = Column(String)
    content_type = Column(String)
    shared_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="urls")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    engagement_type = Column(String)
    platform = Column(String, nullable=True)
    text_content = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="interactions")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    wellbeing_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String)
    behavioral_instability = Column(Float, default=0.0)
    temporal_risk_index = Column(Float, default=0.0)
    distress_probability = Column(Float, default=0.0)
    total_activity_count = Column(Integer, default=0)
    sentiment = Column(String)
    emotions = Column(JSON)
    summary = Column(JSON)
    insights = Column(Text)
    recommendations = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    session_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="analyses")

class AccountProfile(Base):
    __tablename__ = "account_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    username = Column(String)
    full_name = Column(String, nullable=True)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    profile_photo = Column(String, nullable=True)
    creation_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="account_profile")

class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    topic = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="preferences")
