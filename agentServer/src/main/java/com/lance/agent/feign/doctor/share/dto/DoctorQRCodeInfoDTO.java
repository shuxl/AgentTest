package com.lance.agent.feign.doctor.share.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotNull;
import java.util.List;

@Schema(title = "医生微信二维码信息，含渠道码、工作群码", description = "医生微信二维码信息，含渠道码、工作群码")
@Data
public class DoctorQRCodeInfoDTO {

    @Schema(description = "医生Code")
    @NotNull
    private String doctorClientCode;

    @Schema(description = "医生渠道码url")
    @NotNull
    private String doctorChannelCode;

    // todo account_migration 改成列表
    @Schema(description = "医生工作群码url")
    private List<String> doctorGroupCodes;

    // todo account_migration 改成列表
    @Schema(description = "医生管理的群码（患者群码）")
    private List<String> doctorManageGroupCodes;

    @Schema(description = "医生标签（血压=BLOOD_PRESSURE，血脂=BLOOD_LIPID, 大场域=YUEHUI）")
    @NotNull
    private String doctorTag;

    @Schema(description = "小助手名称（血脂没有）")
    private String assistantName;

    @Schema(description = "小助手头像url（血脂没有）")
    private String assistantAvatar;

    @Schema(description = "小助手企微userId")
    private String assistanWxUserId;

    // todo account_migration 新增doctor_assistants字段，保存助手列表
    @Schema(description = "医生助手列表")
    private List<DoctorAssistant> doctorAssistants;

    @Schema(description = "医患企微群id,支持多个")
    private List<String> wxChatIds;

    @Schema(description = "医助企微群id,支持多个")
    private List<String> assistantChatIds;

    @Schema(description = "渠道code")
    private String channelCode;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DoctorAssistant {

        @Schema(description = "医助名称--企信员工微信名称")
        private String assistantName;

        @Schema(description = "医助头像ur--企信员工微信头像")
        private String assistantAvatar;

        @Schema(description = "医助企微userId--企信员工微信ID")
        @NotEmpty(message = "医助id不能为空")
        private String assistantWxUserId;
    }
}
