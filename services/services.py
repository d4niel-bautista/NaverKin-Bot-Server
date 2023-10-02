from database import models, database

def create_database():
    models.Base.metadata.create_all(bind=database.engine)