import bs4 as bs
import urllib.request, re

class GetUrlInfo(object):

    def __init__(self, url):

        self.url = url
        self.sauce = urllib.request.urlopen(self.url).read()
        self.soup = bs.BeautifulSoup(self.sauce, 'lxml')
        self.seasons = self.soup.find_all('li', class_  = 'season')[::-1]
        if len(self.seasons) == 1:
            tituloSeason = self.soup.new_tag('a',title='Temporada Única',**{'class':'season-dropdown'})
            self.soup.li.append(tituloSeason)

    def getAnimeNames(self, index):

        seasons = self.seasons[index]

        divs = seasons.find_all('div', class_ = 'wrapper container-shadow hover-classes')

        for div in divs:
            spans = div.find_all('span', class_ = 'block')
            if any([re.search('\\bEpisódio (SP|\\d+\\.\\d)\\b', str(i)) for i in spans]):
                div.a.decompose()
                

        names = []
        _names = seasons.find_all('img')[::-1]

        for name in _names:
            names.append(name.get('alt'))

        return names

    def getSeasonName(self):

        names = []
        seasons = self.soup.find_all('a', class_ = 'season-dropdown')[::-1]

        for name in seasons:
            names.append(name.get('title'))

        return names