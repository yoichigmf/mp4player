# PyQt5 Video player
#!/usr/bin/env python

from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSlot
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer,  QVideoFrame, QVideoProbe
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,QMessageBox,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys



class FrameCounterWidget(QLabel):

    def __init__(self, parent=None):
        super(FrameCounterWidget, self).__init__(parent)

        self.setFixedWidth(20)
        self.frame_cnt = 0
        self.setText('0')
        self.parent = parent

    def reset_framecount( self ):
        self.frame_cnt = 0
        self.setText('0')

    @pyqtSlot(QVideoFrame)
    def processFrame(self, frame):
        self.frame_cnt = self.frame_cnt + 1
        self.setText(str(self.frame_cnt))

        if self.parent is not None:
            self.parent.FramEncr()

        


class VideoWindow(QMainWindow):

    def  FramEncr( self ):
        self.framecount  = self.framecount 

    def FrameReset( self ):
        self.framecount  = 0
        self.frameCounter.reset_framecount()


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', u'動画ウィンドウを閉じますか?',
               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            self.mediaPlayer.pause()
            print('Window closed')
        else:
           
            event.ignore()	


    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle(u"位置ログ対応動画再生") 

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)


        self.volumeslider  =  QSlider(Qt.Horizontal)
        self.volumeslider.setRange(0,100)
        #self.volumeslider.setFixedwidth(100)
        self.volumeslider.setValue(50)
        self.volumeslider.setEnabled(False)
        self.volumeslider.sliderMoved.connect(self.setvolume)




        self.soundButton = QPushButton()
        self.soundButton.setEnabled(False)
        self.soundButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume)) 
        self.playButton.clicked.connect(self.sound) 

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)


        self.clickButton = QPushButton()
        self.clickButton.setText(u'再生動画位置クリック')
        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        #fileMenu = menuBar.addMenu('&File')
        #fileMenu.addAction(newAction)
        #fileMenu.addAction(openAction)
        #fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        self.frameCounter = FrameCounterWidget(self)

        self.FrameReset()
        
        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)


        soundLayout = QHBoxLayout()
        soundLayout.setContentsMargins(0, 0, 0, 0)
        soundLayout.addWidget(self.soundButton)
        soundLayout.addWidget( self.volumeslider)

        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        buttonLayout.addWidget(self.clickButton)
        #buttonLayout.addWidget( self.frameCounter  )
        #buttonLayout.


        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addLayout(soundLayout)
        layout.addWidget(self.errorLabel)

        layout.addLayout(buttonLayout)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        self.probe = QVideoProbe()

        self.probe.videoFrameProbed.connect( self.frameCounter.processFrame)

        self.probe.setSource(self.mediaPlayer)








    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        self.setFile( fileName )

        self.play()


    #    if fileName != '':
    #        self.mediaPlayer.setMedia(
    #                QMediaContent(QUrl.fromLocalFile(fileName)))
    #        self.playButton.setEnabled(True)
            #self.soundButton.setEnabled(True)
    #        self.volumeslider.setEnabled(True)

    def setFile(self, fileName ):
        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            #self.soundButton.setEnabled(True)
            self.volumeslider.setEnabled(True)
            self.FrameReset( )


    def setModel( self, model ):
        self.model = model
        self.clickButton.clicked.connect( self.model.mapToolEdit )


    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def sound(self):
        if self.mediaPlayer.isMuted():
            print("mute")
            self.mediaPlayer.setMuted( True )
            #self.mediaPlayer.pause()
        else:
            print("not mute")
            self.mediaPlayer.setMuted( False )
            #self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def setvolume(self, volume):
        self.mediaPlayer.setVolume( volume )

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())