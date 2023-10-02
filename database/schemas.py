from pydantic import BaseModel
from datetime import date

class Account(BaseModel):
    username: str
    password: str
    recovery_email: str
    name: str
    date_of_birth: date
    gender: str
    mobile_no: str
    levelup_id: int
    account_url: str
    status: int

    class Config:
        from_attributes = True

class UserSession(BaseModel):
    username: str
    cookies: str
    user_agent: str

    class Config:
        from_attributes = True

class AccountInteraction(BaseModel):
    username: str
    interactions: str

    class Config:
        from_attributes = True

class BotConfigs(BaseModel):
    submit_delay: int
    page_refresh: int
    cooldown: int
    prohibited_words: str
    prompt: str
    prescript: str
    postscript: str
    max_interactions: int
    openai_api_key: str

    class Config:
        from_attributes = True

class QuestionPost(BaseModel):
    url: str
    title: str
    status: int
    author: str
    respondent: Account

    class Config:
        from_attributes = True

class AnswerResponse(BaseModel):
    question_url: str
    type: str
    content: str
    postscript: str
    status: int
    username: str

    class Config:
        from_attributes = True

class AdminBase(BaseModel):
    username: str

class Admin(AdminBase):
    password: str

    class Config:
        from_attributes = True

class QuestionAnswerForm(BaseModel):
    question: str
    answer_1: str
    answer_2: str