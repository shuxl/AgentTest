package com.lance.common.exception;

/**
 * 错误信息接口
 * <p>
 * 定义错误信息的标准接口，包含错误码、错误信息、HTTP状态码等
 * 提供默认方法用于格式化错误信息和获取错误详情
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
public interface IError {
    /**
     * 业务异常错误码
     *
     * @return
     */
    Integer getCode();

    /**
     * 业务错误提示信息
     *
     * @return
     */
    String getMsg();

    /**
     * http 状态码
     *
     * @return
     */
    default int getHttpCode() {
        return 200;
    }

    /**
     * http response body
     *
     * @return
     */
    default Object getResponseBody() {
        return null;
    }

    /**
     * 原始异常
     *
     * @return
     */
    default Throwable getCause() {
        return null;
    }

    /**
     * 根据 message 模板格式化为新的错误信息
     *
     * @param args
     * @return
     */
    default DynamicError format(Object... args) {
        return Errors.error(this.getCode(), String.format(this.getMsg(), args))
                .setHttpCode(getHttpCode()).setResponseBody(getResponseBody()).setCause(getCause());
    }
}
