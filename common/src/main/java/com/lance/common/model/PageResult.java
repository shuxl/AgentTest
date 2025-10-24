package com.lance.common.model;

import lombok.Data;

import java.util.List;

/**
 * 分页查询结果封装类
 * <p>
 * 用于封装分页查询的结果数据，包含记录列表、总数、每页大小和当前页码
 * 通常与ApiResult配合使用，作为ApiResult的data字段
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
@Data
public class PageResult<T> {
    /**
     * 分页查询结果
     */
    private List<T> records;
    /**
     * 分页查询结果总数
     */
    private long total;
    /**
     * 分页查询每页数据条数
     */
    private long size;
    /**
     * 分页查询当前页码，从1开始
     */
    private long current;
}
