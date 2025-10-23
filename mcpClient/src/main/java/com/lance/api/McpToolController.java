package com.lance.api;

import io.modelcontextprotocol.client.McpSyncClient;
import io.modelcontextprotocol.spec.McpSchema;
import jakarta.annotation.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * MCP工具控制器
 * 提供REST API接口来调用所有MCP工具
 * 
 * @author lance
 */
@RestController
@RequestMapping("/api/mcp")
public class McpToolController {

    @Resource
    private List<McpSyncClient> mcpSyncClients;
    
    private McpSyncClient getMcpSyncClient() {
        if (mcpSyncClients == null || mcpSyncClients.isEmpty()) {
            throw new IllegalStateException("没有可用的MCP客户端");
        }
        return mcpSyncClients.get(0);
    }

    /**
     * 获取所有可用的MCP工具列表
     */
    @GetMapping("/tools")
    public ResponseEntity<Map<String, Object>> listTools() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            McpSyncClient client = getMcpSyncClient();
            McpSchema.ListToolsResult toolsResult = client.listTools();
            result.put("tools", toolsResult.tools());
        } catch (Exception e) {
            result.put("error", "获取工具列表失败: " + e.getMessage());
        }
        
        return ResponseEntity.ok(result);
    }

    /**
     * 调用天气预测工具
     */
    @PostMapping("/weather/forecast")
    public ResponseEntity<Map<String, Object>> getWeatherForecast(
            @RequestParam double latitude,
            @RequestParam double longitude) {
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            Map<String, Object> arguments = Map.of(
                "latitude", latitude,
                "longitude", longitude
            );
            
            McpSyncClient client = getMcpSyncClient();
            McpSchema.CallToolResult toolResult = client.callTool(
                new McpSchema.CallToolRequest("getWeatherForecastByLocation", arguments)
            );
            
            result.put("result", toolResult);
        } catch (Exception e) {
            result.put("error", "调用天气预测工具失败: " + e.getMessage());
        }
        
        return ResponseEntity.ok(result);
    }

    /**
     * 获取天气警报
     */
    @PostMapping("/weather/alerts")
    public ResponseEntity<Map<String, Object>> getWeatherAlerts(
            @RequestParam String state) {
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            Map<String, Object> arguments = Map.of("state", state);
            
            McpSyncClient client = getMcpSyncClient();
            McpSchema.CallToolResult toolResult = client.callTool(
                new McpSchema.CallToolRequest("getAlerts", arguments)
            );
            
            result.put("result", toolResult);
        } catch (Exception e) {
            result.put("error", "调用天气警报工具失败: " + e.getMessage());
        }
        
        return ResponseEntity.ok(result);
    }

    /**
     * 通用工具调用接口
     */
    @PostMapping("/tools/call")
    public ResponseEntity<Map<String, Object>> callTool(
            @RequestParam String toolName,
            @RequestBody(required = false) Map<String, Object> arguments) {
        
        Map<String, Object> result = new HashMap<>();
        
        if (arguments == null) {
            arguments = new HashMap<>();
        }
        
        try {
            McpSyncClient client = getMcpSyncClient();
            McpSchema.CallToolResult toolResult = client.callTool(
                new McpSchema.CallToolRequest(toolName, arguments)
            );
            
            result.put("result", toolResult);
        } catch (Exception e) {
            result.put("error", "调用工具 " + toolName + " 失败: " + e.getMessage());
        }
        
        return ResponseEntity.ok(result);
    }

    /**
     * 获取MCP客户端状态
     */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getStatus() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            McpSyncClient client = getMcpSyncClient();
            McpSchema.ListToolsResult toolsResult = client.listTools();
            result.put("status", "connected");
            result.put("tools_count", toolsResult.tools().size());
            result.put("tools", toolsResult.tools().stream()
                .map(McpSchema.Tool::name)
                .toList());
        } catch (Exception e) {
            result.put("status", "error");
            result.put("error", e.getMessage());
        }
        
        return ResponseEntity.ok(result);
    }

    /**
     * 测试所有可用工具
     */
    @PostMapping("/test/all")
    public ResponseEntity<Map<String, Object>> testAllTools() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            // 获取工具列表
            McpSyncClient client = getMcpSyncClient();
            McpSchema.ListToolsResult toolsResult = client.listTools();
            
            // 测试每个工具
            for (McpSchema.Tool tool : toolsResult.tools()) {
                String toolName = tool.name();
                Map<String, Object> toolResult = new HashMap<>();
                
                try {
                    // 根据工具名称使用不同的测试参数
                    Map<String, Object> testArguments = getTestArguments(toolName);
                    
                    McpSchema.CallToolResult callResult = client.callTool(
                        new McpSchema.CallToolRequest(toolName, testArguments)
                    );
                    
                    toolResult.put("status", "success");
                    toolResult.put("result", callResult);
                } catch (Exception e) {
                    toolResult.put("status", "error");
                    toolResult.put("error", e.getMessage());
                }
                
                result.put(toolName, toolResult);
            }
        } catch (Exception e) {
            result.put("error", "获取工具列表失败: " + e.getMessage());
        }
        
        return ResponseEntity.ok(result);
    }

    /**
     * 根据工具名称获取测试参数
     */
    private Map<String, Object> getTestArguments(String toolName) {
        return switch (toolName) {
            case "getWeatherForecastByLocation" -> Map.of(
                "latitude", 47.6062,
                "longitude", -122.3321
            );
            case "getAlerts" -> Map.of("state", "NY");
            default -> new HashMap<>();
        };
    }
}
