from pydantic import BaseModel
from datetime import date, datetime

class NaverAccountBase(BaseModel):
    username: str
    password: str
    levelup_id: int
    account_url: str
    status: int

    class Config:
        from_attributes = True

class NaverAccountCreate(NaverAccountBase):
    recovery_email: str
    name: str
    date_of_birth: date
    gender: str
    mobile_no: str
    registration_date: date
    level: str
    category: int
    verified: bool
    last_login: str

class NaverAccount(NaverAccountCreate):
    id: int

class UserSession(BaseModel):
    username: str
    cookies: str
    user_agent: str

    class Config:
        from_attributes = True

class AccountInteractionBase(BaseModel):
    username: str
    interactions: str

    class Config:
        from_attributes = True

class AccountInteraction(AccountInteractionBase):
    id: int

class BotConfigsBase(BaseModel):
    submit_delay: int

class BotConfigs(BotConfigsBase):
    id: int
    
    class Config:
        from_attributes = True

class BotConfigsStandalone(BotConfigs):
    page_refresh: int
    answers_per_day: str
    cooldown: int
    max_interactions: int

class QuestionPostCreate(BaseModel):
    url: str
    title: str
    status: int
    author: str
    respondent: str

    class Config:
        from_attributes = True

class QuestionPost(QuestionPostCreate):
    id: int

class AnswerResponseCreate(BaseModel):
    question_url: str
    type: str
    content: str
    postscript: str
    status: int
    username: str
    date_answered: datetime

    class Config:
        from_attributes = True

class AnswerResponse(AnswerResponseCreate):
    id: int

class AdminBase(BaseModel):
    username: str

class AdminCreate(AdminBase):
    password: str

    class Config:
        from_attributes = True

class Admin(AdminBase):
    id: int

    class Config:
        from_attributes = True

class QuestionAnswerFormBase(BaseModel):
    question: dict

class QuestionAnswerForm_1Q2A(QuestionAnswerFormBase):
    answer_advertisement: dict
    answer_exposure: dict

class QuestionAnswerForm_1Q1A(QuestionAnswerFormBase):
    answer_advertisement: dict

class PromptConfigs(BaseModel):
    id: int
    description: str
    query: str
    prompt: str
    prescript: str
    postscript: str
    prohibited_words: str
    openai_api_key: str

    class Config:
        from_attributes = True

class PromptConfigsUpdate(BaseModel):
    question: dict
    answer_advertisement: dict
    answer_exposure: dict
    prohibited_words: str

class CategoryBase(BaseModel):
    category: str

    class Config:
        from_attributes = True

class Category(CategoryBase):
    id: int

class LoginCreate(BaseModel):
    username: str
    ip_address: str
    login_timestamp: datetime

    class Config:
        from_attributes = True

class Login(LoginCreate):
    id: int