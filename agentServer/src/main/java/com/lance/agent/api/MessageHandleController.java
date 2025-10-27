package com.lance.agent.api;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.lance.agent.model.MessageHandle;
import com.lance.agent.service.agent.MessageHandleService;
import com.lance.common.model.ApiResult;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.List;

/**
 * 消息处理控制器
 * 
 * @author lance
 */
@RestController
@RequestMapping("/api/message-handle")
public class MessageHandleController {

    @Resource
    private MessageHandleService messageHandleService;

    /**
     * 创建消息处理记录
     */
    @PostMapping
    public ApiResult<MessageHandle> create(@RequestBody MessageHandle messageHandle) {
        if (messageHandle.getCreateTime() == null) {
            messageHandle.setCreateTime(new Date());
        }
        if (messageHandle.getUpdateTime() == null) {
            messageHandle.setUpdateTime(new Date());
        }
        boolean success = messageHandleService.save(messageHandle);
        if (success) {
            return ApiResult.success("创建成功", messageHandle);
        }
        return ApiResult.fail("创建失败");
    }

    /**
     * 根据ID查询消息处理记录
     */
    @GetMapping("/{id}")
    public ApiResult<MessageHandle> getById(@PathVariable Long id) {
        MessageHandle messageHandle = messageHandleService.getById(id);
        if (messageHandle != null) {
            return ApiResult.success(messageHandle);
        }
        return ApiResult.fail("未找到该记录");
    }

    /**
     * 根据消息ID查询消息处理记录
     */
    @GetMapping("/msgId/{msgId}")
    public ApiResult<MessageHandle> getByMsgId(@PathVariable String msgId) {
        MessageHandle messageHandle = messageHandleService.getByMsgId(msgId);
        if (messageHandle != null) {
            return ApiResult.success(messageHandle);
        }
        return ApiResult.fail("未找到该记录");
    }

    /**
     * 根据用户ID查询消息处理记录列表
     */
    @GetMapping("/user/{userId}")
    public ApiResult<List<MessageHandle>> getByUserId(@PathVariable Long userId) {
        List<MessageHandle> list = messageHandleService.getByUserId(userId);
        return ApiResult.success(list);
    }

    /**
     * 更新消息处理记录
     */
    @PutMapping("/{id}")
    public ApiResult<MessageHandle> update(@PathVariable Long id, @RequestBody MessageHandle messageHandle) {
        if (messageHandle.getId() == null) {
            messageHandle.setId(id);
        }
        if (messageHandle.getUpdateTime() == null) {
            messageHandle.setUpdateTime(new Date());
        }
        boolean success = messageHandleService.updateById(messageHandle);
        if (success) {
            return ApiResult.success("更新成功", messageHandle);
        }
        return ApiResult.fail("更新失败");
    }

    /**
     * 删除消息处理记录
     */
    @DeleteMapping("/{id}")
    public ApiResult<Void> delete(@PathVariable Long id) {
        boolean success = messageHandleService.removeById(id);
        if (success) {
            return ApiResult.success("删除成功");
        }
        return ApiResult.fail("删除失败");
    }

    /**
     * 分页查询消息处理记录
     */
    @GetMapping("/page")
    public ApiResult<Page<MessageHandle>> page(
            @RequestParam(defaultValue = "1") Integer current,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String handler,
            @RequestParam(required = false) Long userId) {
        
        LambdaQueryWrapper<MessageHandle> wrapper = new LambdaQueryWrapper<>();
        
        if (handler != null && !handler.isEmpty()) {
            wrapper.like(true, MessageHandle::getHandler, handler);
        }
        
        if (userId != null) {
            wrapper.eq(true, MessageHandle::getUserId, userId);
        }
        
        wrapper.orderByDesc(true, MessageHandle::getCreateTime);
        
        Page<MessageHandle> page = new Page<>(current, size);
        Page<MessageHandle> result = messageHandleService.page(page, wrapper);
        
        return ApiResult.success(result);
    }

    /**
     * 查询所有消息处理记录
     */
    @GetMapping("/list")
    public ApiResult<List<MessageHandle>> list() {
        List<MessageHandle> list = messageHandleService.list();
        return ApiResult.success(list);
    }
}

