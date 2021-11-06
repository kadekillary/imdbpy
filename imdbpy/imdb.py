from typing import Dict, Generator

from bs4.element import Tag

from .scraper import Scraper


class IMDb:
    def __init__(self):
        self.BASE_URL: str = "https://www.imdb.com"
        self.PAGE_URL: str = f"{self.BASE_URL}/search/title/?title_type="

    def get_page_urls(
        self, title_type: str, sort_method: str = None, number_of_pages: int = 200
    ) -> Generator[str, None, None]:
        """
        Dynamically generate all page URLs for IMDb section

        IMDb ranks movies based on various sorting strategies:
            - none (default) -> popularity
            - num_votes
            - boxoffice_gross_us
            - runtime
            - year
            - release_date
            - alpha (alphabeticaly)

        In order to quickly grab data from each of these pages we dynamically
        generate the URL. These URLs will cover the top 10,000 films. After
        10,000 results the next page token becomes a hash. Therefore, there is
        no way to dynamically generate the URL without having to visit the prior page.

        Since the first page contains results 1-50 the second page begins on
        the 51st ranked title. From there each addiitonal page increments by
        50 results (i.e. 51 -> 101).
        """
        results = (number_of_pages * 50) + 1

        endpoint = f"{self.PAGE_URL}{title_type}"

        if not sort_method:
            pages = (f"{endpoint}&start={i}" for i in range(1, results, 50))
        else:
            pages = (
                f"{endpoint}&sort={sort_method},asc&start={i}"
                for i in range(1, results, 50)
            )
        return pages

    def get_movie_urls(self, url: str) -> Generator[str, None, None]:
        """
        Extract all movie URLs from an IMDb ranking page

        Each URl grabbed is originally of the form `/title/tt046859/`.
        Therefore, we need to append the Base URL in order to get a proper URL.
        """
        scraper = Scraper(url)
        imdb_ids = scraper.extract_all_movie_urls()
        movie_links = (
            f"{self.BASE_URL}{imdb_id.find('a')['href']}" for imdb_id in imdb_ids
        )
        return movie_links

    def get_movie_data(self, url: str) -> Dict[str, str]:
        """Extract indiviaual data points from an IMDb movie page"""
        scraper = Scraper(url)
        stars = scraper.extract_stars()
        return {
            "title": scraper.extract_title(),
            "year": scraper.extract_tag_text("span", {"id": "titleYear"}),
            "runtime": scraper.extract_runtime(),
            "imdb_rating": scraper.extract_tag_text(
                "span", {"itemprop": "ratingValue"}
            ),
            "imdb_votes": scraper.extract_tag_text("span", {"itemprop": "ratingCount"}),
            "imdb_id": scraper.extract_imdb_id(url),
            "metascore_rating": scraper.extract_tag_text(
                "div", {"class": "metacriticScore"}
            ),
            "director": scraper.extract_multiple_tags(
                "h4", "Directors:", singular_text="Director:"
            ),
            "star_1": scraper.grab_star(stars, 0),
            "star_2": scraper.grab_star(stars, 1),
            "star_3": scraper.grab_star(stars, 2),
            "genre": scraper.extract_multiple_tags("h4", "Genres:"),
            "summary": scraper.extract_tag_text("div", {"class": "summary_text"}),
            "awards": scraper.extract_awards(),
            "tagline": scraper.extract_next_sibling_text("h4", "Taglines:"),
            "release_date": scraper.extract_next_sibling_text("h4", "Release Date:"),
            "also_known_as": scraper.extract_next_sibling_text("h4", "Also Known As:"),
            "filming_locations": scraper.extract_multiple_tags(
                "h4", "Filming Locations:"
            ),
            "production_company": scraper.extract_multiple_tags("h4", "Production Co:"),
            "mpaa_rating": scraper.extract_mpaa_rating(),
            "mpaa_reasoning": scraper.extract_mpaa_reasoning(),
            "keywords": scraper.extract_multiple_tags("h4", "Plot Keywords:"),
            "writers": scraper.extract_multiple_tags(
                "h4", "Writers:", singular_text="Writer:"
            ),
            "sound_mix": scraper.extract_multiple_tags("h4", "Sound Mix:"),
            "budget": scraper.extract_next_sibling_text("h4", "Budget:"),
            "opening_weekend": scraper.extract_next_sibling_text(
                "h4", "Opening Weekend USA:"
            ),
            "gross": scraper.extract_next_sibling_text("h4", "Gross USA:"),
            "worldwide_gross": scraper.extract_next_sibling_text(
                "h4", "Cumulative Worldwide Gross:"
            ),
        }

    def get_movie_by_id(self, imdb_id: str) -> Dict[str, str]:
        """Extract movie data points for a given IMDb ID"""
        movie_url = f"{self.BASE_URL}/title/{imdb_id}/"
        movie_data = self.get_movie_data(movie_url)
        return movie_data
