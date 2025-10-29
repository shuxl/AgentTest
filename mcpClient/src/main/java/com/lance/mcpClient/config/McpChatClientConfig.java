package com.lance.mcpClient.config;

import io.modelcontextprotocol.client.McpSyncClient;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.ai.deepseek.DeepSeekChatModel;
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class McpChatClientConfig {

    @Bean
    @ConditionalOnProperty(prefix = "spring.ai.deepseek", name = "api-key")
    public ChatClient deepSeekMcpChatClient(DeepSeekChatModel chatModel, List<McpSyncClient> mcpSyncClients) {
        return ChatClient.builder(chatModel)
                .defaultSystem("""
                        You are a helpful assistant with access to mathematical calculation tools.
                        When users ask you to perform arithmetic operations (addition, subtraction, multiplication, division) or any mathematical calculations,
                        you should use the available tools (add, subtract, multiply, divide) to solve them accurately.
                        Always use tools for calculations rather than doing them manually.""")
                .defaultToolCallbacks(new SyncMcpToolCallbackProvider(mcpSyncClients))
                .defaultAdvisors(MessageChatMemoryAdvisor.builder(MessageWindowChatMemory.builder().build()).build())
                .build();
//        return ChatClient.create(chatModel);
    }

//    @Bean
//    @ConditionalOnBean(value = {DeepSeekChatModel.class, McpSyncClient.class})
//    public ChatClient zhiPuAiChatClient(ZhiPuAiChatModel chatModel) {
//        return ChatClient.create(chatModel);
//    }
}