import os
from envparse import env

class BaseConfig:
    HF_TOKEN: str = env("APP_AUTH_TOKEN", "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")
    LOAD_IN_8BIT: bool = env("LOAD_IN_8BIT", True)


settings = BaseConfig()