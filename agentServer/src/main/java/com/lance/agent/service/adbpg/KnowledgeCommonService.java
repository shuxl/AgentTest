package com.lance.agent.service.adbpg;

import com.aliyun.gpdb20160503.models.*;
import com.lance.agent.configuration.properties.AlibabaProperties;
import com.lance.agent.dto.adbpg.AdpPgQueryDTO;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;


@Slf4j
@Service
public class KnowledgeCommonService {
    @Resource
    private AnalyticDbPGQueryService queryService;
    @Resource
    private AlibabaProperties alibabaProperties;

    public List<QueryContentResponseBody.QueryContentResponseBodyMatchesMatchList> query(AdpPgQueryDTO queryDTO) throws Exception {
        QueryContentRequest queryContentRequest = new QueryContentRequest();

        // TODO 是否可以做成builder的形式，builder AlibabaProperties后，再
        queryContentRequest.setRegionId(alibabaProperties.getCloudAdbPgRegion());
        queryContentRequest.setDBInstanceId(alibabaProperties.getCloudAdbPgInstanceId());
        queryContentRequest.setNamespace(alibabaProperties.getVectorNamespaceName());
        queryContentRequest.setNamespacePassword(alibabaProperties.getVectorNamespacePassword());

        queryContentRequest.setCollection(queryDTO.getCollection()) ;
        queryContentRequest.setContent(queryDTO.getContent());
        queryContentRequest.setFilter(queryDTO.getFilter());
//        queryContentRequest.setTopK(queryDTO.getTopK());
        queryContentRequest.setTopK(5);
        queryContentRequest.setMetrics(queryDTO.getMetrics());
        queryContentRequest.setUseFullTextRetrieval(queryDTO.getUseFullTextRetrieval());
        QueryContentResponse response =  queryService.query(queryContentRequest);
        log.info("知识库召回结果: {}", response);
        return response.getBody().getMatches().getMatchList();
    }


}


