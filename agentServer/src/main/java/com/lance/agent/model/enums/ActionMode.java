package com.lance.agent.model.enums;

public enum ActionMode {
    /**
     * 自动
     */
    AUTO("auto"),

    /**
     * 人工介入审核
     */
    HITL("HITL"),

    /**
     * 干跑不生效
     */
    DRY_RUN("dryRun");

    private final String value;

    ActionMode(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
