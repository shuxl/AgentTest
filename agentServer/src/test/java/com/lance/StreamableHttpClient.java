///*
// * Copyright 2024 - 2024 the original author or authors.
// *
// * Licensed under the Apache License, Version 2.0 (the "License");
// * you may not use this file except in compliance with the License.
// * You may obtain a copy of the License at
// *
// * https://www.apache.org/licenses/LICENSE-2.0
// *
// * Unless required by applicable law or agreed to in writing, software
// * distributed under the License is distributed on an "AS IS" BASIS,
// * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// * See the License for the specific language governing permissions and
// * limitations under the License.
// */
//package com.lance;
//
//import com.fasterxml.jackson.databind.JsonNode;
//
//import java.util.HashMap;
//import java.util.Map;
//
///**
// * 使用SimpleMcpClient替代HttpClientStreamableHttpTransport的测试类
// * 解决依赖问题，使用Java内置HttpClient实现MCP客户端
// *
// * @author Lance
// */
//public class StreamableHttpClient {
//
//    public static void main(String[] args) {
//
//        // 使用新的SimpleMcpClient替代HttpClientStreamableHttpTransport
//        SimpleMcpClient client = new SimpleMcpClient("http://localhost:9092");
//
//        client.initialize();
//
//        client.ping();
//
//        // 获取可用工具列表
//        JsonNode toolsList = client.listTools();
//        System.out.println("Available Tools = " + toolsList);
//
//        // 调用天气预测工具
//        JsonNode weatherForecastResult = client.callTool("getWeatherForecastByLocation",
//                Map.of("latitude", "47.6062", "longitude", "-122.3321"));
//        System.out.println(">>>>>>Weather Forecast: " + weatherForecastResult);
//
//        // 调用系统信息工具
//        JsonNode getSystemInfoResult = client.callTool("getSystemInfo", new HashMap<>());
//        System.out.println(">>>>>>> getSystemInfo = " + getSystemInfoResult);
//
//        // 调用数字相加工具
//        JsonNode addNumbersResult = client.callTool("addNumbers",
//                Map.of("num1", 47, "num2", 88));
//        System.out.println(">>>>>>> addNumbers = " + addNumbersResult);
//
//        client.closeGracefully();
//    }
//
//}
