package com.lance.agent.model.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * @projectName: pd-chat
 * @package: com.viatris.pd.chat.core.enums
 * @className: ChatTypeEnum
 * @author: Andy.lq
 * @description: ChatTypeEnum 对话类型
 * @date: 2025/1/21 10:18
 * @version: 1.0
 */
@Getter
@AllArgsConstructor
public enum ChatTypeEnum {
    /**
     * 对话类型
     */
    PERSONAL("single"),
    GROUP("group");

    private String code;

    public static ChatTypeEnum getByCode(String code) {
        for (ChatTypeEnum value : values()) {
            if (value.code.equals(code)) {
                return value;
            }
        }
        throw new IllegalArgumentException("Invalid ChatTypeEnum code: " + code);
    }

}
