package com.lance.agent.service.adbpg;

import com.aliyun.gpdb20160503.Client;
import com.aliyun.gpdb20160503.models.QueryContentRequest;
import com.aliyun.gpdb20160503.models.QueryContentResponse;
import com.aliyun.tea.TeaException;
import com.aliyun.teautil.Common;
import com.aliyun.teautil.models.RuntimeOptions;
import com.lance.common.exception.BusinessException;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;


/**
 * 云原生数据仓库AnalyticDB PostGreSQL检索服务
 *
 * @author XiaoLong.Shu
 * @date 2023/9/15 15:07
 */
@Slf4j
@Service
public class AnalyticDbPGQueryService {

    @Resource(name = "adbPGClient")
    private Client gpdbClient;

    public QueryContentResponse query(QueryContentRequest queryContentRequest) throws Exception {
        try {
            RuntimeOptions runtime = new RuntimeOptions();
            runtime.setAutoretry(true);
            runtime.setMaxAttempts(1);
            runtime.setReadTimeout(10000);
            runtime.setConnectTimeout(10000);
            runtime.setMaxIdleConns(0);
            QueryContentResponse response = gpdbClient.queryContentWithOptions(queryContentRequest, runtime);
            log.info("查询向量库接口 失败: {}", response);
            if (!Integer.valueOf(200).equals(response.getStatusCode()) || response.getBody().getStatus().equals("FAILED")) {
                log.error("查询向量库接口 失败: {}", response.getBody().getMessage());
                throw new Exception(response.getBody().getMessage());
            }
            log.info("查询向量库返回结果: {}", response);
            return response;
        } catch (TeaException teaException) {
            log.error(teaException.getMessage(), teaException.getData().get("Recommend"));
            Common.assertAsString(teaException.message);
        } catch (Exception ex) {
            TeaException exception = new TeaException(ex.getMessage(), ex);
            log.error(exception.getMessage(), exception.getData().get("Recommend"));
            Common.assertAsString(exception.message);
        }
        throw new BusinessException("查询文档时发生未知异常");
    }
}
