from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (  # , QLabel, QSizePolicy
    QApplication, QFileDialog, QHBoxLayout, QPushButton, 
    QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar
)

import libs
from qt_tools import show_elements, hide_elements

# https://doc.qt.io/qtforpython-5/PySide2/QtMultimedia/QMediaPlayer.html#qmediaplayer
# https://clay-atlas.com/us/blog/2020/10/14/pyqt5-en-qmediaplayer-directshowplayerservice/
# https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QListWidget.html

class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.is_settings_hidden = False
        self.mediaPlayer = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.playlist = QMediaPlaylist(self.mediaPlayer)
        self.playlist.PlaybackMode(QMediaPlaylist.Loop)
        
        btnSize = QSize(16, 16)
        self.videoWidget = QVideoWidget()

        openButton = QPushButton("Open Video")
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        openButton.setFont(QFont("Noto Sans", 8))
        openButton.clicked.connect(lambda: self.open_Video_File())

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play_switch)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)
        self.statusBar.setSizeGripEnabled(False)

        self.controlLayout = QHBoxLayout()
        self.controlLayout.setContentsMargins(0, 0, 0, 0)
        self.controlLayout.addWidget(openButton)
        self.controlLayout.addWidget(self.playButton)
        self.controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addLayout(self.controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.setPlaylist(self.playlist)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")
        #self.switch_Settings()

    def playlist_Add_Media(self, filePath):
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(filePath)));
        self.playButton.setEnabled(True)

    def open_Video_File(self, filePath=""):
        if filePath == "":
            filePath, _ = QFileDialog.getOpenFileName(
                self, 
                "Select Media File",
                ".", 
                "Video Files (*.mp4 *.flv *.ts *.mts *.avi)"
            )

        if filePath != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(filePath))
            )
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(filePath)
            self.play_switch()

    def play_switch(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)
            )
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())
        # print("Error: " + self.mediaPlayer.errorString())

    def switch_Settings(self):
        self.is_settings_hidden = not self.is_settings_hidden
        if self.is_settings_hidden:
            for index in range(self.controlLayout.count()):
                hide_elements([self.controlLayout.itemAt(index).widget()])
        else:
            for index in range(self.controlLayout.count()):
                show_elements([self.controlLayout.itemAt(index).widget()])

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Player")
    player.resize(600, 400)
    player.show()
    sys.exit(app.exec_())
