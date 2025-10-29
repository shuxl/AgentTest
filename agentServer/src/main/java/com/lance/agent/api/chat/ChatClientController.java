package com.lance.agent.api.chat;

import jakarta.annotation.Resource;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/chatClient")
public class ChatClientController {
// https://docs.spring.io/spring-ai/reference/api/chatclient.html
//    @Resource
//    private DeepSeekChatModel deepSeekChatModel;

//    private final ChatClient chatClient;
    @Resource(name = "deepSeekChatClient")
    ChatClient deepSeekChatClient;
    @Resource(name = "zhiPuAiChatClient")
    ChatClient zhiPuAiChatClient;

//    @Autowired
//    public ChatClientController(@Qualifier("deepSeekChatClient") ChatClient deepSeekChatClient, @Qualifier("zhiPuAiChatClient") ChatClient zhiPuAiChatClient) {
//
//    }

    @GetMapping("/generation")
    String generation(String userInput, @RequestParam(value = "model", required = false,defaultValue = "deepSeek") String model) {
        ChatClient chatClient = model.equals("deepSeek") ? deepSeekChatClient : zhiPuAiChatClient;
        return chatClient.prompt().user(userInput).call().content();
    }

}