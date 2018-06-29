import os
import random
import requests
import tkinter as tk
import tweepy as tw
from io import BytesIO
from PIL import Image, ImageTk
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET

# こ↑こ↓ url 変数 クソコード要素
url = ''
FILENAME = 'images/_____meshitero.jpg'


class MainFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class ImageLabel(tk.Label):
    SIZE = 250

    def __init__(self, master, image, id, **kwargs):
        super().__init__(master, **kwargs)
        self.id = id
        self._image = image['image']
        self.url = image['url']
        re_image = image['image'].resize(self.get_size(image['image'].size), Image.NEAREST)
        tkpi = ImageTk.PhotoImage(re_image)
        self.configure(image=tkpi)
        self.image = tkpi

        self.bind('<1>', self.click_callback)

    def click_callback(self, event):
        self._image.save(FILENAME)
        global url
        url = self.url

    def get_size(self, tup):
        s = self.SIZE

        x, y = tup
        if x <= s and y <= s:
            return x, y

        elif x > y:
            r = float(s) / float(x)
            return s, int(y*r)
        else:
            r = float(s) / float(y)
            return int(x*r), s


class ImageFrame(tk.Frame):
    COL = 3
    ROW = 3

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.ils = []

    def update(self, images):
        for il in self.ils:
            il.destroy()

        for i, image in enumerate(images):
            il = ImageLabel(self, image, i)
            il.grid(row=int(i/self.COL), column=i % self.COL)
            self.ils.append(il)


class GetButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, text='飯テロ画像収集', **kwargs)
        self.master = master


class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master, *, placeholder='', color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind('<FocusIn>', self.foc_in)
        self.bind('<FocusOut>', self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class HashtagEntry(EntryWithPlaceholder):
    def __init__(self, master, **kwargs):
        super().__init__(master, placeholder='#ハッシュタグ', **kwargs)
        self.master = master


class SendButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, text='飯テロ', **kwargs)
        self.master = master


def get_tweets(api, _max):
    tweets = []
    search_result = api.search(q='飯テロ', count=100)
    for result in search_result:
        if 'media' not in result.entities:
            continue

        if len(tweets) >= _max:
            break

        for media in result.entities['media']:
            tweets.append({'url': media['expanded_url'].split(':')[1], 'image': Image.open(BytesIO(requests.get(media['media_url']).content))})

            if len(tweets) >= _max:
                break

    return tweets


def quit_callback(root):
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
    root.destroy()


def main():
    auth = tw.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tw.API(auth)

    root = tk.Tk()
    root.title('VirtualCast 飯テロ')
    root.protocol('WM_DELETE_WINDOW', lambda: quit_callback(root))

    mfr = MainFrame(root, bg='midnight blue')
    gbt = GetButton(mfr)

    # 迫真のハードコーティング
    images = [
        {'url': 'https://commons.nicovideo.jp/material/nc143034', 'image': Image.open('images/nc143034.jpg')},
        {'url': 'https://commons.nicovideo.jp/material/nc144986', 'image': Image.open('images/nc144986.jpg')},
        {'url': 'https://commons.nicovideo.jp/material/nc142493', 'image': Image.open('images/nc142493.jpg')}
    ]

    ifr = ImageFrame(mfr, bg='navy')
    ifr.update(images)
    hen = HashtagEntry(mfr)
    sbt = SendButton(mfr)

    mfr.pack()
    gbt.pack(pady=5)
    ifr.pack(padx=5, pady=5)
    hen.pack(pady=5)
    sbt.pack(pady=5)

    gbt['command'] = lambda: ifr.update(get_tweets(api, ifr.ROW * ifr.COL))
    global url
    sbt['command'] = lambda: api.update_with_media(filename=FILENAME, status='{}\n{} MT\n出典:{}\n'.format(hen.get(), random.randint(0, 500), url))

    root.mainloop()


if __name__ == '__main__':
    main()
