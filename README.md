# Thai Language Sentence Scraper & Translator

This repository contains two Python scripts for scraping sample sentences from [Thai-language.com](http://www.thai-language.com) and generating a translated HTML output for language learning and study purposes.

## 📜 Scripts Overview

### `dict_scraper.py`

Scrapes example sentences and definitions for Thai words from Thai-language.com.

#### Features:
- Posts site configuration to enable certain options (IPA, Romanization, etc.)
- Loads words from `Test_list.txt`
- Extracts example sentences, English meanings, and structural information
- Outputs scraped items via `pprint`

#### Usage:
```bash
python dict_scraper.py
```

## html_generator.py 
This script translates Thai sentences by looking up words in a predefined dictionary and generating an HTML file that displays the translated content.

### Features:
- Reads Thai sentences from `Text_to_translate.txt`.
- Uses the `Jennie_Bairfern_new_vocab_sorted_dictionary_lookup.pickle` file to find matching dictionary entries for words in the sentences.
- Renders the sentences and their translations into an HTML file using the Jinja2 template system.
- Outputs the translated content in a format suitable for language learning.

### Usage 
```bash
python html_generator.py
```
This script will read the Thai sentences, search for dictionary entries, and generate an HTML output (`templates/test.html`) containing the translated sentences and their respective dictionary definitions.
Let me know if you'd like to make any additional changes!

## 🔧 Requirements
Install dependencies via pip:
```bash
pip install -r requirements.txt
```
Python version: `>=3.7`

## 📂 Data Files
Make sure the following files exist:
- Scraping/Test_list.txt: List of Thai words to scrape
- Scraping/Text_to_translate.txt: Raw Thai text for translation
- Scraping/Jennie_Bairfern_new_vocab_sorted_dictionary_lookup.pickle: Pickled list of matched words and definitions





