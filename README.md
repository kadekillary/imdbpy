![logo](https://miro.medium.com/max/18708/1*WgMZ_JII2WFKMIEtbWeTHg.jpeg)

## Installation

* Install library dependencies

```python
pip3 install -r requirements.txt
```

## Example Usage

* Grab movie details by `imdb_id`

```python
from imdbpy import IMDb

imdb = IMDb()

imdb.get_movie_by_id("tt4154796")
```

* Grab first 3 pages (top 150 results) for most popular films

```python
import concurrent.futures

from imdbpy import IMDb

imdb = IMDb()

pages = imdb.get_page_urls(number_of_pages=3)

for page in pages:
    movie_urls = imdb.get_movie_urls(page)

    movie_data = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(imdb.get_movie_data, url) for url in movie_urls}
        for future in concurrent.futures.as_completed(futures):
            movie_data.append(future.result())
```

* All sort methods supported by `get_page_urls(sort_method="")`

```text
- none (default) -> popularity
- num_votes
- boxoffice_gross_us
- runtime
- year
- release_date
- user_rating
- alpha
```
