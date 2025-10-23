package com.lance.agent.service;

import com.lance.agent.feign.blood.pressure.DoctorWorkbenchServiceApi;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 医生工作台服务实现类
 * 
 * @author lance
 */
@Service
public class DoctorWorkbenchService {

    @Autowired
    private DoctorWorkbenchServiceApi doctorWorkbenchServiceApi;

    /**
     * 获取绑定的医生ID
     * 
     * @param patientId 患者ID
     * @return 绑定的医生ID
     */
    public Object getBindDoctorId(Long patientId) {
        return doctorWorkbenchServiceApi.getBindDoctorId(patientId);
    }
}
