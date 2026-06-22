import sys
import os
import pygame

from PyQt6.QtWidgets import (QApplication,QWidget,QVBoxLayout,QPushButton,QListWidget,QLabel,QFileDialog,QSlider,)
from PyQt6.QtCore import Qt,QSettings


class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()
        
        self.settings=QSettings("BITBOX","folder_mem")

        self.current_folder=self.settings.value("last_folder","")

        self.paused=False

        self.setWindowTitle("BITBOX")
        self.resize(500,500)

        layout=QVBoxLayout()

        self.label=QLabel("No folder selected")
        layout.addWidget(self.label)

        self.folder_button=QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        self.song_list=QListWidget()
        self.song_list.itemDoubleClicked.connect(self.play_song)
        layout.addWidget(self.song_list)

        self.prev_button=QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_song)
        layout.addWidget(self.prev_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_resume)
        layout.addWidget(self.pause_button)

        self.stop_button=QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_song)
        layout.addWidget(self.stop_button)

        self.next_button=QPushButton("Next")
        self.next_button.clicked.connect(self.next_song)
        layout.addWidget(self.next_button)

        volume_label=QLabel("Volume")
        layout.addWidget(volume_label)

        self.volume_slider=QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0,100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)
        layout.addWidget(self.volume_slider)

        pygame.mixer.music.set_volume(0.5)

        self.setLayout(layout)
        
        if self.current_folder:
            self.load_folder(self.current_folder)
        


    def select_folder(self):
        folder=QFileDialog.getExistingDirectory(self,"Select Music Folder")

        if not folder:
            return

        self.current_folder=folder
        self.settings.setValue("last_folder",folder)

        self.load_folder(folder)
        
        
    def load_folder(self,folder):
        self.song_list.clear()

        mp3_files=[file for file in os.listdir(folder)if file.lower().endswith(".mp3")]

        mp3_files.sort()

        for file in mp3_files:
            self.song_list.addItem(file)

        self.label.setText(folder)
        

    def play_song(self):
        item=self.song_list.currentItem()

        if item is None:
            return

        song_path=os.path.join(self.current_folder,item.text())

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()

        self.paused=False
        self.pause_button.setText("Pause")

        self.label.setText(f"Playing: {item.text()}")

    def pause_resume(self):
        if not pygame.mixer.music.get_busy() and not self.paused:
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.pause_button.setText("Pause")
            self.paused = False
        else:
            pygame.mixer.music.pause()
            self.pause_button.setText("Resume")
            self.paused = True

    def stop_song(self):
        pygame.mixer.music.stop()

        self.paused=False
        self.pause_button.setText("Pause")
        self.label.setText("Stopped")

    def change_volume(self, value):
        pygame.mixer.music.set_volume(value/100)

    def next_song(self):
        current_row=self.song_list.currentRow()

        if current_row<self.song_list.count()-1:
            self.song_list.setCurrentRow(current_row + 1)
            self.play_song()

    def previous_song(self):
        current_row=self.song_list.currentRow()

        if current_row>0:
            self.song_list.setCurrentRow(current_row-1)
            self.play_song()


app=QApplication(sys.argv)

window=MusicPlayer()
window.show()

sys.exit(app.exec())