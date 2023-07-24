from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen
import os
import json
import pygame
import random as rd
import gtts
import time
from difflib import SequenceMatcher
import speech_recognition as sr
from kivy.core.window import Window
from kivy.config import Config
Config.set('graphics', 'resizable', False)
SIZE = (1000, 600)
Window.size = SIZE

rec = sr.Recognizer()

def listen():
    while True:
        audio = ""
        with sr.Microphone() as source:
            audio = rec.listen(source, phrase_time_limit=3)
        try:
            response = rec.recognize_google(audio, language='en-US')
            return response
        except:
            pass

class QBApp(App):
    def build(self):
        self.man = ScreenManager()
        for thing in ["Cats", "Diffs", "QB"]:
            self.man.add_widget(Screen(name=thing))
        self.power = False
        outtest = BoxLayout(orientation='horizontal', spacing=0)
        layout = BoxLayout(orientation='vertical', spacing=0)
        outtest.add_widget(layout)

        self.ls = []

        options = [
            "European Literature",
            "American Literature",
            "World Literature",
            "British Literature",
            "Classical Literature",
            "Other Literature",
            #"",
            "World History",
            "American History",
            "Ancient History",
            "European History",
            "Other History",
            "",
            "Biology",
            "Chemistry",
            "Math",
            "Physics",
            "Other Science",
            #"",
            "Visual Fine Arts",
            "Auditory Fine Arts",
            "Other Fine Arts",
            "",
            "Current Events",
            "Geography",
            "Mythology",
            "Philosophy",
            "Religion",
            "Social Science",
            "Trash",
            "Other Academic",
        ]

        for option in options:
            if option:
                inner = BoxLayout(orientation="horizontal", spacing=0)
                checkbox = CheckBox(
                    active=False, size_hint_y=None, height=40, color=(1, 1, 1, 1))
                checkbox.bind(active=self.check)
                checkbox.text = option
                inner.add_widget(Label(text=option))
                inner.add_widget(checkbox)
                layout.add_widget(inner)
            else:
                layout = BoxLayout(orientation="vertical", spacing=0)
                outtest.add_widget(layout)
        inner = BoxLayout(orientation="horizontal", spacing=0)
        checkbox = CheckBox(active=False, size_hint_y=None,
                            height=40, color=(1, 1, 1, 1))
        checkbox.bind(active=self.check)
        checkbox.text = "Restrict to Power"
        inner.add_widget(Label(text="Restrict to Power"))
        inner.add_widget(checkbox)
        layout.add_widget(inner)
        self.b = Button(text="Continue", font_size="20sp", background_color=(
            1, 1, 1, 1), color=(1, 1, 1, 1), size=(32, 32), size_hint_y=None, height=50)
        self.b.bind(on_release=lambda x: self.buildDiffs())
        layout.add_widget(self.b)
        self.man.current_screen.add_widget(outtest)
        return self.man
    
    def check(self, cq, on):
        if cq.text == "Restrict to Power":
            self.power = on
            return
        if on:
            self.ls.append(cq.text)
        else:
            self.ls.remove(cq.text)
    
    def buildDiffs(self):
        self.man.current = "Diffs"
        self.man.current_screen.clear_widgets()
        self.lvls = []
        layout = BoxLayout(orientation='vertical', spacing=5)
        options = [str(x) for x in range(11)]
        for option in options:
            inner = BoxLayout(orientation="horizontal", spacing=0)
            checkbox = CheckBox(
                active=False, size_hint_y=None, height=40, color=(1, 1, 1, 1))
            checkbox.bind(active=lambda cq, on: self.lvls.append(
                int(cq.text)) if on else self.lvls.remove(int(cq.text)))
            checkbox.text = option
            inner.add_widget(Label(text=option))
            inner.add_widget(checkbox)
            layout.add_widget(inner)

        self.b = Button(text="Continue", font_size="20sp", background_color=(
            1, 1, 1, 1), color=(1, 1, 1, 1), size=(32, 32), size_hint_y=None, height=50)
        self.b.bind(on_release=lambda x: self.buildQB())
        layout.add_widget(self.b)
        self.man.current_screen.add_widget(layout)

    def buildQB(self):
        self.man.current = "QB"
        self.man.current_screen.clear_widgets()
        self.outterLayout = BoxLayout(orientation = 'vertical', padding = 10, spacing = 10)
        self.layout = BoxLayout(orientation='horizontal', padding=10, spacing = 10)
        button_layout1 = AnchorLayout(anchor_x='center', anchor_y='top')
        self.b1 = Button(text="Start",
                      font_size="20sp",
                      background_color=(1, 1, 1, 1),
                      color=(1, 1, 1, 1),
                      size=(32, 32),
                      size_hint_y=None,
                      height = 50)
        self.b1.bind(on_press=self.setup)
        button_layout1.add_widget(self.b1)
        self.layout.add_widget(button_layout1)
        self.outterLayout.add_widget(self.layout)
        self.man.current_screen.add_widget(self.outterLayout)
        if not self.lvls:
            self.lvls = list(range(11))
        with open("tossups.json", "r", encoding="utf-8") as f:
            questions = [json.loads(line.strip()) for line in f.readlines()]

        if self.ls:
            self.questions = []
            for q in questions:
                try:
                    if q["subcategory"] in self.ls and int(q['difficulty']['$numberInt']) in self.lvls:
                        self.questions.append(q)
                except:
                    continue
        else:
            if self.lvls != list(range(11)):
                for q in questions:
                    try:
                        if int(q['difficulty']['$numberInt']) in self.lvls:
                            self.questions.append(q)
                    except:
                        continue
            else:
                self.questions = questions

        temps = []
        if self.power:
            for q in self.questions:
                if "(*)" in q['question']:
                    temps.append(q)
            self.questions = temps

        self.rec = rec

        self.points = 0

        self.sigVal = 0.5
        self.started = False
        self.paused = False
        self.ans = ""
        self.mp3 = "question.mp3"

        self.doing_something = True
    
    def setup(self, event = None):
        self.b1.unbind(on_press=self.setup)
        if self.started:
            return
        self.started = True
        event.text = "Buzz"
        bl2 = AnchorLayout(anchor_x='center', anchor_y='top')
        self.b2 = Button(text="Skip",
                         font_size="20sp",
                         background_color=(1, 1, 1, 1),
                         color=(1, 1, 1, 1),
                         size=(32, 32),
                         size_hint_y=None,
                         height=50)
        self.b2.bind(on_press=lambda x = None: Clock.schedule_once(self.skip, 0.1))

        self.b3 = Button(text="Pause",
                         font_size="20sp",
                         background_color=(1, 1, 1, 1),
                         color=(1, 1, 1, 1),
                         size=(32, 32),
                         size_hint_y=None,
                         height=50)
        bl3 = AnchorLayout(anchor_x='center', anchor_y='top')
        bl3.add_widget(self.b3)
        self.b3.bind(on_press=self.pause)
        bl2.add_widget(self.b2)
        self.layout.add_widget(bl2)
        self.layout.add_widget(bl3)
        Clock.schedule_once(self.start, 0.1)
        lay = AnchorLayout(anchor_x = 'center', anchor_y='top')
        self.stats = [0,0,0,0]
        self.pointLabel = Label(text="")
        lay.add_widget(self.pointLabel)
        self.label = Label(text="")
        self.outterLayout.add_widget(lay)
        self.updateStats()
        lay = AnchorLayout(anchor_x='center', anchor_y='top')
        lay.add_widget(self.label)
        self.outterLayout.add_widget(lay)
        l = AnchorLayout(anchor_x='center', anchor_y='bottom')
        self.settingsButton = Button(text="Back", font_size="20sp", background_color=(1,1,1,1), color=(1,1,1,1), size=(32,32), size_hint_y=None, height=50)
        self.settingsButton.bind(on_release = self.categories)
        l.add_widget(self.settingsButton)
        self.outterLayout.add_widget(l)

    def categories(self, event=None):
        self.man.current = "Cats"
    
    def start(self, event = None):
        self.correctAdd = 10
        self.b2.unbind()
        self.doing_something = True
        self.b2.bind(on_press=lambda x=None: Clock.schedule_once(self.skip, 0.1))
        self.b1.bind(on_press=lambda x = None: Clock.schedule_once(self.answer, 0.01))
        self.b2.unbind(on_press=lambda x = None: Clock.schedule_once(self.start, 0.1))
        self.b2.text = "Skip"

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        self.read(rd.choice(self.questions))

    def read(self, question):
        self.label.text = ""
        self.paused = False
        self.ans = question['answer']
        self.q = question
        if "(*)" not in question['question']:
            gtts.gTTS(question['question']).save(self.mp3)
            pygame.mixer.music.load(self.mp3)
            pygame.mixer.music.play()
        else:
            if "(+)" in question['question']:
                self.correctAdd = 25
                p = question['question'].split("(+)")
                self.parts = [p[0]] + p[1].split("(*)")
            else:
                self.correctAdd = 20
                self.parts = question['question'].split("(*)")
            Clock.schedule_once(self.powerRead, 0.01)
        Clock.schedule_once(self.reset, 0.1)

    def powerRead(self, event = None):
        if not pygame.mixer.music.get_busy() and not self.doing_something and not self.paused:
            if self.parts:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                gtts.gTTS(self.parts.pop(0)).save(self.mp3)
                pygame.mixer.music.load(self.mp3)
                pygame.mixer.music.play()
                self.correctAdd -= 5
                Clock.schedule_once(self.powerRead, 1)
        else:        
            Clock.schedule_once(self.powerRead, 0.05)
    
    def reset(self, event = None):
        self.doing_something = False

    def skip(self, event=None):
        if self.doing_something:
            return
        self.doing_something=True
        self.label.text = self.q['answer']
        Clock.schedule_once(self.secondSkip, 0.1)
        
    def secondSkip(self, event = None):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        gtts.gTTS("ANSWER: " + self.q['answer']).save(self.mp3)
        pygame.mixer.music.load(self.mp3)
        pygame.mixer.music.play()
        time.sleep(2)
        while pygame.mixer.music.get_busy():
            pass
        Clock.schedule_once(self.start, 0.1)

    def answer(self, event = None):
        self.b1.unbind(on_press = lambda x = None: Clock.schedule_once(self.answer, 0.01))
        if self.doing_something:
            return
        self.doing_something = True
        if self.ans == "":
            return
        pygame.mixer.music.pause()
        if self.correct(resp:=listen()):
            self.points += self.correctAdd
            self.stats[int((20-self.correctAdd)/5)] += 1
            self.updateStats()
            self.next(resp)
        else:
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy():
                self.reset()
                self.skip()
            else:
                self.b1.bind(on_press = lambda x = None: Clock.schedule_once(self.answer, 0.01))
                Clock.schedule_once(self.reset, 0.1)
                self.stats[-1] += 1
                self.points -= 5
                self.updateStats()
    
    def updateStats(self):
        self.pointLabel.text = f" {self.stats[0]}/{self.stats[1]}/{self.stats[2]}/{self.stats[3]} ({self.points} pts)"
    
    def next(self, resp):
        self.label.text = self.q['answer']
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        gtts.gTTS("Correct!").save(self.mp3)
        pygame.mixer.music.load(self.mp3)
        pygame.mixer.music.play()
        self.b2.text = "Continue"
        self.b2.bind(on_press=lambda x = None: Clock.schedule_once(self.start, 0.1))

    def correct(self, resp):
        a = resp.lower()
        try:
            b = self.q['formatted_answer'].lower()
            ls = [self.q['answer'].split("[")[0].split("&")[0].lower()]
            for t in b.split("<b>"):
                ls.append(t.split("</b>")[0].replace("<u>", "").replace("</u>", "").lower())
            return any([SequenceMatcher(None, a, x).ratio()>self.sigVal for x in ls])
        except KeyError:
            b = self.ans.split("[")[0].split("&")[0].lower()
        return SequenceMatcher(None, a, b).ratio()>self.sigVal
    
    def pause(self, e=None):
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused=not self.paused

if __name__ == "__main__":
    pygame.mixer.init()
    os.chdir("\\".join(os.path.abspath(__file__).split("\\")[:-1]))
    QBApp().run()
