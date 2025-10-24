package com.lance.common.exception;

/**
 * 动态错误类
 * <p>
 * 用于动态创建错误信息，支持链式调用设置错误码、错误信息、HTTP状态码等
 * 实现了IError接口，提供完整的错误信息封装
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
public class DynamicError implements IError {
    private Integer code;
    private String msg;
    private int httpCode = 200;
    private Object responseBody;
    private Throwable cause;
    
    public DynamicError setCode(Integer code) {
        this.code = code;
        return this;
    }
    
    public DynamicError setMsg(String msg) {
        this.msg = msg;
        return this;
    }
    
    public DynamicError setHttpCode(int httpCode) {
        this.httpCode = httpCode;
        return this;
    }
    
    public DynamicError setResponseBody(Object responseBody) {
        this.responseBody = responseBody;
        return this;
    }
    
    public DynamicError setCause(Throwable cause) {
        this.cause = cause;
        return this;
    }
    
    @Override
    public Integer getCode() {
        return code;
    }
    
    @Override
    public String getMsg() {
        return msg;
    }
    
    @Override
    public int getHttpCode() {
        return httpCode;
    }
    
    @Override
    public Object getResponseBody() {
        return responseBody;
    }
    
    @Override
    public Throwable getCause() {
        return cause;
    }
}