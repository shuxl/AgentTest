
package com.lance.agent.feign.blood.pressure;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * 依赖来源
 *         <dependency>
 *             <groupId>com.yuehuijiankang.blood.pressure</groupId>
 *             <artifactId>blood-pressure-service-sdk</artifactId>
 *             <exclusions>
 *                 <exclusion>
 *                     <groupId>com.viatris.framework</groupId>
 *                     <artifactId>viatris-web</artifactId>
 *                 </exclusion>
 *             </exclusions>
 *         </dependency>
 */
@FeignClient(
    value = "blood-pressure-service",
    path = "/doctorWorkbench"
)
public interface DoctorWorkbenchServiceApi {

    @GetMapping({"getBindDoctorId"})
    Object getBindDoctorId(@RequestParam("patientId") Long var1);
}
