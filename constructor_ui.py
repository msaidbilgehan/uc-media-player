
### ### ### ### ### ## ### ### ### ###
### ### ### BUILT-IN LIBRARIES ### ###
### ### ### ### ### ## ### ### ### ###
import logging
from operator import index
from time import sleep
# import cv2

### ### ### ### #### ### ### ###
### ### ### QT LIBRARIES ### ###
### ### ### ### #### ### ### ###
# https://doc.qt.io/archives/qt-4.8/qstyle.html
from PyQt5.QtWidgets import QStyle

### ### ### ### ## ## ## ### ### ###
### ### ### CUSTOM LIBRARIES ### ###
### ### ### ### ## ## ## ### ### ###
import libs

from stdo import stdo
from tools import time_log, TIME_FLAGS, time_list, save_to_json, load_from_json, list_files, path_control, get_OS
from qt_tools import qtimer_Create_And_Run, hide_elements, show_elements, list_Widget_Item
# from image_manipulation import draw_Rectangle
from structure_ui import Structure_UI, init_and_run_UI, init_UI, Graphics_View
from structure_threading import Thread_Object
from structure_data import Structure_Buffer
from media_player import VideoPlayer

### ### ### ### ### ## ## ## ### ### ### ### ###
### ### ### CAMERA UI CONFIGURATIONS ### ### ###
### ### ### ### ### ## ## ## ### ### ### ### ###

