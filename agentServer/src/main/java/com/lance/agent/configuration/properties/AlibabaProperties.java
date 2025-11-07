package com.lance.agent.configuration.properties;

import lombok.Data;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Data
@Component
public class AlibabaProperties {

    @Value("${alibaba.cloud.access_key.id:}")
    private String cloudAccessKeyId;

    @Value("${alibaba.cloud.access_key.secret:}")
    private String cloudAccessKeySecret;

    @Value("${alibaba.cloud.adb_pg.instance_id:}")
    private String cloudAdbPgInstanceId;

    @Value("${alibaba.cloud.adb_pg.region:}")
    private String cloudAdbPgRegion;

    @Value("${alibaba.cloud.adb_pg.endPoint:}")
    private String cloudAdbPgEndPoint;

    @Value("${alibaba.vector.db_manager.account:}")
    private String vectorDbManagerAccount;

    @Value("${alibaba.vector.db_manager.password:}")
    private String vectorDbManagerPassword;

    @Value("${alibaba.vector.namespace.name:}")
    private String vectorNamespaceName;

    @Value("${alibaba.vector.namespace.password:}")
    private String vectorNamespacePassword;
}
