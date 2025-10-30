package com.lance.agent.dto.adbpg;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;

/**
 * AdbPg 向量检索/混合检索查询参数
 * - 用于封装查询所需的内容、过滤条件与检索配置
 * - 对应 ADB PG RAG 查询接口的输入参数
 *
 * @author xiaolong.shu
 * @date 2025-10-30
 */
@Data
public class AdpPgQueryDTO {

    @NotBlank(message = "collection不能为空")
    private String collection;

    /**
     * 用户查询内容（待向量化或语义检索的文本）
     */
    @NotBlank(message = "content不能为空")
    private String content;



    /**
     * 过滤条件（例如文件名、标签等，具体语法由后端解析）
     */
    private String filter;

    /**
     * 返回结果条数上限（Top-K）
     */
//    private Integer topK;

    /**
     * 检索指标/度量方式（例如 cosine、euclidean 等）
     */
    private String metrics;

    /**
     * 是否启用全文检索参与混合检索
     */
    private Boolean useFullTextRetrieval;
}
