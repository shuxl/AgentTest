/*
* Copyright 2024 - 2024 the original author or authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
* https://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/
package com.lance.agent.service.mcp;

import com.lance.agent.annotation.McpTool;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

/**
 * Function service providing basic arithmetic operations
 */
@Service
@McpTool("function-service")
public class FunctionService {

	/**
	 * Add two numbers
	 * @param a First number
	 * @param b Second number
	 * @return The sum of a and b
	 */
	@Tool(description = "Add two numbers and return the result")
	public double add(double a, double b) {
		System.out.println(">>>>>>Add: " + a + " + " + b);
		double result = a + b;
		System.out.println(">>>>>>Result: " + result);
		return result;
	}

	/**
	 * Subtract second number from first number
	 * @param a First number (minuend)
	 * @param b Second number (subtrahend)
	 * @return The difference of a and b
	 */
	@Tool(description = "Subtract second number from first number and return the result")
	public double subtract(double a, double b) {
		System.out.println(">>>>>>Subtract: " + a + " - " + b);
		double result = a - b;
		System.out.println(">>>>>>Result: " + result);
		return result;
	}

	/**
	 * Multiply two numbers
	 * @param a First number
	 * @param b Second number
	 * @return The product of a and b
	 */
	@Tool(description = "Multiply two numbers and return the result")
	public double multiply(double a, double b) {
		System.out.println(">>>>>>Multiply: " + a + " * " + b);
		double result = a * b;
		System.out.println(">>>>>>Result: " + result);
		return result;
	}

	/**
	 * Divide first number by second number
	 * @param a First number (dividend)
	 * @param b Second number (divisor)
	 * @return The quotient of a divided by b
	 * @throws IllegalArgumentException if divisor is zero
	 */
	@Tool(description = "Divide first number by second number and return the result")
	public double divide(double a, double b) {
		System.out.println(">>>>>>Divide: " + a + " / " + b);
		if (b == 0) {
			throw new IllegalArgumentException("Division by zero is not allowed");
		}
		double result = a / b;
		System.out.println(">>>>>>Result: " + result);
		return result;
	}


}
