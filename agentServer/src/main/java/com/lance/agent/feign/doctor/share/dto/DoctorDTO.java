package com.lance.agent.feign.doctor.share.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

@Data
@EqualsAndHashCode(callSuper = false)
@Schema(title = "Doctor对象", description = "医生表")
public class DoctorDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    @Schema(description = "用户id")
    private Long userId;

    @Schema(description = "医生编码")
    private String doctorCode;

    @Schema(description = "医生编码(同步)")
    private String clientCode;

    @Schema(description = "mdm医生编码(同步)")
    @JsonProperty("MDMClientCode")
    private String MDMClientCode;

    @Schema(description = "医生姓名")
    private String doctorName;

    @Schema(description = "医生头像")
    private String doctorAvatar;

    @Schema(description = "医生性别 m:男;f:女")
    private String doctorGender;

    @Schema(description = "医院编号")
    private String hospitalCode;

    @Schema(description = "医院")
    private String hospital;

    @Schema(description = "科室")
    private String dept;

    @Schema(description = "职称")
    private String professionalLevel;

    /**
     * 前端用拼错的professionalLevel
     */
    @Schema(description = "职称")
    private String profesionalLevel;

    @Schema(description = "绑定专员岗位编码")
    private String micsCode;

    @Schema(description = "绑定专员名字")
    private String micsName;

    @Schema(description = "执业证")
    private String certificateImg;

    @Schema(description = "血脂助理姓名")
    private String lipidAssistantName;

    @Schema(description = "血脂小助手头像")
    private String lipidAssistantAvatar;

    @Schema(description = "血脂助理详情")
    private String lipidAssistantDetail;

    @Schema(description = "血脂群二维码")
    private String lipidGroupQrcode;

    @Schema(description = "血脂小助手二维码")
    private String lipidAssistantQrcode;

    @Schema(description = "血压助理姓名")
    private String pressureAssistantName;

    @Schema(description = "血压小助手头像")
    private String pressureAssistantAvatar;

    @Schema(description = "血压助理详情")
    private String pressureAssistantDetail;

    @Schema(description = "血压群二维码")
    private String pressureGroupQrcode;

    @Schema(description = "血压小助手二维码")
    private String pressureAssistantQrcode;

    @Schema(description = "悦晖助理姓名")
    private String yuehuiAssistantName;

    @Schema(description = "悦晖小助手头像")
    private String yuehuiAssistantAvatar;

    @Schema(description = "悦晖群二维码")
    private String yuehuiGroupQrcode;

    @Schema(description = "悦晖小助手二维码")
    private String yuehuiAssistantQrcode;

    @Schema(description = "悦晖台卡码")
    private String yuehuiDeccaQrcode;

    @Schema(description = "悦晖小助手微信uid")
    private String assistantWxUid;

    @Schema(description = "医生所属群列表")
    private String wxChatIds;

    @Schema(description = "医生标签: 1:血压;2:血脂;3:血压+血脂;4:医链;5:血压+医链;6:血脂+医链;7:血压+血脂+医链;位运算 1(001):血压 2(010):血脂 4(100): 悦晖")
    private Integer tag;

    @Schema(description = "扩展信息")
    private String extInfo;

    @Schema(description = "当前隐私协议版本")
    private String agreement_1;

    @Schema(description = "当前用户协议版本")
    private String agreement_2;

    @Schema(description = "最新隐私协议版本")
    private String agreement_1_newest;

    @Schema(description = "最新用户协议版本")
    private String agreement_2_newest;

    @Schema(description = "医生业务场景码")
    private String sceneCodes;
    @Schema(description = "医生业务场景码描述")
    private String sceneCodesDescription;

    @Schema(description = "专员名称")
    private String specName;

    @Schema(description = "已添加的渠道编码")
    private List<String> channelCodeList;

    @Schema(description = "全部台卡码")
    private List<DeccaDTO> deccaList;

    @Schema(description = "默认台卡码")
    private DoctorAssistantInfoDTO normalDecca;

    @Schema(description = "台卡码权限")
    private Map<String, Boolean> toolAuthMap;

    public boolean isPressure() {
        //tag maybe empty
        return tag != null && (PRESSURE_DOCTOR & tag) == PRESSURE_DOCTOR;
    }

    public boolean isLipid() {
        //tag maybe empty
        return tag != null && (LIPID_DOCTOR & tag) == LIPID_DOCTOR;
    }

    public boolean isYuehui() {
        //tag maybe empty
        return tag != null && (YUEHUI_DOCTOR & tag) == YUEHUI_DOCTOR;
    }

    public static final int PRESSURE_DOCTOR = 1;

    public static final int LIPID_DOCTOR = 1 << 1;

    public static final int YUEHUI_DOCTOR = 1 << 2;

}
