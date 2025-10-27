package com.lance.agent.service.agent.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.lance.agent.mapper.MessageHandleMapper;
import com.lance.agent.model.MessageHandle;
import com.lance.agent.service.agent.MessageHandleService;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 消息处理服务实现类
 * 
 * @author lance
 */
@Service
public class MessageHandleServiceImpl extends ServiceImpl<MessageHandleMapper, MessageHandle> implements MessageHandleService {

    @Override
    public MessageHandle getByMsgId(String msgId) {
        LambdaQueryWrapper<MessageHandle> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(true, MessageHandle::getMsgId, msgId);
        return this.getOne(wrapper);
    }

    @Override
    public List<MessageHandle> getByUserId(Long userId) {
        LambdaQueryWrapper<MessageHandle> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(true, MessageHandle::getUserId, userId)
               .orderByDesc(true, MessageHandle::getCreateTime);
        return this.list(wrapper);
    }
}

