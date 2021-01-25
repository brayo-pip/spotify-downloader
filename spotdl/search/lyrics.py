from requests import get
from bs4 import BeautifulSoup
from spotdl.search.sessionClient import get_session

base_url = "https://genius.com"
base_search_url = base_url + "/api/search/multi?per_page=1&q="
ses = get_session()

class Genius:
    @classmethod
    def from_query(self, artist, song, lyric_fail=False) -> str:
        """
        Returns the lyrics as a string \n
        set lyric fail to false if you prefer no lyrics
        to bad lyrics
        """
        if '(' in song:
            song = song[:song.find("(")]
        
        query = f"{artist} {song}"
        # print("Artist name: {} \n Song:{}".format(artist, song))
        encoded_query = query.replace(" ", "+")
        search_url = base_search_url + encoded_query
        response_json = ses.get(search_url).json()
        # print(response_json['response']['sections'][0]['hits'][0]['result'])
        try:
            lyric_url = (
                base_url
                + response_json["response"]["sections"][0]["hits"][0]["result"]["path"]
            )
        except:
            print(f"\nNo lyric hits for {artist} {song}")
            return ""

        if not lyric_url.endswith("lyrics"):
            print(f"\nPossible lyric failure, for {artist} {song}")
            if not lyric_fail:
                return ""

        return self.from_url(lyric_url)

    @classmethod
    def from_url(self, url):
        """
        Returns the lyrics as a string
        """
        # time.sleep(0.5)
        if url == "":
            """return nil if url is nil"""
            return ""
        soup = BeautifulSoup(get(url).content, features="lxml")
        retries = 10
        lyrics = soup.html.p.text
        while retries > 0 and len(lyrics)<100:
            # time.sleep(0.5)
            soup = BeautifulSoup(ses.get(url).content, features="lxml")
            lyrics = soup.html.p.text
        if retries == 0 and lyrics == "Produced by" or lyrics == "Featuring":
            # the scripts gives up and plays hangman
            # print("hangman")
            return ""
        return soup.html.p.text
