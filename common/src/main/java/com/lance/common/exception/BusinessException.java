package com.lance.common.exception;

import lombok.EqualsAndHashCode;
import lombok.Getter;
import org.apache.commons.lang3.StringUtils;

import java.util.Objects;

/**
 * 业务异常类
 * <p>
 * 用于处理业务逻辑中的异常情况，支持多种构造方式
 * 包含错误码、错误信息和原始异常信息
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
@EqualsAndHashCode(callSuper = true)
@Getter
public class BusinessException extends RuntimeException {
    private IError error;

    public BusinessException(String msg) {
        super(msg);
        this.error = Errors.INTERNAL_SERVER_ERROR.format(msg);
    }

    public BusinessException(String msg, Throwable cause) {
        super(msg, cause);
        this.error = Errors.INTERNAL_SERVER_ERROR.format(msg).setCause(cause);
    }

    public BusinessException(Integer code, String msg) {
        super(StringUtils.isNotBlank(msg) ? msg : code.toString());
        this.error = Errors.error(code, msg);
    }

    public BusinessException(Integer code, String msg, Throwable cause) {
        super(StringUtils.isNotBlank(msg) ? msg : code.toString(), cause);
        this.error = Errors.error(code, msg).setCause(cause);
    }

    public BusinessException(IError error) {
        super(error.getMsg());
        Objects.nonNull(error);
        this.error = error;
    }

    public BusinessException(IError error, Throwable cause) {
        super(error.getMsg(), cause);
        Objects.nonNull(error);
        this.error = error;
    }
}
