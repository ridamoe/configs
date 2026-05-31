import jidouteki
from jidouteki import *
from urllib.parse import urlparse, ParseResult

class VyManga(WebsiteParser):
    @property
    def meta(self):
        return Metadata(
            key = "vymanga",
            display_name = "VyManga",
            domains=[
                Domain("https://vymanga.com/")
            ]
        )

    @jidouteki.test(
        "https://vymanga.com/manga/becoming-a-family-with-the-duke-and-his-dear-son",
        {"series": "becoming-a-family-with-the-duke-and-his-dear-son"}
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
        
        return result
            
    def fetch_chapter(self, ch_url):
        proxied = self.proxy(ch_url, headers={"referer": "https://vymanga.com/"})
        return self.fetch(proxied)
    
    def fetch_series(self, series):
        return self.fetch(f"/manga/{series}")
    
    @jidouteki.test({"series": "becoming-a-family-with-the-duke-and-his-dear-son"})     
    @jidouteki.map.series.chapters
    def chapters(self, series) -> list[Chapter]:
        d = self.fetch_series(series)
        lang = "en"

        ret = []
        for el in d.css(".div-chapter .list .list-group a"):
            ch_id = el["id"].lstrip("chapter-")
            data = el["href"]
            chapter = Chapter(
                params = { "ch_url": data, "chapter": ch_id },
                chapter =  ch_id,
                language = lang
            )
            ret.append(chapter)
        return list(reversed(ret))
    
    @jidouteki.test({"series": "becoming-a-family-with-the-duke-and-his-dear-son"})      
    @jidouteki.map.series.cover
    def cover(self, series):
        d = self.fetch_series(series).css(".img-manga img")
        for el in d:
            return el["src"]

    @jidouteki.test({ "series": "becoming-a-family-with-the-duke-and-his-dear-son"}, "Becoming A Family With The Duke and His Dear Son")  
    @jidouteki.map.series.title
    def title(self, series):
        d = self.fetch_series(series)
        d = d.css("h1.title")
        for el in d: 
            return el.get_text()
        return None
    
    @jidouteki.test({"series": "becoming-a-family-with-the-duke-and-his-dear-son", "chapter": "35"}) 
    @jidouteki.map.images
    def images(self, series, chapter):
        chs = self.chapters(series)
        chs = [c for c in chs if c.chapter == chapter]
        
        c = chs[0]
        d = self.fetch_chapter(c.params["ch_url"])
        
        
        ret = []
        for el in d.css(".carousel-item[data-page] img"):
            url = el["data-src"]
            ret.append(url)
        return ret