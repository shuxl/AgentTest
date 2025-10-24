package com.lance.common.model;

import lombok.Data;

/**
 * 分页信息类
 * <p>
 * 用于封装分页查询的请求参数，包含每页大小和当前页码
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
@Data
public class PageInfo {
    private long size;
    private long current;
}
