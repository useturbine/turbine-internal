from dotenv import load_dotenv
import os
from turbine.config import Config as BaseConfig

load_dotenv()


class Config(BaseConfig):
    openai_api_key: str


try:
    config = Config(
        database_url=os.environ["DATABASE_URL"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        sentry_dsn=os.environ["SENTRY_DSN"],
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )
except KeyError:
    raise ValueError("Missing required environment variable")
