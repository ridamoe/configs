from jidouteki import *
import jidouteki
from urllib.parse import urlparse, ParseResult

class Rawkuma(WebsiteParser):
  @property
  def meta(self):
    return Metadata(
      key = "rawkuma",
      display_name = "Rawkuma",
      domains=[
        Domain("https://rawkuma.net/"),
      ]
    )

  def __init__(self, context: jidouteki.Jidouteki) -> None:
     super().__init__(context)
     self.session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
     })
  
  @jidouteki.test(
     "https://rawkuma.net/manga/game-sekai-no-mobu-akuyaku-ni-tensei-shita-node-last-bos-wo-mezashite-mita/",
     {"series": "game-sekai-no-mobu-akuyaku-ni-tensei-shita-node-last-bos-wo-mezashite-mita"}
  )
  @jidouteki.test(
     "https://rawkuma.net/manga/game-sekai-no-mobu-akuyaku-ni-tensei-shita-node-last-bos-wo-mezashite-mita/chapter-1.196705/",
     {"series": "game-sekai-no-mobu-akuyaku-ni-tensei-shita-node-last-bos-wo-mezashite-mita", "chapter": "1.196705"}  
  )
  @jidouteki.map.match
  def match(self, url):
    parsed_url: ParseResult = urlparse(url)
        
    domain = parsed_url.scheme + "://" + parsed_url.hostname + "/"

    if not any([d.url == domain for d in self.meta.domains]):
        return None

    result = None
    path = parsed_url.path.strip("/").split("/")
    if len(path) >= 2 and path[0] == "manga":
        result = {}
        result["series"] = path[1]
        if len(path) > 2: result["chapter"] = path[2].split("-")[-1]
    return result

  def fetch_series(self, series):
    return self.fetch(f"/manga/{series}")
   
  @jidouteki.test({"series": "100-man-no-inochi-no-ue-ni-ore-wa-tatte-iru"})
  @jidouteki.map.series.chapters
  def chapters(self, series):
      d = self.fetch_series(series)
      LANG = { "manga": "ja", "manhwa": "ko", "manhua": "zh" }
      type  = d.css("article section div div:nth-child(1) div:nth-last-child(1) .inline p")[0].get_text()
      lang =  LANG[type.lower()]
      
      ret = []
      for el in d.css("#chapter-list > div"):
        chp_link = el.css.select_one("a")
        matched = self.match(chp_link["href"])
        
        chapter = Chapter(
          params = { "chapter": matched["chapter"]},
          chapter =  el["data-chapter-number"],
          language = lang
        )
        ret.append(chapter)
      return list(reversed(ret))
  
  @jidouteki.test({"series": "100-man-no-inochi-no-ue-ni-ore-wa-tatte-iru"})
  @jidouteki.map.series.cover
  def cover(self, series):
      d = self.fetch_series(series).css("[itemprop=image] img")
      for el in d:
        return el["src"]


  @jidouteki.test({"series": "100-man-no-inochi-no-ue-ni-ore-wa-tatte-iru"})
  @jidouteki.map.series.title
  def title(self, series):
      d = self.fetch_series(series)
      d = d.css("main article section h1[itemprop=name]")
      for el in d: 
        return el.get_text("text").strip()
      return None
  
  @jidouteki.test(
        {"series": "100-man-no-inochi-no-ue-ni-ore-wa-tatte-iru", "chapter": "31.4056"}
  )
  @jidouteki.map.images
  def images(self, series, chapter):
      d = self.fetch(f"/manga/{series}/chapter-{chapter}")
      d = d.css("section[data-image-data] img")
      
      ret = []
      for el in d:
         url = el["src"]
         ret.append(self.proxy(url, headers={"referer": self.domain.url}))
      return ret
      
  # search:
  #   fetcher:
  #     params:
  #       - query
  #     type: request
  #     urls: 
  #       - /?s={query}
  #   series:
  #     selector:
  #       type: css
  #       query: .bs > .bsx a
  #       pipeline:
  #         - props: 
  #           - href
  #         - regex: https://rawkuma\.com/manga/(.*?)/