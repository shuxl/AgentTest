from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from AnalyticDBPgSqlClient import ADBPG_INSTANCE_REGION, ADBPG_INSTANCE_ID, get_client
import os
from env_config import require_env


def init_vector_database(account, account_password):
    request = gpdb_20160503_models.InitVectorDatabaseRequest(
        region_id=ADBPG_INSTANCE_REGION,
        dbinstance_id=ADBPG_INSTANCE_ID,
        manager_account=account,
        manager_account_password=account_password
    )
    response = get_client().init_vector_database(request)
    print(f"init_vector_database response code: {response.status_code}, body:{response.body}")


if __name__ == '__main__':
    account = require_env('VECTOR_DB_MANAGER_ACCOUNT')
    password = require_env('VECTOR_DB_MANAGER_PASSWORD')
    if not account or not password:
        raise RuntimeError("Missing VECTOR_DB_MANAGER_ACCOUNT or VECTOR_DB_MANAGER_PASSWORD in environment/.env")
    init_vector_database(account, password)


# output: body:
# {
#    "Message":"success",
#    "RequestId":"FC1E0318-E785-1F21-A33C-FE4B0301B608",
#    "Status":"success"
# }