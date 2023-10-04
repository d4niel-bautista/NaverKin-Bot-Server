from database import models, database, schemas
from sqlalchemy.orm import Session

def create_database():
    models.Base.metadata.create_all(bind=database.engine)

async def get_naver_account(filters: list = [], db: Session=next(database.get_db_conn()), fetch_one: bool=True):
    return schemas.NaverAccount.model_validate(db.query(models.NaverAccount).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.NaverAccount.model_validate, db.query(models.NaverAccount).filter(*filters).all()))

async def get_account_interactions(filters: list=[], db: Session=next(database.get_db_conn()), fetch_one: bool=True):
    return schemas.AccountInteraction.model_validate(db.query(models.AccountInteraction).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.AccountInteraction.model_validate, db.query(models.AccountInteraction).filter(*filters).all()))

async def get_user_session(filters: list=[], db: Session=next(database.get_db_conn()), fetch_one: bool=True):
    return schemas.UserSession.model_validate(db.query(models.UserSession).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.UserSession.model_validate, db.query(models.UserSession).filter(*filters).all()))

async def get_bot_configs(filters: list=[], db: Session=next(database.get_db_conn()), fetch_one: bool=True):
    return schemas.BotConfigs.model_validate(db.query(models.BotConfigs).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.BotConfigs.model_validate, db.query(models.BotConfigs).filter(*filters).all()))