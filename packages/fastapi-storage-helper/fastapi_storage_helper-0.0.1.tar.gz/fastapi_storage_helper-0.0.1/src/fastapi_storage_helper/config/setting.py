import os

from dotenv import dotenv_values

loaded_env = dotenv_values(".env")


def get_env(key, default=None):
    if key in loaded_env:
        return loaded_env.get(key)
    if os.getenv(key):
        return os.getenv(key)
    return default


class Setting:
    # S3 config
    AWS_S3_BUCKET_NAME = get_env('AWS_S3_BUCKET_NAME')
    AWS_SECRET_KEY = get_env('AWS_SECRET_KEY')
    AWS_ACCESS_KEY_ID = get_env('AWS_ACCESS_KEY_ID')
    AWS_REGION = get_env('AWS_REGION')
    AWS_SNS_S3_TOPIC = get_env('AWS_SNS_S3_TOPIC')
    AWS_SNS_LAMBDA_TOPIC = get_env('AWS_SNS_LAMBDA_TOPIC')
    AWS_SNS_CALLBACK_TOPIC = get_env('AWS_SNS_CALLBACK_TOPIC')
    AWS_SNS_ENDPOINT = get_env('AWS_SNS_ENDPOINT')


env = Setting()
