# 文档来源

- https://help.aliyun.com/zh/analyticdb/analyticdb-for-postgresql/user-guide/prepare-a-development-environment-1?spm=a2c4g.11186623.help-menu-92664.d_2_2_1_2.2d0b5b43snHB6j&scm=20140722.H_2803832._.OR_help-T_cn~zh-V_1

## python环境和sdk 安装

- python 版本 3.9或以上版本

- SDK
  ```
  pip install alibabacloud_gpdb20160503==3.5.0
  pip install alibabacloud_tea_openapi==0.3.8
  ```

- 阿里的环境key
    ```
    # 用RAM用户的AccessKey ID替换access_key_id
    export ALIBABA_CLOUD_ACCESS_KEY_ID="access_key_id"

    # 用RAM用户的AccessKey Secret替换access_key_secret
    export ALIBABA_CLOUD_ACCESS_KEY_SECRET="access_key_secret"

    # 用AnalyticDB for PostgreSQL的实例ID替换instance_id，例如gp-bp166cyrtr4p*****
    export ADBPG_INSTANCE_ID="instance_id"

    # 用AnalyticDB for PostgreSQL的实例所在地域的地域ID替换instance_region，例如cn-hangzhou
    export ADBPG_INSTANCE_REGION="instance_region"
    ```