package com.lance.agent.feign.doctor.share.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
public class DeccaDTO {
    @Schema(description = "台卡二维码")
    private String deccaQrcode;

    @Schema(description = "台卡二维码key")
    private String deccaKey;

    @Schema(description = "渠道标记名称")
    private String channelLabel;

    @Schema(description = "渠道标记code")
    private String channelCode;

    @Schema(description = "状态")
    private Integer state;

    @Schema(description = "招募路径")
    private String recruitChain;

    @Schema(description = "是否跳过基线5")
    private Boolean skipBaseline5;

    @Schema(description = "小程序太阳码")
    private String sunQrcodeUrl;
}
