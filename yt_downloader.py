import sys
import os
from urllib.parse import urlparse, parse_qs

from PyQt6.QtWidgets import QApplication,QWidget,QVBoxLayout,QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl,QThread,pyqtSignal,QSettings

import yt_dlp


class SilentWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self,level,message,lineNumber,sourceID):
        pass


class DownloadWorker(QThread):
    progress=pyqtSignal(str)
    finished_ok=pyqtSignal(str)
    failed=pyqtSignal(str)

    def __init__(self,url:str,output_dir:str):
        super().__init__()
        self.url=url
        self.output_dir=output_dir
 


    def run(self):
        def hook(d):
            if d.get("status")=="downloading":
                pct=d.get("_percent_str", "").strip()
                self.progress.emit(f"Downloading... {pct}")
            elif d.get("status") == "finished":
                self.progress.emit("Converting to mp3...")

        ydl_opts={
            "format":"bestaudio/best", "outtmpl":os.path.join(self.output_dir,"%(title)s.%(ext)s"),"postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec": "mp3","preferredquality": "192",}],
            "cookiesfrombrowser":("firefox",),"remote_components":{"ejs:github"},"progress_hooks":[hook],"quiet":True,"no_warnings":True,
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info=ydl.extract_info(self.url,download=True)
                title=info.get("title","audio")
            self.finished_ok.emit(title)
        except Exception as e:
            self.failed.emit(str(e))


class BrowserWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BITBOX")
        self.resize(1200,850)

        self.worker=None
        self.settings=QSettings("BITBOX","folder_mem")

        layout=QVBoxLayout()

        self.browser=QWebEngineView()
        self.browser.setPage(SilentWebPage(self.browser))
        self.browser.setUrl(QUrl("https://www.youtube.com"))
        layout.addWidget(self.browser)

        self.download_btn=QPushButton("Download MP3")
        self.download_btn.clicked.connect(self.on_download_clicked)
        layout.addWidget(self.download_btn)

        self.setLayout(layout)

    def clean_yt_url(self,url:str)->str:
        url=url.strip()
        parsed=urlparse(url)

        if "youtu.be" in parsed.netloc:
            video_id=parsed.path.strip("/")
            return f"https://www.youtube.com/watch?v={video_id}" if video_id else url

        if "youtube.com" in parsed.netloc:
            qs=parse_qs(parsed.query)
            video_id=qs.get("v")
            if video_id:
                return f"https://www.youtube.com/watch?v={video_id[0]}"

        return url

    def on_download_clicked(self):
        raw_url=self.browser.url().toString()
        clean_url=self.clean_yt_url(raw_url)
        
        selected_folder=self.settings.value("last_folder", "")
        output_dir = selected_folder if selected_folder else os.path.expanduser("~/Downloads")

        self.download_btn.setEnabled(False)
        self.download_btn.setText("Downloading...")

        self.worker=DownloadWorker(clean_url,output_dir)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_ok.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def on_progress(self,message:str):
        print(message)

    def on_finished(self,title:str):
        self.download_btn.setEnabled(True)
        self.download_btn.setText("Download MP3")
        print(f"Done: {title}.mp3")

    def on_failed(self,error_message:str):
        self.download_btn.setEnabled(True)
        self.download_btn.setText("Download MP3")
        print(f"Failed: {error_message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())