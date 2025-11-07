
import time
import io
import os
import glob
from typing import Dict, List, Any
from alibabacloud_tea_util import models as util_models
from alibabacloud_gpdb20160503 import models as gpdb_20160503_models
from AnalyticDBPgSqlClient import ADBPG_INSTANCE_REGION, ADBPG_INSTANCE_ID, get_client

def upload_document_async(
        namespace,
        namespace_password,
        collection,
        file_name,
        file_path,
        metadata: Dict[str, Any] = None,
        chunk_overlap: int = None,
        chunk_size: int = None,
        document_loader_name: str = None,
        text_splitter_name: str = None,
        dry_run: bool = None,
        zh_title_enhance: bool = None,
        separators: List[str] = None,
        vl_enhance: bool = None,
        splitter_model: str = None):
    with open(file_path, 'rb') as f:
        file_content_bytes = f.read()
    request = gpdb_20160503_models.UploadDocumentAsyncAdvanceRequest(
        region_id=ADBPG_INSTANCE_REGION,
        dbinstance_id=ADBPG_INSTANCE_ID,
        namespace=namespace,
        namespace_password=namespace_password,
        collection=collection,
        file_name=file_name,
        metadata=metadata,
        chunk_overlap=chunk_overlap,
        chunk_size=chunk_size,
        document_loader_name=document_loader_name,
        file_url_object=io.BytesIO(file_content_bytes),
        text_splitter_name=text_splitter_name,
        dry_run=dry_run,
        zh_title_enhance=zh_title_enhance,
        separators=separators,
        vl_enhance=vl_enhance,
        splitter_model=splitter_model,
    )
    response = get_client().upload_document_async_advance(request, util_models.RuntimeOptions())
    print(f"upload_document_async response code: {response.status_code}, body:{response.body}")
    return response.body.job_id


def wait_upload_document_job(namespace, namespace_password, collection, job_id):
    def job_ready():
        request = gpdb_20160503_models.GetUploadDocumentJobRequest(
            region_id=ADBPG_INSTANCE_REGION,
            dbinstance_id=ADBPG_INSTANCE_ID,
            namespace=namespace,
            namespace_password=namespace_password,
            collection=collection,
            job_id=job_id,
        )
        response = get_client().get_upload_document_job(request)
        print(f"get_upload_document_job response code: {response.status_code}, body:{response.body}")
        return response.body.job.completed
    while True:
        if job_ready():
            print("successfully load document")
            break
        time.sleep(2)


if __name__ == '__main__':
    job_id = upload_document_async("ns251016", "Ns251016_pwd", "dc_test_1",
                                   "晖致年假政策.docx", "/Users/m684620/work/python/sxl_test/aliAdbPg/file/晖致年假政策.docx")
    wait_upload_document_job("ns251016", "Ns251016_pwd", "dc_test_1", job_id)


# upload_document_async output:
# {
#    "JobId":"95de2856-0cd4-44bb-b216-ea2f0ebcc57b",
#    "Message":"Successfully create job",
#    "RequestId":"9F870770-C402-19EC-9E26-ED7E4F539C3E",
#    "Status":"success"
# }

# get_upload_document_job output:
# {
#    "ChunkResult":{
#        "ChunkFileUrl":"http://knowledge-base-gp-xx.oss-cn-beijing.aliyuncs.com/ns1/dc1/produce-files/test.pdf/chunks.jsonl?Expires=1706530707&OSSAccessKeyId=ak&Signature=6qUSwBtuthr0L9OxKoTh7kEohxQ%3D",
#        "PlainChunkFileUrl":"http://knowledge-base-gp-xx.oss-cn-beijing.aliyuncs.com/ns1/dc1/produce-files/test.pdf/plain_chunks.txt?Expires=1706530707&OSSAccessKeyId=ak&Signature=sxc5iiGUDE2M%2FV0JikFvQE7FdBM%3D"
#    },
#    "Job":{
#        "Completed":true,
#        "CreateTime":"2024-01-29 18:15:27.364484",
#        "Id":"95de2856-0cd4-44bb-b216-ea2f0ebcc57b",
#        "Progress":100,
#        "Status":"Success",
#        "UpdateTime":"2024-01-29 18:15:53.78808"
#    },
#    "Message":"Success get job info",
#    "RequestId":"64487F02-5A02-1CD9-BA5C-B59E9D3A68CC",
#    "Status":"success"
# }