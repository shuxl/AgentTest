import os
from typing import Optional


def _load_project_env() -> None:
    """Load only project-root .env (parent of this file's directory)."""
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    project_root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    if os.path.exists(project_root_env):
        load_dotenv(project_root_env)


# Load at import time (local/dev). In prod, vars can come from real env.
_load_project_env()


def require_env(key: str) -> str:
    value = os.getenv(key)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)

def _mask(value: Optional[str]) -> str:
    if not value:
        return "<EMPTY>"
    if len(value) <= 8:
        return "*" * (len(value) - 2) + value[-2:]
    return value[:2] + "***" + value[-4:]

if __name__ == "__main__":
    # Simple self-test printer for local debugging
    try:
        alibaba_key = require_env("ALIBABA_CLOUD_ACCESS_KEY_ID")
        alibaba_secret = require_env("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        instance_id = require_env("ADBPG_INSTANCE_ID")
        region = get_env("ADBPG_INSTANCE_REGION", "cn-shanghai")

        manager_account = require_env("VECTOR_DB_MANAGER_ACCOUNT")
        manager_password = require_env("VECTOR_DB_MANAGER_PASSWORD")
        namespace = require_env("VECTOR_DB_NAMESPACE")
        collection = get_env("VECTOR_DB_COLLECTION", "dc_test_1")
    except RuntimeError as e:
        print(f"[ENV ERROR] {e}")
        raise

    print("ALIBABA_CLOUD_ACCESS_KEY_ID:", _mask(alibaba_key))
    print("ALIBABA_CLOUD_ACCESS_KEY_SECRET:", _mask(alibaba_secret))
    print("ADBPG_INSTANCE_ID:", instance_id)
    print("ADBPG_INSTANCE_REGION:", region)
    print("VECTOR_DB_MANAGER_ACCOUNT:", manager_account)
    print("VECTOR_DB_MANAGER_PASSWORD:", _mask(manager_password))
    print("VECTOR_DB_NAMESPACE:", namespace)
    print("VECTOR_DB_COLLECTION:", collection)
