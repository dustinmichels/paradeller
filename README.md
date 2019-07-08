# :black_nib: Paradeller

Paradeller is a robo-poet that scours Twitter in search of fodder for [paradelle poems](http://www.shadowpoetry.com/resources/wip/paradelle.html).

## Setup

### 1) Install [Git Large File Storage](https://git-lfs.github.com/)

```bash
# MacOS
brew install git-lfs

# Linux
sudo apt-get install git-lfs

# Initialize
git lfs install
```

### 2) Clone Repo

```bash
git clone https://github.com/dustinmichels/paradeller.git
cd paradeller
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

## About

A paradelle is a poem that looks like this:

> Twilight falls, darkness cover me  
> Twilight falls, darkness cover me  
> as gentle slumber lures awakening dreams  
> as gentle slumber lures awakening dreams  
> cover me gentle twilight, darkness lures dreams,  
> awakening as slumber falls.
>
> Journey on celelstial wings through astral visions  
> Journey on celelstial wings through astral visions  
> and hover above earth-bound limitations  
> and hover above earth-bound limitations  
> on celestial wings, hover above earth bound limitations  
> and journey through astral visions.
>
> Explore the expansiveness of self,  
> Explore the expansiveness of self,  
> look within and discover your untapped wealth  
> look within and discover your untapped wealth  
> look within the expansiveness of self,  
> discover and explore your untapped wealth.
>
> cover me, dreams look within darkness  
> journey -- discover your gentle awakening;  
> slumber lures the expansiveness of self  
> through astral visions. Hover above  
> earthbound limitations on celestial wings,  
> and as twilight falls, explore wealth -- untapped.
>
> _("A Paradelle of Winged Flight", Mary Ellen Clark, 2003.)_

The rules are fairly simple.

For the first three stanzas:

- Lines 1 & 3 must repeat.
- Lines 5 & 6 must use all the words from lines 1 & 3 (no more no less).

For the final stanza, you must use all the words from lines 1 & 3 of the previous stanzas.

## Dev

To generate `requirements.txt` from `Pipefile`:

```bash
pipenv lock -r > requirements.txt
```
