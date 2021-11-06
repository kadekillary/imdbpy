import re
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet

from .utils import exception_handler


class Scraper:
    """
    Scraper handles the request and parsing of a URL.
    """

    def __init__(self, url: str):
        self.url: str = url
        self.source: Optional[BeautifulSoup] = self.__get_source()

    @exception_handler
    def __get_source(self) -> Optional[BeautifulSoup]:
        """Get HTML source from a URL"""
        # TODO: try using `lxml` parser since it should be faster
        source = BeautifulSoup(requests.get(self.url).content, "html.parser")
        return source

    @exception_handler
    def extract_tag_text(self, tag: str, attrs: Dict[str, str]) -> Optional[str]:
        """Extract tag text based on an attribute"""
        text = self.source.find(tag, attrs=attrs).text.strip()
        return text

    @exception_handler
    def extract_next_sibling_text(self, tag: str, text: str) -> Optional[str]:
        """Extract tag by text and get value directly after tag"""
        text = self.source.find(tag, text=text).find_next_siblings(text=True)[0].strip()
        return text

    @exception_handler
    def __combine_multiple_tags(self, tag: str, text: str) -> Optional[str]:
        """
        Extract multipe tags text into a single string

        When we grab an element with multple values, for instance `Directors:`,
        we need to combine the results into one string that becomes the column
        value.
        """
        all_tags = self.source.find(tag, text=text).find_next_siblings("a")
        tags = ", ".join(tag.get_text().strip() for tag in all_tags)
        return tags

    def extract_multiple_tags(
        self, tag: str, text: str, singular_text: str = None
    ) -> Optional[str]:
        """
        Extract multiple tags text based on singular or plural form of text

        Certain elements within the page are based on the number of contributors.
        For instance, Director/Directors and Writer/Writers. There is no way to know
        which a title will require. Therefore, we start with the plural form and
        revert to singular form if that fails.
        """
        tags = self.__combine_multiple_tags(tag, text)
        if not tags:
            try:
                tags = self.__combine_multiple_tags(tag, singular_text)
            except Exception as e:
                tags = None
        return tags

    @exception_handler
    def extract_title(self) -> Optional[str]:
        """
        Extract title from H1 tag

        Example
        -------

        The Matrix&nbsp;(1999) -> The Matrix
        """
        # \xa0 -> representation of non-breaking space
        title = self.source.h1.text.split("\xa0")
        title = title[0]
        return title

    @exception_handler
    def extract_awards(self) -> Optional[str]:
        """Extract all awards won"""
        all_awards = self.source.find_all("span", attrs={"class": "awards-blurb"})
        awards = ", ".join(
            re.sub(" +", " ", award.get_text().replace("\n", "").strip())
            for award in all_awards
        )
        return awards

    @exception_handler
    def extract_stars(self) -> Optional[ResultSet]:
        """Extract all stars associated with a film"""
        stars = self.source.find("h4", text="Stars:").find_next_siblings("a")
        return stars

    @staticmethod
    @exception_handler
    def grab_star(stars: ResultSet, star: int) -> Optional[str]:
        """
        Extract a specific star from stars associated with film

        >>> stars = extract_stars()
        >>> star_1 = grab_star(stars, 0)
        >>> star_2 = grab_star(stars, 1)
        """
        star = stars[star].text
        return star

    @exception_handler
    def extract_mpaa_reasoning(self) -> Optional[str]:
        """Extract MPAA reasoning for a film"""
        mpaa_reason = self.source.find("span", text=re.compile("^Rated")).text
        return mpaa_reason

    @exception_handler
    def extract_runtime(self) -> Optional[str]:
        """Extract runtime for a film"""
        runtime = self.source.find("h4", text="Runtime:").find_next_sibling("time").text
        return runtime

    def extract_all_movie_urls(self) -> List[str]:
        """Extract all movie urls from a page"""
        movie_urls = self.source.find_all("h3", attrs={"class": "lister-item-header"})
        return movie_urls

    @staticmethod
    def extract_imdb_id(url: str) -> str:
        """Extract IMDB ID from request URL"""
        return url.split("/")[-2]

    @exception_handler
    def extract_mpaa_rating(self) -> Optional[str]:
        mpaa_rating = self.source.find(
            "div", attrs={"class": "subtext"}
        ).next_element.strip()
        return mpaa_rating
