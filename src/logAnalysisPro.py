import os
import zipfile
import wave
import pyaudio
from tkinter import *
import tkinter.messagebox as messagebox
from tkinter import scrolledtext
from tkinter.ttk import Combobox
import re

import windnd

from LogFilePro import LogFilePro

# 请提示LogAn
class LogAnalysisPro:
    def __init__(self, init_window_name):
        self.log_files = []
        self.pcm_files = []
        # self.log_files_map = {}
        self.init_window_name = init_window_name
        self.dumpVoiceTriggerPath = "AAAVoicetriggerDump"

     # 设置窗口
    def set_init_window(self):
        self.init_window_name.title('LogAnalysisPro')
        self.init_window_name.geometry('1420x795+350+150')
        self.init_window_name['bg'] = 'AliceBlue'
        self.init_window_name.attributes('-alpha', 1)

        # 标签
        self.file_path_label = Label(self.init_window_name, text='文件/压缩包 拖拽处↓', bg='AliceBlue', font=('楷体', 14), width=20, height=1, relief=FLAT)
        self.file_path_label.place(x=0, y=0)
        self.file_path_text = Text(self.init_window_name, width=32, height=5, bg='White', font=('楷体', 12))
        self.file_path_text.place(x=0, y=23)
        
        # 添加日期输入框和按钮
        self.date_entry_label = Label(self.init_window_name, text='输入时间 (07-26 22:01:00):', bg='AliceBlue', font=('楷体', 13), width=28, height=1, relief=FLAT)
        self.date_entry_label.place(x=0, y=120)
        self.date_entry = Entry(self.init_window_name, width=28, font=('楷体', 13))
        self.date_entry.place(x=0, y=145)

        # self.date_button = Button(self.init_window_name, text='确认日期', bg='AliceBlue', font=('楷体', 13), width=12, height=1, command=self.process_date)
        # self.date_button.place(x=0, y=170)

        self.scheme_label = Label(self.init_window_name, text='唤醒方案', bg='AliceBlue', font=('楷体', 13), width=8, height=1, relief=FLAT)
        self.scheme_label.place(x=0, y=210)
        self.scheme_text = Text(self.init_window_name, width=28, height=1, bg='White', font=('楷体', 13))
        self.scheme_text.place(x=0, y=235)

        self.voice_trigger_version_label = Label(self.init_window_name, text='voicetrigger版本', bg='AliceBlue', font=('楷体', 13), width=16, height=1, relief=FLAT)
        self.voice_trigger_version_label.place(x=0, y=260)
        self.voice_trigger_version_text = Text(self.init_window_name, width=28, height=1, bg='White', font=('楷体', 13))
        self.voice_trigger_version_text.place(x=0, y=285)      
        
        self.build_date_label = Label(self.init_window_name, text='build date', bg='AliceBlue', font=('楷体', 13), width=10, height=1, relief=FLAT)
        self.build_date_label.place(x=0, y=310)
        self.build_date_text = Text(self.init_window_name, width=28, height=1, bg='White', font=('楷体', 13))
        self.build_date_text.place(x=0, y=335)

        self.device_code_label = Label(self.init_window_name, text='设备编号', bg='AliceBlue', font=('楷体', 13), width=8, height=1, relief=FLAT)
        self.device_code_label.place(x=0, y=360)
        self.device_code_text = Text(self.init_window_name, width=28, height=8, bg='White', font=('楷体', 13))
        self.device_code_text.place(x=0, y=390)

        self.phone_name_label = Label(self.init_window_name, text='手机名称', bg='AliceBlue', font=('楷体', 13), width=8, height=1, relief=FLAT)
        self.phone_name_label.place(x=0, y=490)
        self.phone_name_text = Text(self.init_window_name, width=28, height=1, bg='White', font=('楷体', 13))
        self.phone_name_text.place(x=0, y=520)

        self.voice_print_engine_version_label = Label(self.init_window_name, text='算法模型', bg='AliceBlue', font=('楷体', 13), width=8, height=1, relief=FLAT)
        self.voice_print_engine_version_label.place(x=0, y=550)
        self.voice_print_engine_version_text = Text(self.init_window_name, width=28, height=9, bg='White', font=('楷体', 13))
        self.voice_print_engine_version_text.place(x=0, y=580)

        # 文本框
        self.pcm_files_list_label = Label(self.init_window_name, text='音频列表', bg='AliceBlue', font=('楷体', 14), width=8, height=1, relief=FLAT)
        self.pcm_files_list_label.place(x=265, y=0)
        self.pcm_files_list = Combobox(self.init_window_name, width=150)
        self.pcm_files_list.bind("<<ComboboxSelected>>", self.pcm_file_callback)
        self.pcm_files_list.place(x=265, y=23)

        self.log_files_list_label = Label(self.init_window_name, text='日志列表', bg='AliceBlue', font=('楷体', 14), width=8, height=1, relief=FLAT)
        self.log_files_list_label.place(x=265, y=46)
        self.log_files_list = Combobox(self.init_window_name, width=150)
        self.log_files_list.bind("<<ComboboxSelected>>", self.log_file_callback)
        self.log_files_list.place(x=265, y=69)

        self.result_data_label = Label(self.init_window_name, text='日志分析结果', bg='AliceBlue', font=('楷体', 14), width=12, height=1, relief=FLAT)
        self.result_data_label.place(x=265, y=92)
        self.result_data_text = scrolledtext.ScrolledText(self.init_window_name, width=126, height=38, font=('楷体', 13))
        self.result_data_text.place(x=265, y=115)

        windnd.hook_dropfiles(self.init_window_name, func=self.dragged_files)

    # def process_date(self):
    #     date_str = self.date_entry.get()
    #     if re.match(r'\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str):
    #         messagebox.showinfo(title='日期输入', message=f'您输入的日期时间是: {date_str}')
    #         # 这里可以添加处理输入日期时间的逻辑
    #         print(f'输入日期时间: {date_str}')
    #     else:
    #         messagebox.showwarning(title='格式错误', message='请输入正确的日期时间格式 (07-26 22:01:00)')



    def dragged_files(self, files):
        self.clear_text()
        file_path = '\n'.join((item.decode('gbk') for item in files))
        self.log_files_list.set('')
        self.file_path_text.delete(0.0, END)
        self.file_path_text.insert(0.0, file_path)
        self.log_files = []
        self.pcm_files = []
        self.unzip_folder(file_path)
   
    def unzip_folder(self, file_path):
        # 压缩包先解压后再分析，文件直接分析
        print("file path:"+file_path)
        if zipfile.is_zipfile(file_path):
            self.unzipBugReport(file_path)
        else:
            self.clear_text()
            self.log_files_list["value"] = []
            self.analysis_log_file(file_path)


    def log_file_callback(self, event):
        # file_path = self.log_files_map[self.log_files[self.log_files_list.current()]]
        self.analysis_log_file(self.log_files[self.log_files_list.current()])

    def pcm_file_callback(self, event):
        pcm_file = self.pcm_files[self.pcm_files_list.current()]
        self.analysis_pcm_file(pcm_file)

    def analysis_pcm_file(self, pcm_file):
        player = pyaudio.PyAudio()
        stream = player.open(format=player.get_format_from_width(2), channels=1, rate=16000, output=True)
        with open(pcm_file, "rb") as file:
            stream.write(file.read())
        stream.stop_stream()
        stream.close()
        player.terminate()

    def analysis_log_file(self, file_path):
        self.clear_text()
        date_str = self.date_entry.get()

        log_file = LogFilePro(file_path, self.result_data_text, date_str)
        log_file.start_process()
        self.scheme_text.insert(END, log_file.voice_trigger_scheme)
        self.voice_trigger_version_text.insert(END, log_file.voice_trigger_version)
        self.build_date_text.insert(END, log_file.build_date)
        self.device_code_text.insert(END, log_file.device_code)
        # self.device_name_text.insert(END, log_file.device_name)
        self.phone_name_text.insert(END, log_file.phone_name)
        self.voice_print_engine_version_text.insert(END, log_file.voice_print_engine_version)
        # self.wakeup_engine_version_version_text.insert(END, log_file.wakeup_engine_version)

    def clear_text(self):
        self.result_data_text.delete('0.0', END)
        self.scheme_text.delete('0.0', END)
        self.voice_trigger_version_text.delete('0.0', END)
        self.build_date_text.delete('0.0', END)
        self.device_code_text.delete('0.0', END)
        # self.device_name_text.delete('0.0', END)
        self.phone_name_text.delete('0.0', END)
        # self.android_version_text.delete('0.0', END)
        # self.sdk_version_text.delete('0.0', END)
        self.voice_print_engine_version_text.delete('0.0', END)
        # self.wakeup_engine_version_version_text.delete('0.0', END)

    def unzipBugReport(self, bugReportFileName):
        fz = zipfile.ZipFile(bugReportFileName, 'r')
        dump_path = os.path.join(bugReportFileName[:-4], self.dumpVoiceTriggerPath)
        dest_path = bugReportFileName[:-4]
        for file in fz.namelist():
            fz.extract(file, bugReportFileName[:-4])
            # 把unzip_file_path字符串转成_path变量
            if os.path.basename(file) == "voice_trigger.zip":
                self.unzipInerVoiceTriggerAudio(file, dest_path, dump_path)
            elif os.path.basename(file) == "encrypt_voice_trigger.zip":
                self.unzipInerVoiceTriggerAudio(file, dest_path, dump_path)
                print("unzip encrypt_voice_trigger.zip")
            elif os.path.basename(file) == "voice_trigger_log.zip":
                self.unzipInerVoiceTriggerLog(file, dest_path, dump_path)
            elif os.path.basename(file).endswith('.zip') and os.path.basename(file).startswith('bugreport-'):
                self.unzip284BugLog(file, dest_path, dump_path)

        if len(self.log_files) == 0:
            messagebox.showinfo(title=None, message="无有效日志！")
        else:
            self.log_files_list["value"] = self.log_files
            self.pcm_files_list["value"] = self.pcm_files


    def unzip284BugLog(self, file, dest_path, dump_path):
        srcfile = zipfile.ZipFile(os.path.join(dest_path, file))
        for file_name in srcfile.namelist():
            srcfile.extract(file_name, dump_path)
            if os.path.basename(file_name).startswith('bugreport-') and os.path.basename(file_name).endswith('.txt'):
                self.log_files.append(dump_path + "/" + file_name)
                print()
                print("unzip284BugLog filelist:" + file_name)
                print()


    def unzipInerVoiceTriggerLog(self, file, dest_path, dump_path):
        srcfile = zipfile.ZipFile(os.path.join(dest_path, file))
        for file_name in srcfile.namelist():
            srcfile.extract(file_name, dump_path)
            self.log_files.append(dump_path + "/" + file_name)
            # print("unzipInerVoiceTriggerLog filelist:" + file_name)

    # 定义一个unzipInerVoiceTriggerAudio函数
    def unzipInerVoiceTriggerAudio(self, file, dest_path, dump_path):
        try:
            srcfile = zipfile.ZipFile(os.path.join(dest_path, file))
            for file_name in srcfile.namelist():
                srcfile.extract(file_name, dump_path,"18d0e1382aeab5274eada82f6cc747a9".encode("utf-8"))
                if file_name.endswith('.zip'):
                    self.recursive_unzip(os.path.basename(file_name), dump_path + "/" + os.path.dirname(file_name))
                else:
                    file_abspath = dump_path + file_name
                    print("unzipInerVoiceTriggerAudio filelist:" + file_abspath)
                    if file_name.endswith('.txt'):
                        self.log_files.append(file_abspath)
                    else:
                        self.pcm_files.append(file_abspath)
                        self.convertPcmToWave(file_abspath)
        except Exception as e:
            # messagebox.showinfo(title="错误信息", message="解压失败或压缩文件损坏")
            print("unzipInerVoiceTriggerAudio error:" + str(e))
    
    def recursive_unzip(self, file, dump_path):
        # file_path用于解压缩文件；des_dir用于存放下一级的解压缩的同名目录
        if dump_path.endswith('/'):
            dump_path = dump_path[:-1]
        print("@@@recursive_unzip path:" + dump_path + " --- file name " + file)
        srcfile = zipfile.ZipFile(dump_path + "/" + file)
        for file_name in srcfile.namelist():
            srcfile.extract(file_name, dump_path)
            if file_name.endswith('.zip'):
                  self.recursive_unzip(os.path.basename(file_name), dump_path + "/" + os.path.dirname(file_name))
            else:
                file_abspath = dump_path + "/" + file_name
                print("recursive_unzip file_abspath:" + file_abspath)
                if file_name.endswith('.txt'):
                    self.log_files.append(file_abspath)
                else:
                    self.pcm_files.append(file_abspath)
                    self.convertPcmToWave(file_abspath)
    
    def convertPcmToWave(self, pcmfile):
        # print("@@@@@@@@@@convert target:" + pcmfile[:-4] + '.wav')
        pcmData = open(pcmfile, 'rb').read()
        with wave.open(pcmfile[:-4] + '.wav', 'wb') as wavfile:
            wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
            wavfile.writeframes(pcmData)

def analysis_start():
    init_window = Tk()
    analysis_window = LogAnalysisPro(init_window)
    analysis_window.set_init_window()
    init_window.mainloop()


analysis_start()
