package com.lance.agent.api.adbpg;

import com.aliyun.gpdb20160503.models.QueryContentResponseBody;
import com.lance.agent.dto.adbpg.AdpPgQueryDTO;
import com.lance.agent.service.adbpg.KnowledgeCommonService;
import com.lance.common.model.ApiResult;
import jakarta.annotation.Resource;
import jakarta.validation.Valid;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * AnalyticDB PG 查询接口
 * - 提供知识库检索的对外 API
 */
@Validated
@RestController
@RequestMapping("/api/adbPG")
public class AnalyticDbPGQueryController {

    @Resource
    private KnowledgeCommonService knowledgeCommonService;

    /**
     * 发起知识库检索
     */
    @PostMapping("/knowledge/query")
    public ApiResult<List<QueryContentResponseBody.QueryContentResponseBodyMatchesMatchList>> knowledgeQuery(@Valid @RequestBody AdpPgQueryDTO dto) throws Exception {
        var result = knowledgeCommonService.query(dto);
        return ApiResult.success(result);
    }
}
