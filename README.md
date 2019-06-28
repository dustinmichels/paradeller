# :black_nib: Paradeller

Paradeller is a robo-poet that scours Twitter in search of fodder for [paradelle poems](http://www.shadowpoetry.com/resources/wip/paradelle.html).

## Setup

```bash
pipenv install --dev
pipenv shell
jupyter labextension install @jupyter-widgets/jupyterlab-manager

# fill out twitter credentials
mv paradeller/keys.template.py paradeller/keys.py
```
