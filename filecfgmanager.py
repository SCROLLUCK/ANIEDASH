import os, re, json
from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT

class CFGfile(object):

    def __init__(self, path, episodeList):
        
        self.isExpection = False
        self.path = path
        self.episodeNumbers = set({})
        self.episodeList = episodeList
        self.episodeInfoList = []
    
    def getEpisodesNnumbers(self):

        for number in self.episodeList:
            x = re.findall('\\d+', number[:-1])
            if x:
                self.episodeNumbers.add(int(''.join(x)))

    def getEpisodeInfo(self, names, season):

        for number, name in enumerate(names, 1):
            
            if number in self.episodeNumbers:

                input_file = self.path + 'episodio-' + str(number) + '.mp4'

                videoInfo = VideoCapture(input_file)
                fps = videoInfo.get(CAP_PROP_FPS)
                frameCount = videoInfo.get(CAP_PROP_FRAME_COUNT)

                duration = self.getCorretDuration(int(round(frameCount / fps, 0)))
                quality = videoInfo.get(4)

                episodeData = {'temporada' : season + 1, 'episodio' : number, 'nome' : name, 'duracao' : duration, 'thumb' : 'thumb-' + str(number) + '.png', 'qualidade' : str(quality)[:-2] + 'p' }
                self.episodeInfoList.append(episodeData)

                videoInfo.release()

    def getCorretDuration(self, duration):
        
        h = int(duration / 3600)
        m = int(duration % 3600 / 60)
        s = int(duration % 3600 % 60)

        if m <= 9: 
            m = '0' + str(m)
        if s <= 9: 
            s = '0' + str(s)

        duration = str(m) + ':' + str(s)

        if h > 0:
            if h <= 9: 
                h = '0' + str(h)
                
            duration = str(h) + ':' + duration
            
        return duration

    def getEpisodeInfoList(self):

        return self.episodeInfoList

    def setCfgFile(self, path, jsonList):
        
        with open(path + 'config.cfg', 'w', encoding = 'utf-8') as cfg:

            for info in jsonList:
                cfg.write(json.dumps(info, ensure_ascii = False))
                cfg.write('\n')
    
    def epsodeNameVerify(self):

        return all([re.search('\\bepisodio-\\d+[.]mp4\\b', j) for j in self.episodeList])