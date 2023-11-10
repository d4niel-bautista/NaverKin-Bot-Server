from sqlalchemy import Column, ForeignKey, Integer, String, Date, Text
from sqlalchemy.orm import relationship

from .database import Base

class NaverAccount(Base):
    __tablename__ = "naver_accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True)
    password = Column(String(30), index=True)
    recovery_email = Column(String(255), index=True, default="")
    name = Column(String(255), index=True)
    date_of_birth = Column(Date, index=True)
    gender = Column(String(10), index=True)
    mobile_no = Column(String(20), index=True)
    levelup_id = Column(Integer, index=True)
    account_url = Column(String(255), index=True)
    status = Column(Integer, index=True)
    interactions = relationship("AccountInteraction", cascade="all, delete-orphan")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True)
    cookies = Column(Text, index=True, default="")
    user_agent = Column(String(255), index=True, default="")

class AccountInteraction(Base):
    __tablename__ = "account_interactions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), ForeignKey("naver_accounts.username"), unique=True, index=True, default="")
    interactions = Column(Text, index=True)

class BotConfigs(Base):
    __tablename__ = "bot_configs"

    id = Column(Integer, primary_key=True, index=True)
    submit_delay = Column(Integer, index=True, default=600)
    page_refresh = Column(Integer, index=True, default=600)
    answers_per_day = Column(Integer, index=True, default=20)
    cooldown = Column(Integer, index=True, default=86400)
    max_interactions = Column(Integer, index=True, default=1)

class NaverKinQuestionPost(Base):
    __tablename__ = "naverkin_question_posts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), index=True, unique=True, default="")
    title = Column(Text, index=True, default="")
    status = Column(Integer, index=True, default=0)
    author = Column(String(30), index=True, default="")
    respondent_id = Column(String(30), ForeignKey("naver_accounts.username"), index=True, default="")

    respondent = relationship("NaverAccount", uselist=False)

class NaverKinAnswerResponse(Base):
    __tablename__ = "naverkin_answer_responses"

    id = Column(Integer, primary_key=True, index=True)
    question_url = Column(String(255), ForeignKey("naverkin_question_posts.url"), index=True, default="")
    type = Column(String(32), index=True, default="")
    content = Column(Text, index=True, default="")
    postscript = Column(Text, index=True, default="")
    status = Column(Integer, index=True, default=0)
    username = Column(String(30), index=True)

class AdminLogin(Base):
    __tablename__ = "admin_login"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True)
    password = Column(String(30), index=True)

    def verify_password(self, password: str):
        return self.password == password

class PromptConfigs(Base):
    __tablename__ = "prompt_configs"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), unique=True, index=True, default="")
    query = Column(Text, index=True, default="")
    prompt = Column(Text, index=True, default="")
    prescript = Column(Text, index=True, default="")
    postscript = Column(Text, index=True, default="")
    prohibited_words = Column(Text, index=True, default="")
    openai_api_key = Column(Text, index=True, default="")