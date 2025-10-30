from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from AnalyticDBPgSqlClient import ADBPG_INSTANCE_REGION, ADBPG_INSTANCE_ID, get_client
import os
from env_config import require_env

def create_document_collection(account,
                               account_password,
                               namespace,
                               collection,
                               metadata: str = None,
                               full_text_retrieval_fields: str = None,
                               parser: str = None,
                               embedding_model: str = None,
                               metrics: str = None,
                               hnsw_m: int = None,
                               pq_enable: int = None,
                               external_storage: int = None,):
    request = gpdb_20160503_models.CreateDocumentCollectionRequest(
        region_id=ADBPG_INSTANCE_REGION,
        dbinstance_id=ADBPG_INSTANCE_ID,
        manager_account=account,
        manager_account_password=account_password,
        namespace=namespace,
        collection=collection,
        metadata=metadata,
        full_text_retrieval_fields=full_text_retrieval_fields,
        parser=parser,
        embedding_model=embedding_model,
        metrics=metrics,
        hnsw_m=hnsw_m,
        pq_enable=pq_enable,
        external_storage=external_storage
    )
    response = get_client().create_document_collection(request)
    print(f"create_document_collection response code: {response.status_code}, body:{response.body}")


if __name__ == '__main__':
    metadata = '{"title":"text", "page":"int"}'
    full_text_retrieval_fields = "title"
    embedding_model = "m3e-small"
    # Resolve and validate required envs to avoid API 400
    _account = require_env('VECTOR_DB_MANAGER_ACCOUNT')
    _password = require_env('VECTOR_DB_MANAGER_PASSWORD')
    _namespace = require_env('VECTOR_DB_NAMESPACE')
    _collection = require_env('VECTOR_DB_COLLECTION')
    if not _account or not _password:
        raise RuntimeError("Missing VECTOR_DB_MANAGER_ACCOUNT or VECTOR_DB_MANAGER_PASSWORD in environment/.env")
    if not _namespace:
        raise RuntimeError("Missing VECTOR_DB_NAMESPACE in environment/.env")
    create_document_collection(
        _account,
        _password,
        _namespace,
        _collection,
        metadata=metadata, full_text_retrieval_fields=full_text_retrieval_fields,
        embedding_model=embedding_model)


# output: body:
# {
#    "Message":"success",
#    "RequestId":"7BC35B66-5F49-1E79-A153-8D26576C4A3E",
#    "Status":"success"
# }