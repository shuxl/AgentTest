package com.lance.agent.service.agent;

import com.baomidou.mybatisplus.extension.service.IService;
import com.lance.agent.model.MessageHandle;

/**
 * 消息处理服务接口
 * 
 * @author lance
 */
public interface MessageHandleService extends IService<MessageHandle> {
    
    /**
     * 根据消息ID查询消息处理记录
     * 
     * @param msgId 消息ID
     * @return 消息处理记录
     */
    MessageHandle getByMsgId(String msgId);
    
    /**
     * 根据用户ID查询消息处理记录
     * 
     * @param userId 用户ID
     * @return 消息处理记录
     */
    java.util.List<MessageHandle> getByUserId(Long userId);
}

