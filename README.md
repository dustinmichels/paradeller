# :black_nib: Paradeller

Paradeller is a robo-poet that scours Twitter in search of fodder for [paradelle poems](http://www.shadowpoetry.com/resources/wip/paradelle.html).

## Setup

### 1) Install [Git Large File Storage](https://git-lfs.github.com/)

```bash
# MacOS
brew install git-lfs

# Linux
sudo apt-get install git-lfs
```

### 2) Clone Repo

```bash
git clone https://github.com/dustinmichels/paradeller.git
cd paradeller

# Initialize large file storage
git lfs install
```

### 3) Install Python Dependencies

```bash
# dev
pipenv install --dev
pipenv shell
jupyter labextension install @jupyter-widgets/jupyterlab-manager

# prod
pip -r requirements.txt
```

### 4) _[Optional]_ Twitter API Keys

If you will be scraping tweets:

- Create Twitter API credentials
- Copy keys template: `cp paradeller/keys.template.py paradeller/keys.py`
- Populate `keys.py` with API credentials

## Usage

### Scraping Tweets

Scrape tweets using Tweepy.

```bash
python -m paradeller.scrape
python -m paradeller.scrape 100
```

- Optional CLI argument is the number of iterations of `get_tweets` to perform.
- Each iteration will scrape about 100 tweets, filter that collection down, then save to `data/archive.json`.
- Scraper will automatically pause when rate limits are hit and resume when possible.

Can easily run with default of 10,000 tweets using:

```bash
./scrape.sh
```

### Analyzing Tweets

To search for paradelles in the saved tweets, use `paradeller/run.py`.

```bash
python -m paradeller.run
python -m paradeller.run 1000
```

- Optional CLI argument is number of ids to pair off as initial pairs

Can easily run with default of 1,000 ids using:

```bash
./search.sh
```

## Dev Notes

To generate `requirements.txt` from `Pipefile`:

```bash
pipenv lock -r > requirements.txt
```
