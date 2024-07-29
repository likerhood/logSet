import json
import re
import tkinter
import time
import datetime
from tkinter import messagebox



class LogFilePro:
    def __init__(self, file_path, result_text, target_time):
        self.file_path = file_path
        self.result_text = result_text
        # 目标时间
        self.target_time = target_time
        # 日志关键词
        self.keywords_filename = 'voicetrigger_keywords.json'
        self.keywords = []
        self.load_keywords()

        # 关键日志记录
        self.log_lines = []
        # 日志时间匹配
        self.keylog_time = ""
        # 全局日志扫描
        self.global_log_lines = []

        # 日志事件分类
        self.event_list = []
        self.voice_trigger_scheme = None
        self.voice_trigger_version = ''
        self.build_date = ''
        self.device_code = ''
        # self.device_name = ''
        self.phone_name = ''
        self.voice_print_engine_version = ''
        # self.wakeup_engine_version = ''

        # 未收到一级唤醒事件原因
        self.microphone_error = []
        self.switcher_error = []
        # 二级唤醒失败原因
        self.second_ladder_fail = []
        # 录制失败原因
        self.record_fail = []
        # 录制失败的关键日志记录
        self.record_fail_log = []
        
        

    # 加载json文件的日志关键词
    def load_keywords(self):
        # 从JSON文件中加载关键词
        with open(self.keywords_filename, 'r', encoding='utf-8') as file:
            keywords_data = json.load(file)
        self.keywords = keywords_data['keywords']


    # 全局搜索遍历
    def global_search(self):
        pass

    # 分析日志并输出日志结果
    def start_process(self):

        # 输入问题发生时间
        print("self.target_time", self.target_time)
        if re.match(r'\d{2}-\d{2} \d{2}:\d{2}:\d{2}', self.target_time):
            # messagebox.showinfo(title='日期输入', message=f'您输入的日期时间是: {self.target_time}')
            # # 这里可以添加处理输入日期时间的逻辑
            print(f'输入日期时间: {self.target_time}')
        else:
            # 全局搜索
            self.global_search()
            messagebox.showwarning(title='格式错误', message='请输入正确的日期 (例如07-26 22:01:00)')
            return

        # 读取日志文件
        self.read_log_file()

        # 未收到一级唤醒事件
        if len(self.event_list) == 0:
            if len(self.record_fail) != 0:
                self.analysis_record_fail()
            else:
                self.result_text.insert(tkinter.END, '录制唤醒词成功\n')
                self.result_text.insert(tkinter.END, '未收到一级唤醒事件！\n\n')
                # 在这里继续分析具体未收到一级唤醒事件的原因
                self.analysis_first_wakelose_event()
                # if not self.file_path.startswith('bugReport-'):
                #     self.result_text.insert(tkinter.END, open(self.file_path, encoding='utf-8', errors='ignore').read())
                self.result_text.insert(tkinter.END, self.log_lines)

        # 收到一级唤醒事件
        if self.voice_trigger_scheme == 'MTK' or self.voice_trigger_scheme == 'MTK自研':
            self.process_mtk()
        elif self.voice_trigger_scheme == '自研E':
            self.process_e()
        elif self.voice_trigger_scheme == '高通':
            self.process_qualcomm()
        else:
            self.voice_trigger_scheme = ''

        text = "\n\n\n 问题发生时间前后三分钟的关键日志输出如下，可供检查和分析日志问题：\n\n"
        self.result_text.insert(tkinter.END, text)
        self.result_text.insert(tkinter.END, self.log_lines)


    def check_switch_on(self):
        '''
        function: 
         1. 检查开关是否打开
         2. 将相关日志保存起来
        return:
         布尔值
        
        '''
        return False
    

    def check_micphone(self):
        '''
            mic被占用
                AudioRecord: start没有packageName对应的AudioRecord: stop
                例如：
                05-06 10:22:42.760 10179 14344 15668 W AudioRecord: start mSessionID=257 start(63): sync event 0 trigger session 0  packageName: com.miui.voiceassist
            speaker增益导致无法唤醒
                在"AudioTrack: start"和"AudioTrack: stop"之间（packageName一致），存在无法唤醒
                例如：
                05-06 10:33:06.786 media  3029 22453 W AudioTrack: start(106): prior state:STATE_STOPPED packageName: com.miui.player
                05-06 10:33:16.907 media  3029 22453 W AudioTrack: stop(sessionID=401), packageName: com.miui.player
            
        '''
        flag = False
        # audio_record变量
        audio_packageName_record = {}
        audio_record = []
        issues_record = []
        # audio_track变量
        audio_packageName_track = {}
        audio_track = []
        issues_track = []
        packageName_pattern = re.compile(r'packageName: (\S+)')
        
        # 遍历日志
        for line in self.log_lines:
            if re.search('AudioRecord: start', line) is not None:
                audio_record.append(line)
                start_package = packageName_pattern.search(line)
                if start_package:
                    package_name = start_package.group(1)
                    if package_name not in audio_packageName_record:
                        audio_packageName_record[package_name] = []
                    audio_packageName_record[package_name].append(line)
            elif re.search('AudioRecord: stop', line) is not None:
                audio_record.append(line)
                stop_package = packageName_pattern.search(line)
                if stop_package:
                    package_name = stop_package.group(1)
                    if package_name in audio_packageName_record and audio_packageName_record[package_name]:
                        audio_packageName_record[package_name].pop(0)
                    # else:
                    #     issues_record.append(line)
            elif re.search('AudioTrack: start', line) is not None:
                audio_track.append(line)
                start_package = packageName_pattern.search(line)
                if start_package:
                    package_name = start_package.group(1)
                    if package_name not in audio_packageName_track:
                        audio_packageName_track[package_name] = []
                    audio_packageName_track[package_name].append(line)
            elif re.search('AudioTrack: stop', line) is not None:
                audio_track.append(line)
                stop_package = packageName_pattern.search(line)
                if stop_package:
                    package_name = stop_package.group(1)
                    if package_name in audio_packageName_track and audio_packageName_track[package_name]:
                        audio_packageName_track[package_name].pop(0)
                    # else:
                    #     issues_track.append(line)

        # 收集record所有没有对应stop的start日志
        for package_name, starts in audio_packageName_record.items():
            for start in starts:
                issues_record.append(start)

        # 收集track所有没有对应stop的start日志
        for package_name, starts in audio_packageName_track.items():
            for start in starts:
                issues_track.append(start)
        if len(issues_record) != 0:
            self.microphone_error.append("mic被占用\n")
            # 将关键日志输出
            for item in issues_record:
                self.microphone_error.append(item)
            self.microphone_error.append("-------------------------------------------\n")
            self.microphone_error.append("check——全部日志输出：在AudioTrack: start和AudioTrack: stop之间（packageName一致），存在无法唤醒\n")
            # 将全部有关日志输出，便于检查
            for item in audio_record:
                self.microphone_error.append(item)
            self.microphone_error.append("\n\n ------------------------------------------------------\n")
            flag = True
        if len(issues_track) != 0:
            self.microphone_error.append("speaker增益导致无法唤醒\n")
            # 将关键日志输出
            for item in issues_track:
                self.microphone_error.append(item)
            self.microphone_error.append("-------------------------------------------\n")
            self.microphone_error.append("check——全部日志输出：AudioRecord: start没有packageName对应的AudioRecord: stop\n")
            # 将全部有关日志输出，便于检查
            for item in audio_track:
                self.microphone_error.append(item)
            self.microphone_error.append("\n\n ------------------------------------------------------\n")
            flag = True

        return flag



    # 未唤醒一级事件的原因分析
    def analysis_first_wakelose_event(self):
        
        # 开关问题分析
        is_switch_on = False
        is_micphone_error = False
        is_switch_on= self.check_switch_on()

        # 不是开关问题,则分析其他原因
        if is_switch_on == False:
            is_micphone_error = self.check_micphone()

        # 开关问题
        reason_show = []
        if(is_switch_on == True):
            reason_show.append("开关问题, 呼唤小爱时语音唤醒未打开\n")
            reason_show.extend(self.switcher_error)
        elif(is_micphone_error == True):
            reason_show.append("mic或者speaker增益问题，未收到一级唤醒事件\n")
            reason_show.extend(self.microphone_error)
        else:
            reason_show.append("其他原因\n")
        self.result_text.insert(tkinter.END, reason_show)



    # 提取时间戳
    def parse_log_timestamp(self, line):
        # 解析日志行中的时间戳
        timestamp_pattern = re.compile(r'(\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        match = timestamp_pattern.search(line)
        if match:
            timestamp_str = match.group(1)
            # 将字符串转换为datetime对象，并设置为当前年份
            return datetime.datetime.strptime(timestamp_str, '%m-%d %H:%M:%S').replace(year=datetime.datetime.now().year)
        return None

    # 获取目标时间附近是日志
    def extract_effective_logs(self):
        file = open(self.file_path, encoding='utf-8', errors='ignore')
        log_file = file.readlines()
        # 将目标时间字符串转换为datetime对象
        target_time = datetime.datetime.strptime(self.target_time, '%m-%d %H:%M:%S').replace(year=datetime.datetime.now().year)
        # 计算前后时间范围
        start_time = target_time - datetime.timedelta(minutes=3)
        end_time = target_time + datetime.timedelta(minutes=3)
        print("target_time :", target_time)

        '''
        1. 筛选出有效时间范围内的全部日志
        '''
        result_lines = []  # 存储提取的日志行
        step = 2000  # 每次处理的行数
        total_lines = len(log_file)  # 日志总行数
        i = 0  # 行索引
        while i < total_lines:
            # 获取当前位置和下一步位置的时间戳
            current_time = self.parse_log_timestamp(log_file[i])
            next_i = min(i + step, total_lines - 1)
            next_time = self.parse_log_timestamp(log_file[next_i])
            # 检查当前时间或下一时间是否在目标范围内
            if (current_time and start_time <= current_time <= end_time) or (next_time and start_time <= next_time <= end_time):
                # 如果在范围内，添加到结果列表
                result_lines.extend(log_file[i:next_i + 1])
            i += step  # 移动到下一步

        '''
        2. 筛选具有关键词的日志
        '''
        self.log_lines = []
        for line in result_lines:
            # 如果行中包含任何关键词，则添加到过滤列表
            if any(keyword in line for keyword in self.keywords):
                self.log_lines.append(line)

        print("result_lines len", len(result_lines))
        print("self.log_lines len", len(self.log_lines))
        

    # 读取文件
    def read_log_file(self):

        self.extract_effective_logs()
        rows = len(self.log_lines)
        is_processed_info = False
        is_get_package_info = False
        is_get_devie_code = False
        i = 0
        cnt = 10
        while i < rows:
            if re.search('rice volume too low', self.log_lines[i]) is not None:
                reason = '唤醒时record增益导致的无法唤醒 \n'
                self.second_ladder_fail.append(reason)
            if re.search('verifyVoicePrintData: registerState=13', self.log_lines[i]) is not None:
                reason = '录制唤醒词失败\n原因：录制时record增益问题导致录制失败 \n\n'
                self.record_fail.append(reason)
                self.record_fail_key_logs(self.record_fail_log, i, cnt)
                i += cnt
            elif re.search('MTK-VowUtils: send voice Command', self.log_lines[i]) is not None:
                reason = '录制唤醒词失败\n原因：未知 \n'
                self.record_fail.append(reason)
                self.record_fail_key_logs(self.record_fail_log, i, cnt)
                i += cnt


            if re.search('onRecognition:', self.log_lines[i]) is None:
                i += 1
                continue
            # 找到一次一级事件 可以判断MTK方案和MTK自研
            if re.search('GenericRecognitionEvent', self.log_lines[i]) is not None:
                self.voice_trigger_scheme = 'MTK'
            if re.search('MTK', self.log_lines[i]) is not None:
                self.voice_trigger_scheme = 'MTK自研'
            log_list = [self.log_lines[i]]
            while i < rows:
                i += 1
                if i >= rows:
                    break

                if re.search('rice volume too low', self.log_lines[i]) is not None:
                    reason = '唤醒时record增益导致的无法唤醒 \n'
                    self.second_ladder_fail.append(reason)
                if self.voice_trigger_scheme is None and re.search('getSoundModel:', self.log_lines[i]) is not None:
                    if re.search('default', self.log_lines[i]) is not None:
                        self.voice_trigger_scheme = '自研E'
                    elif re.search('小爱', self.log_lines[i]) is not None:
                        self.voice_trigger_scheme = '高通'

                if re.search('setActive = -1000', self.log_lines[i]) is not None or re.search('commandId',
                                                                                         self.log_lines[i]) is not None:
                    if re.search('XATX', self.log_lines[i]) is not None or \
                            (re.search('0', self.log_lines[i]) is not None and re.search('false', self.log_lines[i]) is not None):
                        log_list.insert(0, '小爱同学')
                    elif re.search('UDK', self.log_lines[i]) is not None or \
                            (re.search('0', self.log_lines[i]) is not None and re.search('true', self.log_lines[i]) is not None):
                        log_list.insert(0, '小爱自定义')
                    elif re.search('FindPhone', self.log_lines[i]) is not None or re.search('1', self.log_lines[i]) is not None:
                        log_list.insert(0, '小爱你在哪')

                if re.search('PhraseWakeupResult', self.log_lines[i]) is not None and re.search(r"MIXWVPCallback",
                                                                                           self.log_lines[i]) is not None:
                    log_list.append(self.log_lines[i])

                if re.search('SVA Wakeup', self.log_lines[i]) is not None:
                    log_list.append(self.log_lines[i])

                if re.search('onStartCommand action:', self.log_lines[i]) is not None:
                    log_list.append(self.log_lines[i])

                if not is_get_package_info and re.search('Package \[com.miui.voicetrigger\]', self.log_lines[i]) is not None:
                    self.build_date = self.log_lines[i+10].split('=')[1]
                    self.voice_trigger_version = self.log_lines[i+12].split('=')[1:]
                    is_get_package_info = True

                if not is_get_devie_code and re.search('Build fingerprint', self.log_lines[i]) is not None:
                    self.device_code = self.log_lines[i].split(':')[1:]
                    is_get_devie_code = True

                if not is_processed_info and re.search('WakeupAudioUtils', self.log_lines[i]) is not None:
                    self.voice_print_engine_version = self.log_lines[i+5].split('=')[1:]
                    self.voice_print_engine_version += self.log_lines[i+6].split('=')[1:]
                    self.voice_print_engine_version += self.log_lines[i+7].split('=')[1:]
                    self.voice_print_engine_version += self.log_lines[i+8].split('=')[1:]
                    is_processed_info = True

                if re.search('onRecognition:', self.log_lines[i]) is not None:
                    i -= 1
                    break
            self.event_list.append(log_list)


    # 二级事件唤醒失败原因
    def analysis_second_ladder_fail(self):
        # 具体原因分析
        if len(self.second_ladder_fail) != 0:
            self.result_text.insert(tkinter.END, self.second_ladder_fail[0])
        else:
            self.result_text.insert(tkinter.END, '未知原因导致二级唤醒失败\n')

    # 录入唤醒词失败
    def analysis_record_fail(self):
        pass   


    # MTK方案
    def process_mtk(self):
        # MTK方案一次事件会触发两次唤醒
        self.result_text.insert(tkinter.END, 'Note：MTK、MTK自研方案上报一次可能会无间隔触发两次唤醒！\n\n\n')
        i = 1
        for item in self.event_list:
            self.result_text.insert(tkinter.END, '【一级事件】- ' + str(i) + ' - ')
            if re.search('onRecognition:', item[0]) is not None:
                item.insert(0, '小爱同学')
            for line in item:
                self.result_text.insert(tkinter.END, line + '\n\n')
                if re.search('SVA Wakeup success', line) is not None:
                    self.result_text.insert(tkinter.END, '唤醒成功！\n')
                # 耳机事件唤醒失败，需要分析二级唤醒失败的具体原因
                elif re.search('SVA Wakeup exception', line) is not None:
                    self.result_text.insert(tkinter.END, '二级唤醒失败！\n')
                    self.analysis_second_ladder_fail()

            self.result_text.insert(tkinter.END, '\n\n\n')
            i += 1

    def process_e(self):
        # 方案E
        i = 1
        for item in self.event_list:
            self.result_text.insert(tkinter.END, '【一级事件】- ' + str(i) + ' - ')
            for line in item:
                self.result_text.insert(tkinter.END, line + '\n\n')
                if re.search('data=0', line) is not None:
                    self.result_text.insert(tkinter.END, '一级事件异常！(data = 0）\n\n')
                if re.search('PhraseWakeupResult', line) is not None:
                    # 添加上二级事件未唤醒的原因分析
                    if re.search('isVoconWakeupPassed=false', line) is not None and re.search('isVBPassed=false', line) is not None:
                        self.result_text.insert(tkinter.END, '二级失败：未通过唤醒引擎及声纹引擎！\n\n')
                        self.analysis_second_ladder_fail()  # 输出
                        continue
                    elif re.search('isVoconWakeupPassed=false', line) is not None and re.search('isVBPassed=true', line) is not None:
                        self.result_text.insert(tkinter.END, '二级失败：未通过唤醒引擎！\n\n')
                        self.analysis_second_ladder_fail()
                        continue
                    elif re.search('isVoconWakeupPassed=true', line) is not None and re.search('isVBPassed=false', line) is not None:
                        self.result_text.insert(tkinter.END, '二级失败：未通过声纹引擎！\n\n')
                        self.analysis_second_ladder_fail()
                        continue
                    else:
                        self.result_text.insert(tkinter.END, '二级成功！\n\n')
                        ed = self.line_timestamp(line)
                if re.search('onStartCommand action:', line) is not None:
                    self.result_text.insert(tkinter.END, '唤醒成功！\n')
                    st = self.line_timestamp(item[1])
                    ed = self.line_timestamp(item[len(item) - 2])
                    self.result_text.insert(tkinter.END, '一级-->二级耗时：' + str(ed - st) + 'ms\n')
            self.result_text.insert(tkinter.END, '\n\n')
            i += 1

    # 高通方案
    def process_qualcomm(self):
        i = 1
        for item in self.event_list:
            self.result_text.insert(tkinter.END, '【一级事件】- ' + str(i) + ' - ')
            if len(item) == 2:
                for line in item:
                    self.result_text.insert(tkinter.END, line + '\n\n')
                self.result_text.insert(tkinter.END, '唤醒失败！\n\n\n\n')
                continue
            for line in item:
                self.result_text.insert(tkinter.END, line + '\n\n')
                if re.search('SVA Wakeup success', line) is not None:
                    self.result_text.insert(tkinter.END, '唤醒成功！\n')
                elif re.search('SVA Wakeup exception', line) is not None:
                    self.result_text.insert(tkinter.END, '唤醒失败！\n')
            self.result_text.insert(tkinter.END, '\n\n')
            i += 1

    def line_timestamp(self, line):
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        year = re.findall(r'\d{4}', nowTime)[0]
        timestr = year + '-' + re.search(r'\d{2}-\d{2}[ ]\d{2}:\d{2}:\d{2}.\d{3}', line).group()
        datetime_obj = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
        return int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)



