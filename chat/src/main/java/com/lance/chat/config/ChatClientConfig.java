package com.lance.chat.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.deepseek.DeepSeekChatModel;
import org.springframework.ai.zhipuai.ZhiPuAiChatModel;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ChatClientConfig {

    @Bean
    public ChatClient deepSeekChatClient(DeepSeekChatModel chatModel) {
        return ChatClient.create(chatModel);
    }

    @Bean
    public ChatClient zhiPuAiChatClient(ZhiPuAiChatModel chatModel) {
        return ChatClient.create(chatModel);
    }
}