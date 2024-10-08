from jidouteki import Metadata, Config, Chapter
import jidouteki

@jidouteki.register
class Retsu(Config):
    @jidouteki.meta
    def _meta(self):
        return Metadata(
            key = "retsuorg",
            display_name = "Retsu.org",
            base = "https://retsu.org"    
        )

    @jidouteki.match
    def _match(self):
        return (
            r"https://retsu\.org/manga/(?P<series>.*?)/(?:ch|chapter)-(?P<chapter>.*?)(?:[/?].*|)$",
            r"https://retsu\.org/manga/(?P<series>.*?)(?:[/?].*|)$"
        ) 

    def _fetch_series(self, series):
        return self.fetch(f"/manga/{series}")
    
    @jidouteki.series.cover
    def _series_cover(self, series): 
        d = self._fetch_series(series)
        d = d.css(".summary_image img")
        for el in d:
            return el["data-src"]
    
    @jidouteki.series.title
    def _series_title(self, series): 
        d = self._fetch_series(series)
        d = d.css("h1.post-title").pop()        
        return d.get_text()

    @jidouteki.series.chapters
    def _chapters(self, series):
        d = self._fetch_series(series)
        d = d.css(".wp-manga-chapter > a")
        chapters = []
        for el in d:
            chap_val = self.match(el["href"])["chapter"]
            chapter = Chapter(
            params = { "chapter": chap_val }, 
            chapter = chap_val,
            language = "en",
            )
            chapters.append(chapter)
        return chapters

    @jidouteki.images
    def _images(self, series, chapter):
        for d in self.fetch(f"/manga/{series}/", [f"ch-{chapter:0>3}",  f"chapter-{chapter}"]):
            d = d.css(".reading-content img")

            images = []
            for el in d:
                image = el["data-src"].replace("\t", '').replace("\n", '')
                images.append(image)
            if images: return images
        return None

# search:
#   fetcher:
#     params:
#           - query
#     type: request
#     urls: 
#       - /?s={query}&post_type=wp-manga

#   series:
#     selector:
#       type: css
#       query: .manga__item > .manga__content a
#       pipeline:
#         - props: 
#           - href
#         - regex: https://retsu\.org/manga/(.*?)/