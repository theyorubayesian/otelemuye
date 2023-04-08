# Ọ̀tẹlẹ̀múyẹ́

`Ọ̀tẹlẹ̀múyẹ́` means detective in Yoruba.

This project, `Ọ̀tẹlẹ̀múyẹ́` provides an extensible framework for scraping websites. It relies on Scrapy and provides a Selenium middleware to handle dynamic content.

## 🎬 Installation

* Create a conda environment

```bash
conda create -n otelemuye python=3.9
conda activate otelemuye
```

* Run the following command to install this project

```bash
pip install .
```

* If you would like a development installation instead, use the following command

```bash
pip install -e ".[dev]"
```

## Setup 🛠️

* You can find a list of existing `spiders` [here](src/otelemuye/spiders/README.md).

* See [example.ipynb](notebooks/example.ipynb) to see notebook examples of how you can create your own Spider and start crawling.

* To use this tool via command line, you will require a development installation. See [Installation](#🎬-installation)

* You can create a new spider using the following command:

```bash
otelemuye create-spider --template template/sitemap --spider-name <YourSpiderName> --language <Language>
```

## Contribution

* You will require a development installation in order to contribute a Spider to this repository. See [Installation](#🎬-installation)

* To contribute new crawlers, extend `otelemuye.SitemapSpider` or `otelemuye.Spider` and provide concrete implementations of the abstract methods.

* You will also need to provide a template config file in [config/](config). Your filename should be name of the spider class you created e.g. `legitng.yaml` is the config file for `LegitNGSpider`.

* See [LegitNGSpider](src/otelemuye/spiders/legitng.py) for guidance if your crawler requires Selenium to load dynamic content.

* You can run start crawling by running a command similar to:

```bash
otelemuye run-till-complete --spider-class LegitNGSpider --check-interval 300
```
Note that `--check-interval` is only used when the Selenium middleware is in use.

* To see other commands, configurations and functionalities

```bash
otelemuye --help
```
