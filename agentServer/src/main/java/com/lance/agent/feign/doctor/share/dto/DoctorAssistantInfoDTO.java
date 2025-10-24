package com.lance.agent.feign.doctor.share.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.Date;
import java.util.List;

/**
 * @author tieshou
 * @version V1.0
 * @Title: doctor-service
 * @Package com.yuehuijiankang.doctor.share.dto
 * @Description: (用一句话描述该文件做什么)
 * @date 2023/3/13 15:16
 */
@Data
@EqualsAndHashCode(callSuper = false)
@Schema(title = "DoctorAssistant对象", description = "医生助手信息表")
public class DoctorAssistantInfoDTO {

    @Schema(description = "id")
    private Long id;

    @Schema(description = "医生id")
    private Long doctorId;

    @Schema(description = "医生tag")
    private Integer doctorTag;

    @Schema(description = "助手姓名")
    private String assistantName;

    @Schema(description = "助手头像")
    private String assistantAvatar;

    @Schema(description = "助手二维码")
    private String assistantQrcode;

    @Schema(description = "医助群二维码")
    private String groupQrcode;

    @Schema(description = "医助群二维码列表")
    private List<String> groupQrcodes;

    @Schema(description = "患者群二维码")
    private String patientQrcode;

    @Schema(description = "患者群二维码列表")
    private List<String> patientQrcodes;

    @Schema(description = "台卡二维码")
    private String deccaQrcode;

    @Schema(description = "台卡二维码key")
    private String deccaKey;

    @Schema(description = "台卡码类型：1正常，2迁移")
    private Integer deccaType;

    @Schema(description = "小助手企微userId")
    private String assistantWxUid;

    @Schema(description = "医患企微群id,支持多个")
    private List<String> wxChatIds;

    @Schema(description = "医助企微群id,支持多个")
    private List<String> assistantChatIds;

    @Schema(description = "小助手信息列表")
    private List<DoctorQRCodeInfoDTO.DoctorAssistant> doctorAssistants;

    @Schema(description = "状态0: 未启用，1: 已启用，2: 已停用，3 删除")
    private Integer state;

    @Schema(description = "渠道标记")
    private String channelLabel;

    @Schema(description = "台卡名称")
    private String deccaName;

    @Schema(description = "台卡描述")
    private String deccaDesc;

    @Schema(description = "渠道标记code")
    private String channelCode;

    @Schema(description = "是否启用新群，true表示启用")
    private Boolean newGroup;

    @Schema(description = "是否自动拉群, true表示自动拉群")
    private Boolean enableAutoPullGroup;

    @Schema(description = "是否执行群SOP, true表示执行 不传默认true")
    private Boolean enableGroupSop;

    @Schema(description = "群名称, 空表示不修改，非空表示要修改的群名")
    private String groupName;

    @Schema(description = "医患群企微群id,支持多个")
    @Deprecated
    private List<String> patientChatGroupIds;

    @Schema(description = "医患群企微群id,支持多个")
    @Deprecated
    private List<String> assistantChatGroupIds;

    @Schema(description = "启用时间")
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private Date startUseTime;

    @Schema(description = "停用时间")
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private Date stopUseTime;

    @Schema(description = "创建时间")
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createTime;

    @Schema(description = "更新时间")
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private Date updateTime;

    @Schema(description = "医生信息")
    private DoctorDTO doctor;

    @Schema(description = "招募链路")
    private String recruitChain;

    @Schema(description = "公众号二维码")
    private String mpQrCode;

    @Schema(description = "是否跳过基线5")
    private Boolean skipBaseline5;

    @Schema(description = "小程序太阳码url")
    private String sunQrcodeUrl;
}
