from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url : str
    CLOUD_NAME : str
    API_KEY : str
    API_SECRET : str
    
    class Config:
        env_file = 'db.env'

settings = Settings()