from database import models, database, schemas
from sqlalchemy.orm import Session
from fastapi import HTTPException

def create_database():
    models.Base.metadata.create_all(bind=database.engine)

async def get_admin_account(db: Session, filters: list=[], fetch_one: bool=True, schema_validate: bool=True):
    if schema_validate:
        return schemas.Admin.model_validate(db.query(models.AdminLogin).filter(*filters).first())\
                if fetch_one else\
                list(map(schemas.Admin.model_validate, db.query(models.AdminLogin).filter(*filters).all()))
    else:
        return db.query(models.AdminLogin).filter(*filters).first()\
                if fetch_one else\
                db.query(models.AdminLogin).filter(*filters).all()

async def get_naver_account(db: Session, filters: list=[], fetch_one: bool=True, schema: schemas.BaseModel = schemas.NaverAccountBase):
    return schema.model_validate(db.query(models.NaverAccount).filter(*filters).first())\
            if fetch_one else\
            list(map(schema.model_validate, db.query(models.NaverAccount).filter(*filters).all()))

async def get_account_interactions(db: Session, filters: list=[], fetch_one: bool=True):
    return schemas.AccountInteraction.model_validate(db.query(models.AccountInteraction).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.AccountInteraction.model_validate, db.query(models.AccountInteraction).filter(*filters).all()))

async def get_user_session(db: Session, filters: list=[], fetch_one: bool=True):
    return schemas.UserSession.model_validate(db.query(models.UserSession).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.UserSession.model_validate, db.query(models.UserSession).filter(*filters).all()))

async def get_bot_configs(db: Session, filters: list=[], fetch_one: bool=True):
    return schemas.BotConfigs.model_validate(db.query(models.BotConfigs).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.BotConfigs.model_validate, db.query(models.BotConfigs).filter(*filters).all()))

async def get_prompt_configs(db: Session, filters: list=[], fetch_one: bool=True):
    return schemas.PromptConfigs.model_validate(db.query(models.PromptConfigs).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.PromptConfigs.model_validate, db.query(models.PromptConfigs).filter(*filters).all()))

async def add_naver_account(account: schemas.NaverAccountCreate, db: Session):
    naver_account = models.NaverAccount(**account.model_dump())
    db.add(naver_account)
    try:
        db.commit()
        db.refresh(naver_account)
        return schemas.NaverAccountBase.model_validate(naver_account)
    except:
        db.rollback()

async def add_user_session(account: schemas.NaverAccountCreate, db: Session):
    user_session = models.UserSession(username=account.model_dump()['username'], cookies='', user_agent='')
    db.add(user_session)
    try:
        db.commit()
        db.refresh(user_session)
        return user_session
    except:
        db.rollback()

async def add_account_interactions(account: schemas.NaverAccountCreate, db: Session):
    account_interactions = models.AccountInteraction(username=account.model_dump()['username'], interactions='')
    db.add(account_interactions)
    try:
        db.commit()
        db.refresh(account_interactions)
        return account_interactions
    except:
        db.rollback()

async def update(model: models.Base, data: dict, filters: dict, db: Session):
    try:
        db.query(model).filter_by(**filters).update(data)
        db.commit()
        return f'UPDATED {model.__tablename__}: {", ".join([i for i in data])} SUCCESSFULLY'
    except Exception as e:
        print(e)
        return "UPDATE FAILED"