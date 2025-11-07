from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_gpdb20160503.client import Client
import os
from env_config import require_env

ALIBABA_CLOUD_ACCESS_KEY_ID = require_env('ALIBABA_CLOUD_ACCESS_KEY_ID')
ALIBABA_CLOUD_ACCESS_KEY_SECRET = require_env('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
ADBPG_INSTANCE_ID = require_env('ADBPG_INSTANCE_ID')
ADBPG_INSTANCE_REGION = require_env('ADBPG_INSTANCE_REGION')


def get_client():
    config = open_api_models.Config(
        access_key_id=ALIBABA_CLOUD_ACCESS_KEY_ID,
        access_key_secret=ALIBABA_CLOUD_ACCESS_KEY_SECRET
    )
    config.region_id = ADBPG_INSTANCE_REGION
    # https://api.aliyun.com/product/gpdb
    if ADBPG_INSTANCE_REGION in ("cn-beijing", "cn-hangzhou", "cn-shanghai", "cn-shenzhen", "cn-hongkong",
                                 "ap-southeast-1"):
        config.endpoint = "gpdb.aliyuncs.com"
    else:
        config.endpoint = f'gpdb.{ADBPG_INSTANCE_REGION}.aliyuncs.com'
    return Client(config)