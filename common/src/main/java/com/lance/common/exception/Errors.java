package com.lance.common.exception;

/**
 * 系统错误码枚举
 * <p>
 * 定义系统中常用的错误码和错误信息
 * 提供静态方法用于创建动态错误对象
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
public enum Errors implements IError {
    /**
     * 未知异常
     */
    UNAUTHORIZED(401, "Unauthorized"),
    INTERNAL_SERVER_ERROR(500, "Internal Server Error"),
    ILLEGAL_ARGUMENT_EXCEPTION(502, "Illegal Argument Error"),
    REMOTE_SERVICE_ERROR(601, "feign接口调用异常"),
    ;

    private Integer code;
    private String msg;

    Errors(Integer code, String msg) {
        this.code = code;
        this.msg = msg;
    }

    @Override
    public Integer getCode() {
        return code;
    }

    @Override
    public String getMsg() {
        return msg;
    }

    public static DynamicError error(){
        return new DynamicError();
    }
    public static DynamicError error(Integer code){
        return error().setCode(code);
    }
    public static DynamicError error(Integer code,String msg){
        return error().setCode(code).setMsg(msg);
    }

    public static DynamicError error(Integer code,String msg,Throwable cause){
        return error().setCode(code).setMsg(msg).setCause(cause);
    }

    public static DynamicError error(Integer code,String msg,Throwable cause,int httpCode){
        return error().setCode(code).setMsg(msg).setCause(cause).setHttpCode(httpCode);
    }
}
