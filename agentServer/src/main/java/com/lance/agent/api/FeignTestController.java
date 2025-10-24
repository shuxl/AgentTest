package com.lance.agent.api;

import com.lance.agent.feign.doctor.share.DoctorScheduleApi;
import com.lance.agent.feign.doctor.share.dto.DoctorScheduleSettingV2;
import com.lance.agent.service.DoctorWorkbenchService;
import com.lance.common.model.ApiResult;
import jakarta.annotation.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/feign")
public class FeignTestController {

    @Resource
    private DoctorWorkbenchService doctorWorkbenchService;

    @Autowired
    private DoctorScheduleApi doctorScheduleApi;

    @GetMapping("/getBindDoctorId")
    public Object getBindDoctorId(Long patientId) {
        return doctorWorkbenchService.getBindDoctorId(patientId);
    }

    @GetMapping("/getScheduleDetailV2")
    public ApiResult<DoctorScheduleSettingV2> getScheduleDetailV2(Long doctorId) {
        var result = doctorScheduleApi.getScheduleDetailV2(doctorId);
        return result;
    }
}
