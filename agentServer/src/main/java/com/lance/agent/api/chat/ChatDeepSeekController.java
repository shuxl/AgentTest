package com.lance.agent.api.chat;

import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.ChatOptions;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.deepseek.DeepSeekAssistantMessage;
import org.springframework.ai.deepseek.DeepSeekChatModel;
import org.springframework.ai.deepseek.DeepSeekChatOptions;
import org.springframework.ai.deepseek.api.DeepSeekApi;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

@RestController
@RequestMapping("/api/chat/deepSeek")
public class ChatDeepSeekController {
    // https://docs.spring.io/spring-ai/reference/api/chat/deepseek-chat.html
    @Autowired
    @Qualifier("deepSeekChatModel")
    private DeepSeekChatModel chatModel;

    @GetMapping("/ai/generate")
    public Map generate(@RequestParam(value = "message", defaultValue = "请讲个笑话") String message) {
        return Map.of("generation", chatModel.call(message));
    }

    @GetMapping("/ai/generateStream")
	public Flux<ChatResponse> generateStream(@RequestParam(value = "message", defaultValue = "请讲个笑话") String message) {
        var prompt = new Prompt(new UserMessage(message));
        return chatModel.stream(prompt);
    }

    @GetMapping("/ai/generatePythonCode")
    public String generatePythonCode(@RequestParam(value = "message", defaultValue = "请写一个快速排序算法（python）") String message) {
        UserMessage userMessage = new UserMessage(message);
        Message assistantMessage = DeepSeekAssistantMessage.prefixAssistantMessage("```python\\n");
        Prompt prompt = new Prompt(List.of(userMessage, assistantMessage), ChatOptions.builder().stopSequences(List.of("```")).build());
        ChatResponse response = chatModel.call(prompt);
        return response.getResult().getOutput().getText();
    }

    @GetMapping("/ai/generateReasoning")
    public String generateReasoning(@RequestParam(value = "message", defaultValue = "9.11 and 9.8, which is greater?") String message) {
        return deepSeekReasonerMultiRoundExample();
    }

    public String deepSeekReasonerMultiRoundExample() {
        List<Message> messages = new ArrayList<>();
        messages.add(new UserMessage("9.11 和 9.8, 谁更大?"));
        DeepSeekChatOptions promptOptions = DeepSeekChatOptions.builder()
                .model(DeepSeekApi.ChatModel.DEEPSEEK_REASONER.getValue())
                .build();

        Prompt prompt = new Prompt(messages, promptOptions);
        ChatResponse response = chatModel.call(prompt);

        DeepSeekAssistantMessage deepSeekAssistantMessage = (DeepSeekAssistantMessage) response.getResult().getOutput();
        String reasoningContent = deepSeekAssistantMessage.getReasoningContent();
        System.err.println(reasoningContent);
        String text = deepSeekAssistantMessage.getText();

        messages.add(new AssistantMessage(Objects.requireNonNull(text)));
        messages.add(new UserMessage("“strawberry”这个单词里有几个r ？"));
        Prompt prompt2 = new Prompt(messages, promptOptions);
        ChatResponse response2 = chatModel.call(prompt2);

        DeepSeekAssistantMessage deepSeekAssistantMessage2 = (DeepSeekAssistantMessage) response2.getResult().getOutput();
        String reasoningContent2 = deepSeekAssistantMessage2.getReasoningContent();
        System.err.println("");
        System.err.println(">>>>>>>>>");
        System.err.println("");
        System.err.println(reasoningContent2);
        return deepSeekAssistantMessage2.getText();
    }
}