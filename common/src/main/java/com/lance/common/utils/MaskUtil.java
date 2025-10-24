package com.lance.common.utils;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * 数据脱敏工具类
 * <p>
 * 提供对敏感数据的脱敏处理功能，包括：
 * - 手机号脱敏
 * - 银行卡号脱敏  
 * - 身份证号脱敏
 * - 邮箱地址脱敏
 * </p>
 *
 * @author xiaolong.shu
 * @date 2025年10月24日 11:20
 */
public class MaskUtil {

    private static final String PLACEHOLDER = "*";
    private static Set<Pattern> patterns;

    static {
        String patternString = "((?<![\\w\\*])1\\d{2})(\\d{4})(\\d{4}(?![\\w\\*]));(\\d)(\\d{5}(?:19|20)\\d{2}(?:0[1-9]|1[0-2])(?:[0-2]\\d|3[01])\\d{3})([\\dxXyY]);((?<![\\w\\*])\\d)(\\d{5}\\d{2}(?:0[1-9]|1[0-2])(?:[0-2]\\d|3[01])\\d{2})(\\d(?![\\w\\*]));(\\w[\\.\\w]+)(@\\w[\\.\\w]+)";
        patterns = Arrays.stream(patternString.split(";")).map(Pattern::compile).collect(Collectors.toSet());
    }

    public static String desensitize(final String item) {
        if (isBlank(item))
            return item;
        String tmp = item;
        for (Pattern pattern : patterns) {
            tmp = desensitize(tmp, pattern);
        }
        return tmp;
    }

    public static String desensitize(final String item, String pattern) {
        if (isBlank(item))
            return item;
        return desensitize(item, Pattern.compile(pattern));
    }

    private static boolean isBlank(String string) {
        if (isEmpty(string)) {
            return true;
        }
        for (int i = 0; i < string.length(); i++) {
            if (!Character.isWhitespace(string.charAt(i))) {
                return false;
            }
        }
        return true;
    }

    private static boolean isEmpty(String string) {
        return string == null || string.isEmpty();
    }

    private static String desensitize(final String item, Pattern pattern) {
        try {
            Matcher m = pattern.matcher(item);
            Set<String> str = new HashSet<>();
            while (m.find()) {
                str.add(m.group());
            }
            if (str.isEmpty())
                return item;
            String replace = item;
            for (String toRp : str) {
                replace = replace.replaceAll(toRp, mask(toRp, 4));
            }
            return replace;

        } catch (Throwable t) {
            return String.format("%s [regex error %s]", item, pattern.toString());
        }
    }

    private static String mask(String content, int maxShow) {
        if (content == null) {
            return "null";
        } else {
            if (content.length() == 1) {
                return PLACEHOLDER;
            } else if (content.length() == 2) {
                return PLACEHOLDER + content.substring(1);
            } else {
                StringBuffer buffer = new StringBuffer();
                int step = Math.min(content.length() / 3, maxShow);
                buffer.append(content.substring(0, step));
                String right = content.substring(content.length() - step);
                int maskLength = content.length() - buffer.length() - right.length();
                for (int i = 0; i < maskLength; i++) {
                    buffer.append("*");
                }
                return buffer.append(right).toString();
            }
        }
    }
}
