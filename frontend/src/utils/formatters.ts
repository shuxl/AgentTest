/**
 * 格式化工具函数
 */
import dayjs from 'dayjs';

/**
 * 格式化时间戳为可读时间
 */
export function formatTimestamp(timestamp: number): string {
  const now = dayjs();
  const time = dayjs(timestamp);
  const diff = now.diff(time, 'minute');

  if (diff < 1) {
    return '刚刚';
  } else if (diff < 60) {
    return `${diff}分钟前`;
  } else if (diff < 1440) {
    return `${Math.floor(diff / 60)}小时前`;
  } else if (diff < 10080) {
    return `${Math.floor(diff / 1440)}天前`;
  } else {
    return time.format('YYYY-MM-DD HH:mm');
  }
}

/**
 * 格式化日期时间
 */
export function formatDateTime(timestamp: number): string {
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss');
}

/**
 * 格式化日期
 */
export function formatDate(timestamp: number): string {
  return dayjs(timestamp).format('YYYY-MM-DD');
}

