import kivy
from kivy.app import App
from tkinter import messagebox, END, filedialog, Tk
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from geturlinfo import urllib,GetUrlInfo
from filecfgmanager import CFGfile
import os, sys, re, json
from kivy.config import Config

DEBUG = False

def resource_path(relative_path):
    
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if DEBUG:
    Config.set('kivy','window_icon', resource_path(r'img/logoIco.ico'))
else:
    Config.set('kivy','window_icon', resource_path(r'logoIco.ico'))

Config.set('graphics', 'resizable', '1') 
Config.set('graphics', 'width', '1100')  
Config.set('graphics', 'height', '600') 

class Display(BoxLayout):
    pass
class Episodio(BoxLayout):
    def __init__(self, numeroEpisodio, nomeAnime, nomeEpisodio, **kwargs):
        super().__init__(**kwargs)
        self.ids.numeroEpisodio.text = numeroEpisodio
        self.ids.nomeAnime.text = nomeAnime
        self.ids.nomeEpisodio.text = nomeEpisodio

class MyButton(Button):
    def __init__(self, meta, **kwargs):
        super().__init__(**kwargs)
        self.text = meta

class InputResult(TextInput):
    def __init__(self, meta, **kwargs):
        super().__init__(**kwargs)
        self.text = meta

class Season(Button):
    def __init__(self, seasonName, seasonNumber, **kwargs):
        super().__init__(**kwargs)
        self.text = seasonName
        self.id = seasonNumber

class Login(Screen):
    def login(self):
        self.parent.current = 'Scraping'

class Scraping(Screen):
    
    def __init__(self, episodios, **kwargs):
        super().__init__(**kwargs)
        
        self.url = ''
        self.animeInfo = None
        self.cfgFileObject = None
        self.directoryPath = ''
        self.fileNames = []
        self.seasonList = None
        self.seasonDict = {}
        self.seasonChosen = 0
        self.root = Tk()
        self.root.withdraw()

    def generateCfgCommand(self):
        
        editedJasonList = []
        keyList = ['temporada', 'episodio', 'nome', 'duracao', 'thumb', 'qualidade']

        inputList = re.split('\n', self.episodeInfoTextBox.get('1.0', 'end-2c'))
        
        flag = False
        for info1, info2 in zip(inputList, self.cfgFileObject.episodeInfoList):
            
            editJson = json.loads(re.sub('\'', '"', re.sub('"', '', info1)))
            editedJasonList.append(editJson)

            for key in keyList:
                if editJson[key] != info2[key]:
                    flag = True

        if flag == True:
            if messagebox.askokcancel('ANIEDASH', 'Foram feitas modificações, tem certeza que deseja gerar assim mesmo?'):
                self.cfgFileObject.setCfgFile(self.directoryPath, editedJasonList)
        else:
            if messagebox.askokcancel('ANIEDASH', 'Tem certeza que deseja gerar o arquivo cfg?'):
                self.cfgFileObject.setCfgFile(self.directoryPath, self.cfgFileObject.episodeInfoList)

        messagebox.showwarning('ANIEDASH', 'CFG Criado com sucesso!')
        self.resetAll()
    
    def showInfoCommand(self):     
        
        if self.fileNames:

            self.cfgFileObject = CFGfile(self.directoryPath, self.fileNames)
            self.cfgFileObject.getEpisodesNnumbers()

            season = self.seasonChosen
            names = self.animeInfo.getAnimeNames(season)

            try:
                self.cfgFileObject.getEpisodeInfo(names, season)
            except Exception as fnf:
                messagebox.showerror('ANIEDASH' , fnf)
                return

            episodeInfoList = self.cfgFileObject.getEpisodeInfoList()
            
            if self.cfgFileObject.epsodeNameVerify():

                if episodeInfoList:
                    for info in episodeInfoList:
                        self.ids.resultScraping.add_widget(InputResult(meta=str(info)))

                else:
                     messagebox.showwarning('ANIEDASH', 'Não há episódios para a temporada escolhida')
               
            else:
                messagebox.showerror('ANIEDASH', 'Parece que um ou mais arquivos não estão com o nome correto.')
                self.fileNames = []

        else:
            messagebox.showwarning('ANIEDASH', 'Não é possível mostrar informações dos arquivos.')
            return

    def fileSearchCommand(self):

        if self.ids.selectedFiles.children:

            while self.ids.resultScraping.children:
                self.ids.resultScraping.children.pop()

            while self.ids.selectedFiles.children:
                self.ids.selectedFiles.children.pop()

            self.fileNames = []

        fileNames = filedialog.askopenfilenames(title = 'Selecione os Episódios', filetypes = [('Arquivos .mp4', '*.mp4')])
        
        if fileNames:
            self.directoryPath = '\\'.join(re.split('/', fileNames[0])[:-1]) + os.sep
 
            if fileNames != '':
                for name in fileNames:
                    self.fileNames.append(re.split('/', name)[-1])
                    self.ids.selectedFiles.add_widget(MyButton(re.split('/', name)[-1]))
            else:
                messagebox.showwarning('ANIEDASH', 'Selecione algum episódio.')
        
        if self.animeInfo:
            self.showInfoCommand()
        return
    
    def getAnimeInfo(self):
        self.animeInfo = GetUrlInfo(self.url)

    def search(self):

        if self.ids.temporadas.children:
            while self.ids.temporadas.children:
                self.ids.temporadas.children.pop()

        self.url = self.ids.url.text
        if self.url == '':
            messagebox.showwarning('ANIEDASH', 'Forneça um link meu parsero!')
            return

        try:
            self.getAnimeInfo()
        except ValueError as ve:
            messagebox.showerror('ANIEDASH - Link inválido', ve)
            return
        except urllib.error.URLError:
            messagebox.showerror('ANIEDASH', 'Não foi possível acessar o link. Verifique sua conexão com a internet.')
            return

        self.seasonList = self.animeInfo.getSeasonName()
        
        if self.seasonList:
            for num, season in enumerate(self.seasonList, 0):
                self.ids.temporadas.add_widget(Season(season,str(num)))
                self.seasonDict[season] = num
    
    def getSeason(self, season):

        if self.ids.resultScraping.children:
            while self.ids.resultScraping.children:
                self.ids.resultScraping.children.pop()

        self.seasonChosen = season
        if self.ids.selectedFiles.children:
            self.showInfoCommand()

class Upload(Screen):

    def __init__(self, episodios, **kwargs):
        super().__init__(**kwargs)
        for episodio in episodios:
            self.ids.Episodios.add_widget(Episodio(numeroEpisodio=episodio, nomeAnime=episodio, nomeEpisodio=episodio))

    def addMultEps(self):
        url = 'https://www.crunchyroll.com/pt-br/saga-of-tanya-the-evil'
        season = 1
        anime = GetUrlInfo(url)
        names = anime.getAnimeNames(season)
        for name in names:
           self.ids.Episodios.add_widget(Episodio(numeroEpisodio=name, nomeAnime=name, nomeEpisodio=name))

class ANIEDASH(App):
    def build(self):
        return Display()

ANIEDASH().run()