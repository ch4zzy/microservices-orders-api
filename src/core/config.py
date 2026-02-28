from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DEBUG: bool
    ALGORITHM: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    USERS_API_HOST: str = ...
    USERS_API_PORT: int = ...

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # noqa
