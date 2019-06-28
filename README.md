# :black_nib: Paradeller

Paradeller is a robo-poet that scours Twitter in search of fodder for [paradelle poems](http://www.shadowpoetry.com/resources/wip/paradelle.html).

## Setup

```bash
pipenv install --dev
pipenv shell
jupyter labextension install @jupyter-widgets/jupyterlab-manager

# fill out twitter credentials
cp paradeller/keys.template.py paradeller/keys.py
```

## Usage

### Scraping Tweets

Scrape tweets using Scrapy.

```bash
python -m paradeller.scrape
python -m paradeller.scrape 100
```

- Optional CLI argument is the number of iterations of `get_tweets` to perform.
- Each iteration will scrape about 100 tweets, filter that collection down, then save to archive.
- Scraper will automatically pause when rate limits are hit and resume when possible.
