# :black_nib: Paradeller

Paradeller is a robo-poet that scours Twitter in search of fodder for [paradelle poems](http://www.shadowpoetry.com/resources/wip/paradelle.html). A paradelle is a poem that looks like this:

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

("A Paradelle of Winged Flight", Mary Ellen Clark, 2003).

For the first three stanzas:

- The first line and the third line repeat.
- The final two lines (5 & 6) use all the words from lines 1 & 3.

For the final stanza:

- Use all the words from the previous stanzas.

## Setup

```bash
pipenv install --dev
pipenv shell
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

Create Twitter API credentials and populate `keys.py`

```bash
cp paradeller/keys.template.py paradeller/keys.py
```

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

### Analyzing Tweets

To search for paradelles in the saved tweets, use `paradeller/run.py`.

```bash
python -m paradeller.run 1000
```
