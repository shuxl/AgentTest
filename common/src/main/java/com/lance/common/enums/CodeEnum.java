package com.lance.common.enums;

/**
 * 通用状态码枚举
 * <p>
 * 定义系统中常用的状态码，包括成功和失败状态
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
public enum CodeEnum {
    SUCCESS(0, "SUCCESS"),
    ERROR(1, "ERROR");

    private final Integer code;
    private final String desc;
    
    CodeEnum(Integer code, String desc){
        this.code = code;
        this.desc = desc;
    }
    
    public Integer getCode() {
        return code;
    }
    
    public String getDesc() {
        return desc;
    }
}
