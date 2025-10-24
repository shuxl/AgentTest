package com.lance.agent.feign.doctor.share.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

import java.util.Date;
import java.util.List;

/**
 * @author system
 * @version V1.0
 * @Title: doctor-service
 * @Package com.yuehuijiankang.doctor.share.vo.schedule
 * @Description: 医生排班设置V2返回对象
 * @date 2024/3/10
 */
@Data
@Accessors(chain = true)
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Schema(title = "医生排班设置V2", description = "医生排班设置V2")
public class DoctorScheduleSettingV2 {

    @Schema(description = "医生信息")
    private DoctorDTO doctorInfo;

    @Schema(description = "执业点信息列表")
    private List<PracticeInfo> practiceInfos;

    @Data
    @Accessors(chain = true)
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(title = "执业点信息", description = "执业点信息")
    public static class PracticeInfo {
        @Schema(description = "是否开启循环配置")
        private Boolean enableSchedule;

        @Schema(description = "循环开始日期")
        @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
        private Date cycleStartDate;

        @Schema(description = "循环结束日期")
        @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
        private Date cycleEndDate;

        @Schema(description = "停诊结束时间")
        @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
        private Date suspendEndTime;

        @Schema(description = "停诊开始时间")
        @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
        private Date suspendStartTime;

        @Schema(description = "灵活排班")
        private List<ScheduleInfo> flexibleSchedule;

        @Schema(description = "执业点key")
        private String practiceKey;

        @Schema(description = "执业点名称")
        private String practiceName;

        @Schema(description = "执业点备注")
        private String practiceRemark;

        @Schema(description = "四周排班(患者端用)")
        private List<ScheduleInfo> fourWeekSchedule;

        @Schema(description = "本周排班")
        private List<ScheduleInfo> thisWeekSchedule;

        @Schema(description = "发布标记")
        private Boolean publicFlg;
    }

    @Data
    @Accessors(chain = true)
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(title = "排班信息", description = "排班信息")
    public static class ScheduleInfo {
        @Schema(description = "下午是否有排班")
        private Boolean afternoonArranged;

        @Schema(description = "周几")
        private Integer dayOfWeek;

        @Schema(description = "上午是否有排班")
        private Boolean morningArranged;

        @Schema(description = "排班日期")
        private String scheduleDay;

        @Schema(description = "是否停诊 是(true)否(false)")
        private Boolean suspendFlg;

        @Schema(description = "是否是当天")
        private Boolean today;
    }
}