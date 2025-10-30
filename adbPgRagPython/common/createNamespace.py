from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from AnalyticDBPgSqlClient import ADBPG_INSTANCE_REGION, ADBPG_INSTANCE_ID, get_client
import os
from env_config import require_env

def create_namespace(account, account_password, namespace, namespace_password):
    request = gpdb_20160503_models.CreateNamespaceRequest(
        region_id=ADBPG_INSTANCE_REGION,
        dbinstance_id=ADBPG_INSTANCE_ID,
        manager_account=account,
        manager_account_password=account_password,
        namespace=namespace,
        namespace_password=namespace_password
    )
    response = get_client().create_namespace(request)
    print(f"create_namespace response code: {response.status_code}, body:{response.body}")


if __name__ == '__main__':
    create_namespace(
        require_env('VECTOR_DB_MANAGER_ACCOUNT'),
        require_env('VECTOR_DB_MANAGER_PASSWORD'),
        require_env('VECTOR_DB_NAMESPACE'),
        require_env('VECTOR_DB_NAMESPACE_PASSWORD')
    )


# output: body:
# {
#    "Message":"success",
#    "RequestId":"78356FC9-1920-1E09-BB7B-CCB6BD267124",
#    "Status":"success"
# }