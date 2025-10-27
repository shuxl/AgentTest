package com.lance.agent.model;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.lance.agent.model.enums.ActionMode;
import com.lance.agent.model.enums.ChatTypeEnum;
import com.lance.agent.model.enums.HandlerStatus;
import lombok.Data;

import java.util.Date;

@Data
@TableName("message_handle")
public class MessageHandle {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String msgId;
    private Long userId;
    private Date sendTime;
    private ChatTypeEnum chatType;
    private Long duration;

    /**
     * 群聊消息：群 ID
     * 私聊消息：小助手企微用户 ID
     */
    private String targetId;

    private String handler;
    private ActionMode actionMode;
    private String requestData;
    private String responseData;
    private HandlerStatus handlerStatus;
    private String traceId;
    private Date createTime;
    private Date updateTime;

}
