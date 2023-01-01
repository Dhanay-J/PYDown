import flet
import datetime
import os

from flet import Page, colors, ProgressBar, Dropdown, ListTile, TextField, FilledButton, Text, Column, Container
from pytube import YouTube
from moviepy.editor import AudioFileClip


class GUI(flet.UserControl):
    def __init__(self):
        super(GUI, self).__init__()

    def build(self):
        self.UFiled = TextField(label="URL", hint_text="Video URL", on_change=self.updater)
        # btn = FilledButton(text="CLICK", on_click=self.updater)

        return Container(
            content=Column(controls=[
                self.UFiled  # ,
                # btn

            ])
        )

    def getVidInfo(self, url):
        Vid = YouTube(url)
        return {'title': Vid.title, 'duration': datetime.timedelta(seconds=Vid.length), 'url': Vid.watch_url}

    def calcPerc(self, stream, chunk, bytes_remaining):
        size = stream.filesize
        progress = (float(abs(bytes_remaining - size) / size))
        self.progBar.value = progress
        self.page.update()

    def removeRow(self, e):
        self.page.remove(e.control)

    def downComplet(self, e, a):
        self.page.remove(self.progBar)
        if self.streamTyp != 'audio':
            self.clear_controls()
            r = ListTile(title=Text("Finished Download : " + self.Vidtitle), on_long_press=self.removeRow)
            self.page.add(r)

    def MP4ToMP3(self, mp4, mp3):
        FILETOCONVERT = AudioFileClip(mp4)
        audProg = ProgressBar(width=400, height=10, bgcolor=colors.CYAN)
        msg = ListTile(title=Text("Converting : " + self.Vidtitle + "|| To Mp3"), on_long_press=self.removeRow)
        self.page.add(audProg, msg)
        self.page.update()
        FILETOCONVERT.write_audiofile(mp3, logger=None)
        FILETOCONVERT.close()
        os.remove(mp4)
        self.page.remove(audProg, msg)
        self.clear_controls()
        r = ListTile(title=Text("Finished Download : " + self.Vidtitle), on_long_press=self.removeRow)
        self.page.add(r)
        self.page.update()

    def downloadFunc(self, e):
        self.streamTyp = ''
        self.page.remove(e.control)
        stream = self.drp_list[e.control.text.split(' ')[-1]]

        r = ListTile(title=Text("Started Download : " + stream.title), on_long_press=self.removeRow)
        self.page.add(r)

        self.progBar = ProgressBar(width=400, height=10, bgcolor=colors.AMBER)
        self.page.add(self.progBar)
        self.Vidtitle = stream.title
        currntDate = str(datetime.datetime.now()).replace(':', '_').replace('.', '_')
        files = [''.join(i.split('.')[:-1]) for i in os.listdir()]

        dupli = False
        vid = None
        forbidenChars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '#']
        VidFile = ''.join(i for i in self.Vidtitle if i not in forbidenChars)
        for file in files:
            if file == VidFile:
                vid = stream.download(currntDate)
                dupli = True

        self.streamTyp = stream.type
        if not dupli:
            vid = stream.download()
        if self.streamTyp == 'audio':
            aud = ''.join(vid.split('.')[:-1]) + '.mp3'
            self.MP4ToMP3(vid, aud)

    def doDownload(self, e):

        downlaod = FilledButton(text=f"Download {e.control.value}", on_click=self.downloadFunc)
        self.page.remove(e.control)
        self.page.add(downlaod)

    def clear_controls(self):
        for i in self.page.controls[1:]:
            self.page.remove(i)

    def updater(self, e):

        url = self.UFiled.value

        e.control.disabled = True
        e.control.update()
        self.clear_controls()

        if 25 < len(url) < 100:
            try:
                vidObj = YouTube(url, on_progress_callback=self.calcPerc, on_complete_callback=self.downComplet)
                t = vidObj.title
                dur = datetime.timedelta(seconds=vidObj.length)

                vid_list = [i for i in vidObj.streams.filter(progressive=True)]

                mp3 = vidObj.streams.get_audio_only()
                _360p = vidObj.streams.get_by_resolution("360p")
                _480p = vidObj.streams.get_by_resolution("480p")
                _720p = vidObj.streams.get_by_resolution("720p")
                _1080p = vidObj.streams.get_by_resolution("1080p")

                self.drp_list = {"mp3": mp3}
                if _360p in vid_list:
                    self.drp_list['360p'] = _360p
                if _480p in vid_list:
                    self.drp_list['480p'] = _480p
                if _720p in vid_list:
                    self.drp_list["720p"] = _720p
                if _1080p in vid_list:
                    self.drp_list["1080p"] = _1080p

                dropdnw = Dropdown(options=[flet.dropdown.Option(i) for i in self.drp_list], on_change=self.doDownload)
                r = ListTile(title=Text(vidObj.title), trailing=Text(str(dur)), on_long_press=self.removeRow)

                self.page.add(r, dropdnw)

            except Exception as E:
                self.clear_controls()
                r = ListTile(title=Text("Error :" + str(E)), on_long_press=self.removeRow)
                self.page.add(r)
            self.page.update()

        e.control.disabled = False
        e.control.update()


def main(page: Page):
    ap = GUI()
    w = 800
    h = 1000

    page.window_width = w
    page.window_height = h

    page.window_max_width = w * 1.2
    page.window_max_height = h * 1.2

    page.window_min_width = w * 0.8
    page.window_min_height = h * 0.8

    page.title = "PYDown"

    page.add(ap)
    page.update()



flet.app(target=main)
