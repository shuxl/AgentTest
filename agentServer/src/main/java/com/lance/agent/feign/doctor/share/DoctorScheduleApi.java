package com.lance.agent.feign.doctor.share;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(
        value = "doctor-service",
        path = "/sdk/schedule"
)
public interface DoctorScheduleApi {

    /**
     * 获取排班明细V2new
     * @param var1
     * @return
     */
    @GetMapping({"/detail/v2"})
    Object getScheduleDetailV2(@RequestParam("doctorId") Long var1);
}
