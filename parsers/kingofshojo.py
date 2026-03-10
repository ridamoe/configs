import jidouteki
from jidouteki import *
from urllib.parse import urlparse, ParseResult

class KingOfShojo(WebsiteParser):
    @property
    def meta(self):
        return Metadata(
            key = "kingofshojo",
            display_name = "King of Shojo",
            domains=[
                Domain("https://kingofshojo.com/")
            ]
        )

    @jidouteki.test(
        "https://kingofshojo.com/the-grand-duke-is-mine-chapter-63/",
        {"series": "the-grand-duke-is-mine", "chapter": "63"}
    )
    @jidouteki.test(
        "https://kingofshojo.com/manga/the-grand-duke-is-mine/",
        {"series": "the-grand-duke-is-mine"}
    )     
    @jidouteki.map.match
    def match(self, url):
        parsed_url: ParseResult = urlparse(url)
        
        domain = parsed_url.scheme + "://" + parsed_url.hostname + "/"

        if not any([d.url == domain for d in self.meta.domains]):
            return None
        
        result = None
        path = parsed_url.path.strip("/").split("/")
        if len(path) == 2 and path[0] == "manga":
            result = {}
            result["series"] = path[1]
        elif len(path) == 1:
            slug = path[0].split("-")
            if slug[-2] == "chapter":
                result = {}
                result["series"] = "-".join(slug[:-2])
                result["chapter"] = slug[-1]
        
        return result
            
    def fetch_chapter(self, series, chapter):
        return self.fetch(f"/{series}-chapter-{chapter}")
    
    def fetch_series(self, series):
        return self.fetch(f"/manga/{series}") # use v3
    
    @jidouteki.test({ "series": "the-grand-duke-is-mine"})     
    @jidouteki.map.series.chapters
    def chapters(self, series):
        d = self.fetch_series(series)
        lang = "en"

        ret = []
        for el in d.css("#chapterlist li"):
            chapter = Chapter(
                params = { "chapter": el["data-num"]},
                chapter =  el["data-num"],
                language = lang
            )
            ret.append(chapter)
        return list(reversed(ret))
    
    @jidouteki.test({"series": "the-grand-duke-is-mine"})     
    @jidouteki.map.series.cover
    def cover(self, series):
        d = self.fetch_series(series).css(".thumb img")
        for el in d:
            return el["src"]

    @jidouteki.test({"series": "the-grand-duke-is-mine"}, "The Grand Duke is Mine")
    @jidouteki.map.series.title
    def title(self, series):
        d = self.fetch_series(series)
        d = d.css("h1.entry-title")
        for el in d: 
            return el.get_text()
        return None
    
    @jidouteki.test({"series": "the-grand-duke-is-mine", "chapter": "63"}) 
    @jidouteki.map.images
    def images(self, series, chapter):
        d = self.fetch_chapter(series, chapter).css("#readerarea img")
        
        ret = []
        for el in d:
            url = el["src"]
            # ret.append(self.proxy(url, headers={"referer": self.domain.url}))
            ret.append(url)
        return ret