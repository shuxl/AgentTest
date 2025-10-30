package com.lance.agent.configuration;


import com.aliyun.credentials.Client;
import com.aliyun.teaopenapi.models.Config;
import com.lance.agent.configuration.properties.AlibabaProperties;
import jakarta.annotation.Resource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 *
 * @author xiaoLong.shu
 * @date 2025-10-30
 */
@Configuration
public class AnalyticDbPGConfig {
    @Resource
    private AlibabaProperties alibabaProperties;
    @Bean("adbPGClient")
    public com.aliyun.gpdb20160503.Client createClient() throws Exception {
        try {
            Client credential = new Client();
            Config config = new com.aliyun.teaopenapi.models.Config()
                    .setAccessKeyId(alibabaProperties.getCloudAccessKeyId())
                    .setAccessKeySecret(alibabaProperties.getCloudAccessKeySecret())
//                    .setRegionId(alibabaProperties.getCloudAdbPgRegion())
                    .setEndpoint(alibabaProperties.getCloudAdbPgEndPoint())
                    .setCredential(credential);
            return new com.aliyun.gpdb20160503.Client(config);
        } catch (Exception e) {
            throw new RuntimeException("Failed to initialize AnalyticDB Client", e);
        }
    }
}
