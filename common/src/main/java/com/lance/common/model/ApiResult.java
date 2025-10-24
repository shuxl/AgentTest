package com.lance.common.model;

import com.lance.common.enums.CodeEnum;
import com.lance.common.exception.IError;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

import java.io.Serializable;

/**
 * API统一响应结果封装类
 * <p>
 * 提供统一的API响应格式，包含状态码、消息和数据
 * 支持链式调用和泛型数据封装
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
@Data
@NoArgsConstructor
@Accessors(chain = true)
public class ApiResult<T> implements Serializable {

    private Integer code;
    private String msg;
    private T data;
    
    public ApiResult(Integer code, String msg, T data) {
        this.code = code;
        this.msg = msg;
        this.data = data;
    }

    public static <T> ApiResult<T> success() {
        return new ApiResult<>(CodeEnum.SUCCESS.getCode(), CodeEnum.SUCCESS.getDesc(), null);
    }

    public static <T> ApiResult<T> success(T data) {
        return new ApiResult<>(CodeEnum.SUCCESS.getCode(), CodeEnum.SUCCESS.getDesc(), data);
    }

    public static <T> ApiResult<T> success(String msg) {
        return new ApiResult<>(CodeEnum.SUCCESS.getCode(), msg, null);
    }

    public static <T> ApiResult<T> success(String msg, T data) {
        return new ApiResult<>(CodeEnum.SUCCESS.getCode(), msg, data);
    }

    public static <T> ApiResult<T> fail() {
        return new ApiResult<>(CodeEnum.ERROR.getCode(), CodeEnum.ERROR.getDesc(), null);
    }

    public static <T> ApiResult<T> fail(String msg) {
        return new ApiResult<>(CodeEnum.ERROR.getCode(), msg, null);
    }

    public static <T> ApiResult<T> fail(Integer code, String msg) {
        return new ApiResult<>(code, msg, null);
    }

    public static <T> ApiResult<T> fail(Integer code, String msg, T data) {
        return new ApiResult<>(code, msg, data);
    }

    public static <T> ApiResult<T> fail(IError error) {
        return new ApiResult<>(error.getCode(), error.getMsg(), null);
    }

    public boolean isSuccess(){
        return CodeEnum.SUCCESS.getCode().equals(this.code);
    }
}
