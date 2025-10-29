package com.lance.mcpClient.api;

import jakarta.annotation.Resource;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/chatClient")
public class McpChatClientController {
    @Resource(name = "deepSeekMcpChatClient")
    ChatClient chatClient;


    @GetMapping("/generation")
    String generation(String userInput) {
        return chatClient.prompt().user(userInput).call().content();
    }

}