import os
import re
from os import system

from requests import Session

# основной плеер для запуска видео
PLAYER = "mpv"
# команда для установки заголовка headers
OS_HEADERS_COMMAND = "--http-header-fields"

# regex для поиска паттернов
ANIME_FIND_PATTERN = re.compile(r'<a href="(https://animego\.org/anime/.*)" title="(.*?)">')  # url + title
COUNT_SERIES_PATTERN = re.compile(r'"col-6 col-sm-8 mb-1">(\d+)')  # count series
WATCH_ID_PATTERN = re.compile(r'data-watched-id="(\d+)"')  # episodes ids
DUB_NAME_PATTERN = re.compile(
    r'data-dubbing="(\d+)"><span class="video-player-toggle-item-name text-underline-hover">\s+(.*)')  # dubs
PLAYER_PATTERN = re.compile(r'data-player="(.*)"\s+data-provider="\d+"\s+data-provide-dubbing="(\d+)"')  # video players

EP_PATTERN = re.compile(r'data-id="(\d+)"')  # episodes id
EP_NAME_PATTERN = re.compile(r'data-episode-title="(.*)"')  # episode name

ANIBOOM_PATTERN = re.compile(r"hls:\{src:(.*\.m3u8)")  # aniboom video pattern


class Anime:
    USER_AGENT = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/94.0.4606.104 Safari/537.36", "x-requested-with": "XMLHttpRequest"}
    USER_AGENT_AJAX = USER_AGENT.copy()
    SEARCH_URL = "https://animego.org/search/anime"

    def __init__(self):
        self.session = Session()
        self.session.headers.update(self.USER_AGENT)
        self.anime_results = []
        self.series_count = 0
        self._episodes = []
        self.anime_url = ""
        self.__anime_id = ""
        self._videos = []

    def search(self, pattern: str) -> list:
        r = self.session.get("https://animego.org/search/anime", params={"q": pattern})
        anime_urls = re.findall(ANIME_FIND_PATTERN, r.text)
        self.anime_results = anime_urls
        return self.anime_results

    @staticmethod
    def is_unsupported_player(player: str):
        return not ("kodik" in player or "anivod" in player)

    def parse_episodes_count(self, index_choose: int):
        self.anime_url = self.anime_results[index_choose][0]
        self.__anime_id = self.anime_url.split("-")[-1]
        r = self.session.get(self.anime_url)
        self.series_count = re.findall(COUNT_SERIES_PATTERN, r.text)
        if len(self.series_count) > 0:
            return int(self.series_count[0])
        else:
            self.series_count = 1
            return self.series_count

    def parse_players(self, episode_num: int, series_id: str):
        r = self.session.get("https://animego.org/anime/series", params={"dubbing": 2, "provider": 24,
                                                                         "episode": episode_num,
                                                                         "id": series_id}).json()["content"]
        dubs = re.findall(DUB_NAME_PATTERN, r)
        players = re.findall(PLAYER_PATTERN, r)
        results = []
        for dub in dubs:
            result = {
                "dub": dub[1],
                "player":
                    [p[0].replace("amp;", "") for p in players if p[1] == dub[0] and self.is_unsupported_player(p[0])]
            }
            if len(result["player"]) > 0:
                results.append(result)
        self._videos = results

    def parse_series(self):
        r = self.session.get(f"https://animego.org/anime/{self.__anime_id}/player?_allow=true").json()["content"]
        #  доступные эпизоды
        ep_ids = re.findall(EP_PATTERN, r)
        ep_titles = re.findall(EP_NAME_PATTERN, r)
        self._episodes = list(zip(ep_ids, ep_titles))
        return self._episodes

    def choose_episode(self, index_ep: int):
        ep_id = self._episodes[index_ep][0]
        self.parse_players(index_ep, ep_id)
        return self._videos

    def play(self, player: str):
        if "sibnet" in player:
            os.system(f"{PLAYER} {'https:' + player}")
        elif "aniboom" in player:
            # заголовки обязательно должны быть с заглавной буквы для удачного запроса
            r = self.session.get("https:" + player,
                                 headers={"Referer": "https://animego.org/",
                                          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                                        "(KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"})
            r = r.text.replace("&quot;", "").replace("\\", "")
            player = re.findall(ANIBOOM_PATTERN, r)[0]
            os.system(f'{PLAYER} {OS_HEADERS_COMMAND}="Referer: https://aniboom.one" {player}')
        elif "kodik" in player:
            # not support
            pass


class Menu:

    def __init__(self):
        self.__ACTIONS = {"q": ("quit", self.exit),
                          "r": ("back next step", self.back_on),
                          "h": ("help", self.help),
                          "f": ("find anime action", self.find),
                          "c": ("clear", self.cls)
                          }
        self.anime = Anime()
        self.__back_action = True

    def back_on(self):
        self.__back_action = False

    def back_off(self):
        self.__back_action = True

    @staticmethod
    def cls():
        system("clear")

    @property
    def is_back(self):
        return self.__back_action

    def choose_dub(self, result):
        print(*[f"{i}] {r['dub']}" for i, r in enumerate(result, 1)], sep="\n")
        while self.is_back:
            print("Choose dub:", 1, "-", len(result))
            command = input("c_d > ")
            if not self.command_wrapper(command) and command.isdigit():
                command = int(command)
                print("Start playing")
                player = result[command - 1]["player"][0]
                self.anime.play(player)
            return
        self.back_off()

    def choose_episode(self, num: int):
        self.anime.parse_episodes_count(num - 1)
        episodes = self.anime.parse_series()
        if len(episodes) > 0:
            print(*[f"{i}] {s[1]}" for i, s in enumerate(episodes, 1)], sep="\n")
            while self.is_back:
                print(f"Choose episode: 1-{len(episodes)}")
                command = input("c_e > ")
                if not self.command_wrapper(command) and command.isdigit():
                    result = self.anime.choose_episode(int(command) - 1)
                    if len(result) > 0:
                        self.choose_dub(result)
                    else:
                        print("Not available dubs")
                        return
            self.back_off()
        return

    def choose_anime(self):
        while self.is_back:
            print("Choose anime:", 1, "-", len(self.anime.anime_results))
            command = input(" > ")
            if not self.command_wrapper(command) and command.isdigit():
                self.choose_episode(int(command))
        self.back_off()

    def find(self, pattern):
        results = self.anime.search(pattern)
        if len(results) > 0:
            print("Found", len(results))
            print(*[f"{i}] {a[1]}" for i, a in enumerate(results, 1)], sep="\n")
            self.choose_anime()
        else:
            print("Not found!")
            return

    def help(self):
        for k, v in self.__ACTIONS.items():
            print(k, v[0])

    def command_wrapper(self, command):
        if self.__ACTIONS.get(command):
            self.__ACTIONS[command][1]()
            return True
        return False

    def main(self):
        print("Input anime name or USAGE: h for get commands")
        while True:
            command = input("m > ")
            if not self.command_wrapper(command):
                self.find(command)

    @staticmethod
    def exit():
        exit(1)


if __name__ == '__main__':
    Menu().main()
