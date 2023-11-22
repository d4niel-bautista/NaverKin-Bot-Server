from database import models, database, schemas
from sqlalchemy.orm import Session

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

async def get_naver_account(db: Session, filters: list=[], fetch_one: bool=True, schema: schemas.BaseModel = schemas.NaverAccountBase, schema_validate: bool=True):
    if schema_validate:
        return schema.model_validate(db.query(models.NaverAccount).filter(*filters).first())\
                if fetch_one else\
                list(map(schema.model_validate, db.query(models.NaverAccount).filter(*filters).all()))
    else:
        return db.query(models.NaverAccount).filter(*filters).first()\
                if fetch_one else\
                db.query(models.NaverAccount).filter(*filters).all()

async def get_account_interactions(db: Session, filters: list=[], fetch_one: bool=True):
    return schemas.AccountInteraction.model_validate(db.query(models.AccountInteraction).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.AccountInteraction.model_validate, db.query(models.AccountInteraction).filter(*filters).all()))

async def get_user_session(db: Session, filters: list=[], fetch_one: bool=True):
    return schemas.UserSession.model_validate(db.query(models.UserSession).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.UserSession.model_validate, db.query(models.UserSession).filter(*filters).all()))

async def get_bot_configs(db: Session, filters: list=[], fetch_one: bool=True, schema: schemas.BaseModel = schemas.BotConfigs):
    return schema.model_validate(db.query(models.BotConfigs).filter(*filters).first())\
            if fetch_one else\
            list(map(schema.model_validate, db.query(models.BotConfigs).filter(*filters).all()))

async def get_prompt_configs(db: Session, filters: list=[], fetch_one: bool=True):
    return schemas.PromptConfigs.model_validate(db.query(models.PromptConfigs).filter(*filters).first())\
            if fetch_one else\
            list(map(schemas.PromptConfigs.model_validate, db.query(models.PromptConfigs).filter(*filters).all()))

async def get_categories(db: Session, filters: list=[], fetch_one: bool=True, schema_validate: bool=True):
    if schema_validate:
        return schemas.Category.model_validate(db.query(models.Categories).filter(*filters).first())\
                if fetch_one else\
                list(map(schemas.Category.model_validate, db.query(models.Categories).filter(*filters).order_by(models.Categories.id.asc()).all()))
    else:
        return db.query(models.Categories).filter(*filters).first()\
                if fetch_one else\
                list(db.query(models.Categories).filter(*filters).order_by(models.Categories.id.asc()).all())

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

async def add_answer_response(answer: schemas.AnswerResponse, db: Session):
    answer_response = models.NaverKinAnswerResponse(**answer)
    db.add(answer_response)
    try:
        db.commit()
        db.refresh(answer_response)
        return answer_response
    except Exception as e:
        print(e)
        db.rollback()

async def add_category(category: schemas.Category, db: Session):
    category = models.Categories(**category.model_dump())
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
        return category
    except Exception as e:
        print(e)
        db.rollback()

async def update(model: models.Base, data: dict, filters: dict, db: Session):
    try:
        db.query(model).filter_by(**filters).update(data)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False
    
async def delete(model: models.Base, db: Session):
    try:
        db.delete(model)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False