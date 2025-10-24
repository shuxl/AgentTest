package com.lance.agent.feign.doctor.share;

import com.lance.agent.feign.doctor.share.dto.DoctorScheduleSettingV2;
import com.lance.common.model.ApiResult;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(
        value = "doctor-service",
        path = "/sdk/schedule"
)
public interface DoctorScheduleApi {

    /**
     * 获取排班明细V2
     * @param doctorId 医生ID
     * @return 排班信息
     */
    @GetMapping({"/detail/v2"})
    ApiResult<DoctorScheduleSettingV2> getScheduleDetailV2(@RequestParam("doctorId") Long doctorId);
}
