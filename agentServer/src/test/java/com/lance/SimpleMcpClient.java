///*
//* Copyright 2024 - 2024 the original author or authors.
//*
//* Licensed under the Apache License, Version 2.0 (the "License");
//* you may not use this file except in compliance with the License.
//* You may obtain a copy of the License at
//*
//* https://www.apache.org/licenses/LICENSE-2.0
//*
//* Unless required by applicable law or agreed to in writing, software
//* distributed under the License is distributed on an "AS IS" BASIS,
//* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//* See the License for the specific language governing permissions and
//* limitations under the License.
//*/
//package com.lance;
//
//import com.fasterxml.jackson.databind.JsonNode;
//import com.fasterxml.jackson.databind.ObjectMapper;
//import com.fasterxml.jackson.databind.node.ObjectNode;
//
//import java.net.URI;
//import java.net.http.HttpClient;
//import java.net.http.HttpRequest;
//import java.net.http.HttpResponse;
//import java.time.Duration;
//import java.util.Map;
//import java.util.concurrent.CompletableFuture;
//
///**
// * 基于Java内置HttpClient的简单MCP客户端实现
// * 替代HttpClientStreamableHttpTransport，避免依赖问题
// *
// * @author Lance
// */
//public class SimpleMcpClient {
//
//    private final HttpClient httpClient;
//    private final String baseUrl;
//    private final ObjectMapper objectMapper;
//    private int requestId = 1;
//
//    public SimpleMcpClient(String baseUrl) {
//        this.baseUrl = baseUrl;
//        this.httpClient = HttpClient.newBuilder()
//                .connectTimeout(Duration.ofSeconds(30))
//                .build();
//        this.objectMapper = new ObjectMapper();
//    }
//
//    /**
//     * 初始化MCP连接
//     */
//    public void initialize() {
//        System.out.println("MCP客户端初始化完成，连接到: " + baseUrl);
//    }
//
//    /**
//     * 发送ping请求
//     */
//    public void ping() {
//        try {
//            JsonNode response = sendRequest("ping", Map.of());
//            System.out.println("Ping响应: " + response);
//        } catch (Exception e) {
//            System.err.println("Ping失败: " + e.getMessage());
//        }
//    }
//
//    /**
//     * 获取可用工具列表
//     */
//    public JsonNode listTools() {
//        try {
//            return sendRequest("tools/list", Map.of());
//        } catch (Exception e) {
//            System.err.println("获取工具列表失败: " + e.getMessage());
//            return null;
//        }
//    }
//
//    /**
//     * 调用工具
//     */
//    public JsonNode callTool(String toolName, Map<String, Object> arguments) {
//        try {
//            Map<String, Object> params = Map.of(
//                "name", toolName,
//                "arguments", arguments
//            );
//            return sendRequest("tools/call", params);
//        } catch (Exception e) {
//            System.err.println("调用工具失败: " + e.getMessage());
//            return null;
//        }
//    }
//
//    /**
//     * 发送JSON-RPC请求
//     */
//    private JsonNode sendRequest(String method, Map<String, Object> params) throws Exception {
//        // 构建JSON-RPC请求
//        ObjectNode request = objectMapper.createObjectNode();
//        request.put("jsonrpc", "2.0");
//        request.put("id", requestId++);
//        request.put("method", method);
//
//        if (!params.isEmpty()) {
//            ObjectNode paramsNode = objectMapper.valueToTree(params);
//            request.set("params", paramsNode);
//        }
//
//        String requestBody = objectMapper.writeValueAsString(request);
//        System.out.println("发送请求: " + requestBody);
//
//        // 创建HTTP请求 - 尝试不同的端点路径
//        String[] endpoints = {"/mcp", "/api/mcp", "/tools", "/api/tools"};
//        JsonNode result = null;
//        Exception lastException = null;
//
//        for (String endpoint : endpoints) {
//            try {
//                HttpRequest httpRequest = HttpRequest.newBuilder()
//                        .uri(URI.create(baseUrl + endpoint))
//                        .header("Content-Type", "application/json")
//                        .header("Accept", "application/json")
//                        .POST(HttpRequest.BodyPublishers.ofString(requestBody))
//                        .timeout(Duration.ofSeconds(30))
//                        .build();
//
//                // 发送请求并获取响应
//                HttpResponse<String> response = httpClient.send(httpRequest, HttpResponse.BodyHandlers.ofString());
//
//                System.out.println("尝试端点: " + endpoint + ", 状态码: " + response.statusCode());
//
//                if (response.statusCode() == 200) {
//                    String responseBody = response.body();
//                    System.out.println("收到响应: " + responseBody);
//
//                    // 解析响应
//                    JsonNode responseNode = objectMapper.readTree(responseBody);
//
//                    // 检查是否有错误
//                    if (responseNode.has("error")) {
//                        JsonNode error = responseNode.get("error");
//                        throw new RuntimeException("MCP错误: " + error.get("message").asText());
//                    }
//
//                    result = responseNode.get("result");
//                    break; // 成功则跳出循环
//                } else {
//                    System.out.println("端点 " + endpoint + " 返回状态码: " + response.statusCode());
//                }
//            } catch (Exception e) {
//                lastException = e;
//                System.out.println("端点 " + endpoint + " 请求失败: " + e.getMessage());
//            }
//        }
//
//        if (result == null) {
//            throw new RuntimeException("所有端点都失败，最后一个错误: " +
//                (lastException != null ? lastException.getMessage() : "未知错误"));
//        }
//
//        return result;
//    }
//
//    /**
//     * 异步发送请求
//     */
//    public CompletableFuture<JsonNode> sendRequestAsync(String method, Map<String, Object> params) {
//        return CompletableFuture.supplyAsync(() -> {
//            try {
//                return sendRequest(method, params);
//            } catch (Exception e) {
//                throw new RuntimeException(e);
//            }
//        });
//    }
//
//    /**
//     * 关闭客户端
//     */
//    public void closeGracefully() {
//        System.out.println("MCP客户端已关闭");
//    }
//}
