import sqlalchemy
from app.database import DATABASE_URL

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata = sqlalchemy.MetaData()
metadata.reflect(bind=engine)
activity_logs_table = metadata.tables['activity_logs']
activity_logs_table.drop(engine)
