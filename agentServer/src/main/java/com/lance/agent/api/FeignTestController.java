package com.lance.agent.api;

import com.lance.agent.service.DoctorWorkbenchService;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/feign")
public class FeignTestController {

    @Resource
    private DoctorWorkbenchService doctorWorkbenchService;

    @GetMapping("/getBindDoctorId")
    public Object getBindDoctorId(Long patientId) {
        return doctorWorkbenchService.getBindDoctorId(patientId);
    }
}
