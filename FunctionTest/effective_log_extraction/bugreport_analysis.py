import re
import datetime
import json

class LogProcessor:
    def __init__(self, log_filename, keywords_filename):
        # 初始化日志文件和关键词文件名
        self.log_filename = log_filename
        self.keywords_filename = keywords_filename
        # 编译正则表达式，用于匹配日志中的时间戳
        self.timestamp_pattern = re.compile(r'(\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        # 加载关键词
        self.keywords = self.load_keywords()

    def load_keywords(self):
        # 从JSON文件中加载关键词
        with open(self.keywords_filename, 'r', encoding='utf-8') as file:
            keywords_data = json.load(file)
        return keywords_data['keywords']

    def parse_log_timestamp(self, line):
        # 解析日志行中的时间戳
        match = self.timestamp_pattern.search(line)
        if match:
            timestamp_str = match.group(1)
            # 将字符串转换为datetime对象，并设置为当前年份
            return datetime.datetime.strptime(timestamp_str, '%m-%d %H:%M:%S').replace(year=datetime.datetime.now().year)
        return None

    def extract_logs(self, target_time_str, pre_delta_minutes=3, post_delta_minutes=3):
        # 从日志文件中提取特定时间范围内的日志
        with open(self.log_filename, 'r', encoding="utf-8") as file:
            lines = file.readlines()

        # 将目标时间字符串转换为datetime对象
        target_time = datetime.datetime.strptime(target_time_str, '%m-%d %H:%M:%S').replace(year=datetime.datetime.now().year)
        # 计算前后时间范围
        start_time = target_time - datetime.timedelta(minutes=pre_delta_minutes)
        end_time = target_time + datetime.timedelta(minutes=post_delta_minutes)

        result_lines = []  # 存储提取的日志行
        step = 2000  # 每次处理的行数
        total_lines = len(lines)  # 日志总行数
        i = 0  # 行索引

        while i < total_lines:
            # 获取当前位置和下一步位置的时间戳
            current_time = self.parse_log_timestamp(lines[i])
            next_i = min(i + step, total_lines - 1)
            next_time = self.parse_log_timestamp(lines[next_i])

            # 检查当前时间或下一时间是否在目标范围内
            if (current_time and start_time <= current_time <= end_time) or (next_time and start_time <= next_time <= end_time):
                # 如果在范围内，添加到结果列表
                result_lines.extend(lines[i:next_i + 1])

            i += step  # 移动到下一步

        return result_lines  # 返回提取的日志行

    def filter_logs_by_keywords(self, logs):
        # 根据关键词过滤日志行
        filtered_logs = []
        for line in logs:
            # 如果行中包含任何关键词，则添加到过滤列表
            if any(keyword in line for keyword in self.keywords):
                filtered_logs.append(line)
        return filtered_logs

    def process_logs(self, target_time_str, pre_delta_minutes=3, post_delta_minutes=2, output_filename='filtered_output.txt'):
        # 主处理方法，提取并过滤日志，然后将结果写入输出文件
        logs = self.extract_logs(target_time_str, pre_delta_minutes, post_delta_minutes)
        filtered_logs = self.filter_logs_by_keywords(logs)
        # 将过滤后的日志写入输出文件
        with open(output_filename, 'w', encoding="utf-8") as output_file:
            output_file.writelines(filtered_logs)

# 示例使用
if __name__ == "__main__":
    log_filename = 'bugreport-goku-UKQ1.240116.001-2024-07-06-22-06-59.txt'
    keywords_filename = 'voicetrigger_keywords.json'
    target_time_str = '07-06 22:04:40'
    
    # 创建LogProcessor实例并处理日志
    log_processor = LogProcessor(log_filename, keywords_filename)
    log_processor.process_logs(target_time_str, pre_delta_minutes=3, post_delta_minutes=3, output_filename='new_filtered_output.txt')
