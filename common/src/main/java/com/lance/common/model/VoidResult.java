package com.lance.common.model;

/**
 * 空结果枚举类
 * <p>
 * 当接口需要返回null/void/Void时，使用VoidResult代替
 * 采用单例模式，提供统一的空结果表示
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
public enum VoidResult {
    INSTANCE;
}