class Player_UI(Structure_UI):
    def __init__(self, *args, obj=None, logger_level=logging.INFO, **kwargs):
        super(Player_UI, self).__init__(*args, logger_level=logger_level, **kwargs)

        ### Constractor ###
        self.__thread_Dict = dict()
        self.uart_buffer = Structure_Buffer(max_limit=10, name="uart_buffer")
        self.is_uart_pause = False
        self.serial = None
        
        self.video_file_paths = list()
        
        self.setting_file_path = "settings.json"
        self.settings = dict()
        self.is_settings_open = True
        
        ### ### Init ### ##
        self.init()
        
    ### ### ## ### ###
    ### OVERWRITES ###
    ### ### ## ### ###
    
    def init(self):
        self.configure_Button_Connections()
        self.configure_Other_Settings()

        self.video_player = VideoPlayer(self)
        self.widget_Frame.layout().addWidget(self.video_player)
        self.switch_Settings()

        # Load Last Settings
        self.load_Settings()
        self.UART_Start_Communication(
            port="/dev/ttyS0", 
            bound_Rate=9600
        )

    def init_QTimers(self, *args, **kwargs):
        super(Player_UI, self).init_QTimers(*args, **kwargs)
        
    def UART_Start_Communication(self, port="/dev/ttyS0", bound_Rate=9600):
        self.UART_Initialize(port=port, bound_Rate=bound_Rate)
        # self.UART_Listener(buffer, delay=0.1)
        self.UART_Listener_Thread_Start(
            buffer=self.uart_buffer,
            trigger_quit=self.is_Quit_App, 
            trigger_pause=self.is_UART_Pause
        )

    def UART_Listener_Thread_Start(self, buffer=None, delay=0.1, trigger_quit=None, trigger_pause=None):
        self.__thread_Dict["UART_Listener"] = Thread_Object(
            name="UART_Listener",
            delay=delay,
            # logger_level=None,
            set_Deamon=True,
            run_number=None,
            quit_trigger=trigger_quit
        )
        self.__thread_Dict["UART_Listener"].init(
            params=[
                buffer, 
                delay,
                trigger_pause,
                trigger_quit
            ],
            task=self.UART_Listener
        )
        self.__thread_Dict["UART_Listener"].start()
        
    def is_UART_Pause(self):
        return self.is_uart_pause
    
    def switch_UART_Pause(self, bool=None):
        self.is_uart_pause = not self.is_uart_pause if bool is None else bool
        return self.is_uart_pause
        
    def configure_Button_Connections(self):
        ### Load Files ###
        self.pushButton_Load_Video_Files.setIcon(
            self.style().standardIcon(QStyle.SP_DirIcon)
        )
        self.pushButton_Load_Video_Files.clicked.connect(
            lambda: self.load_Videos(
                self.QFileDialog_Event(
                    "getExistingDirectory",
                    [
                        "Open Folder",
                        "",
                    ]
                )
            )
        )

        ### Save / Load Settings ###
        self.pushButton_Load_Settings.setIcon(
            self.pushButton_Load_Settings.style().standardIcon(QStyle.SP_DialogOpenButton)
        )
        self.pushButton_Load_Settings.clicked.connect(self.load_Settings)
        
        self.pushButton_Save_Settings.setIcon(
            self.pushButton_Save_Settings.style().standardIcon(QStyle.SP_DialogSaveButton)
        )
        self.pushButton_Save_Settings.clicked.connect(self.save_Settings)
        
        ### Refresh Video Folder ###
        self.pushButton_Refresh_Video_Files.clicked.connect(
            lambda: self.load_Videos(self.settings["last_Video_File_Path"])
        )
        self.pushButton_Refresh_Video_Files.setIcon(
            self.pushButton_Refresh_Video_Files.style().standardIcon(QStyle.SP_BrowserReload)
        )

    ####################
    ### VIDEO STREAM ###
    ####################

    def switch_Settings(self):
        self.is_settings_open = not self.is_settings_open
        if self.is_settings_open:
            #hide_elements([self.widget_Frame])
            show_elements([
                self.groupBox_Settings,
            ])
        else:
            hide_elements([
                self.groupBox_Settings,
            ])
            #show_elements([self.widget_Frame])
        self.video_player.switch_Settings()

    ####################
    ####################
    ####################

    def configure_Other_Settings(self):
        self.action_Settings_Page.triggered.connect(self.switch_Settings)
        # self.listWidget_Video_Files.itemDoubleClicked.connect(self.play_Video)
        self.listWidget_Video_Files.itemDoubleClicked.connect(
            self.list_Widget_Double_Click_Action
        )
        self.spinBox_Simulate_Index.valueChanged.connect(
            # lambda: self.UART_Action(self.spinBox_Simulate_Index.value())
            lambda: self.uart_buffer.append(self.spinBox_Simulate_Index.value())
        )
        """
        self.label_UART_Current_Action.textChanged.connect(
            self.label_UART_Last_Action.setText(
                self.label_UART_Current_Action.text()
            )
        )
        """

    def closeEvent(self, *args, **kwargs):
        super(Player_UI, self).closeEvent(*args, **kwargs)
        
    ### ### ## ### ###
    ### ### ## ### ###
    ### ### ## ### ###
    
    def list_Widget_Double_Click_Action(self, item):
        # stdo(1, f"Selected File: {self.video_file_paths[self.listWidget_Video_Files.currentRow()]}")
        self.video_player.playlist.setCurrentIndex(
            self.listWidget_Video_Files.currentRow()
        )
        self.video_player.mediaPlayer.play()
        # self.video_player.play()
    
    def UART_Initialize(self, port="/dev/ttyS0", bound_Rate=9600):
        if get_OS() == "Linux":
            global serial
            import serial
            
            self.serial = serial.Serial(port, bound_Rate)
            self.switch_UART_Pause(bool=True)
            
        elif get_OS() == "Windows":
            self.switch_UART_Pause(bool=False)

    def UART_Listener(self, buffer, delay, trigger_pause, trigger_quit):
        if self.serial is not None:
            while True:
                if trigger_quit():
                    break
                sleep(delay)
                if not trigger_pause():
                    received_data = self.serial.read()
                    sleep(delay)
                    data_left = self.serial.inWaiting()  # check for remaining byte
                    received_data += self.serial.read(data_left)
                    self.serial.write(received_data)  # transmit data serially

                    # stdo(1, f"received_data: {received_data}")
                    if buffer is not None:
                        buffer.append(received_data)
                        self.QObject_Text_Event_Add([
                            self.label_UART_Current_Action,
                            buffer.get_Last()
                        ])
        else:
            if buffer is not None:
                action = buffer.pop()
                self.QObject_Text_Event_Add([
                    self.label_UART_Current_Action,
                    action
                ])
                self.QTFunction_Caller_Event_Add([
                    self.UART_Action,
                    [
                        action
                    ]
                ]) if action is not None else action

    def UART_Action(self, index):
        # stdo(1, f"Selected File: {self.video_file_paths[self.listWidget_Video_Files.currentRow()]}")
        self.video_player.playlist.setCurrentIndex(
            index
        )
        self.video_player.mediaPlayer.play()
        # self.video_player.play()
        
    def load_Videos(self, path):
        # stdo(1, f"load_Videos Parameters: {path}")
        if path != "":
            self.settings["last_Video_File_Path"] = path + \
                "/" if path[-1] != "/" else path
            # stdo(1, f"Video Directory Path: {path}")
            self.video_file_paths = list_files(
                path=self.settings["last_Video_File_Path"],
                extensions=[".mp4", ".avi"],
                recursive=False
            )
            # stdo(1, f"Video File Paths: {self.video_file_paths}")
            self.listWidget_Video_Files.clear()
            self.video_player.playlist.clear()
            for video_file_path in self.video_file_paths:
                self.qt_Priority()
                self.listWidget_Video_Files.addItem(
                    list_Widget_Item(
                        title=video_file_path.split("/")[-1]
                    )
                )
                self.video_player.playlist_Add_Media(video_file_path)
        self.spinBox_Simulate_Index.setMaximum(len(self.video_file_paths) - 1)
        
    def save_Settings(self):
        save_to_json(
            path=self.setting_file_path, 
            data=self.settings, 
            sort_keys=True
        )
        
    def load_Settings(self):
        if path_control(self.setting_file_path, is_file=True, is_directory=False)[0]:
            self.settings = load_from_json(
                path=self.setting_file_path
            )
            # stdo(1, f"{self.settings}")
        if self.settings.get("last_Video_File_Path"):
            self.load_Videos(self.settings["last_Video_File_Path"])
        
    def play_Video(self):
        pass


### ### ### ### ### ## ## ## ### ### ### ### ###
### ### ### ### ### ## ## ## ### ### ### ### ###
### ### ### ### ### ## ## ## ### ### ### ### ###

if __name__ == "__main__":
    # title, Class_UI, run=True, UI_File_Path= "test.ui", qss_File_Path = ""
    stdo(1, "Running {}...".format(__name__))
    app, ui = init_and_run_UI(
        "Player UI Test",
        Player_UI,
        UI_File_Path="player_v2_UI.ui"
    )
