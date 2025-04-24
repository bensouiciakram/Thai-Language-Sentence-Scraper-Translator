# importation part ---------------------------------------------------------------------------------------#
from requests import Session, Response
from re import findall
from parsel import Selector, SelectorList
import logging
from typing import List, Tuple, Union, Optional
from pprint import pprint

# payload for setting the site
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(message)s'
)

settings_payload: dict[str, str] = {
    # ... (unchanged dictionary)
}

word_payload: dict[str, str] = {
    'search': '',
    'emode': '0',
    'tmode': '0'
}

item_regex: str = r'/id/\d+'
session: Session = Session()

# helper functions ---------------------------------------------------------------------------------------#

def settings_setter() -> None:
    """
    Posts configuration settings to the target site.
    """
    global session, settings_payload
    logging.info('Posting the configuration to the site.')
    session.post(
        'http://www.thai-language.com/default.aspx?nav=control',
        data=settings_payload
    )

def words_extractor() -> List[str]:
    """
    Extracts a list of words from a file.
    Returns:
        List[str]: A list of word strings.
    """
    with open('Scraping/Test_list.txt', 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines

def get_sample_sentences(td: Selector) -> List[Tuple[str, str]]:
    """
    Extracts sample sentences from a given HTML table cell.

    Args:
        td (Selector): The table cell selector containing the data.

    Returns:
        List[Tuple[str, str]]: A list of (Thai sentence, English translation) tuples.
    """
    sentences: List[Tuple[str, str]] = []
    try:
        following_rows_count = int(td.xpath('./@rowspan').get())
        rows = td.xpath('./following-sibling::td[1]') + td.xpath(
            './ancestor::tr[1]/following-sibling::tr[position() < {}]'.format(following_rows_count)
        )
    except TypeError:
        rows = td.xpath('./following-sibling::td[1]')

    for row in rows:
        try:
            sentences.append((
                row.xpath('string(.//span[@class="th"])').get(),
                row.xpath('.//div[@class="igt"]/text()').get().replace('"', '')
            ))
        except AttributeError:
            continue
    return sentences

def get_sentences_id(td: Selector) -> int:
    """
    Extracts the ID of a sentence block from a given table cell.

    Args:
        td (Selector): The selector of the current cell.

    Returns:
        int: The ID of the sentence.
    """
    preceding_rows = td.xpath('./ancestor::tr[1]/preceding-sibling::tr[descendant::td[@colspan]]')
    id_selector = [p for p in preceding_rows if findall('^[1-9]+', p.xpath('string(.)').get())][-1]
    return int(findall('^([1-9]+)', id_selector.xpath('string(.)').get())[0])

# the main function ----------------------------------------------------------------------------------#

def words_scraper(word: str) -> Union[bool, Tuple[str, str, str, List[Tuple[str, str]]], List[Tuple]]:
    """
    Scrapes the Thai-language site for definitions and sample sentences.

    Args:
        word (str): The word to be searched.

    Returns:
        Union[bool, Tuple, List[Tuple]]: The result can be:
            - False if no result is found.
            - A tuple containing one word's info if it's a single result.
            - A list of tuples if multiple results are found.
    """
    global word_payload
    word_payload['search'] = word
    response: Response = session.post('http://www.thai-language.com/dict', data=word_payload)

    if response.url.endswith('dict'):
        selector = Selector(text=response.text)
        if 'Sorry, there were no results' in response.text:
            logging.info('No results found.')
            return False

        elif selector.xpath('//table[@class="gridtable"]'):
            response = session.get(
                'http://www.thai-language.com/' +
                selector.xpath('//td[contains(text(),"1.")]/following-sibling::td[1]/a[not(@onclick)][last()]/@href').get()
            )
            selector = Selector(text=response.text)
            rows = selector.xpath('//tr[descendant::td[contains(text(),"contents of this page")]]/following-sibling::tr')

            if rows and len(rows[0].xpath('.//td')) == 4:
                logging.info('Several results found.')
                items: List[Tuple[str, str, str, str, str, List[Tuple[str, str]]]] = []
                for row in rows:
                    items.append((
                        row.xpath('string(./td[1])').get().replace('.', ''),
                        response.url + row.xpath('./td[1]/a/@href').get(),
                        row.xpath('string(./td[2])').get(),
                        row.xpath('string(./td[3])').get(),
                        row.xpath('string(./td[4])').get(),
                        []
                    ))

                tds = selector.xpath('//td[contains(text(),"sample")]')
                for td in tds:
                    sentences = get_sample_sentences(td)
                    sentences_id = get_sentences_id(td)
                    item_list = list(items[sentences_id - 1])
                    item_list[-1] = sentences
                    items[sentences_id - 1] = tuple(item_list)
                pprint(items)
                return items

            else:
                sels = selector.xpath('//tr[descendant::td[contains(text(),"contents of this page")]]/following-sibling::tr')
                if not sels:
                    logging.info('Single result found.')
                    try:
                        td = selector.xpath('//td[contains(text(),"sample")]')[0] if selector.xpath('//td[contains(text(),"sample")]') else None
                        sentences = get_sample_sentences(td) if td else []
                    except IndexError:
                        sentences = []

                    item = (
                        selector.css('span.th3::text').get(),
                        selector.xpath('string(//span[@class="th3"]/following-sibling::span)').get(),
                        selector.xpath('string(//td[contains(text(),"definition")]/following-sibling::td)').get(),
                        sentences
                    )
                    pprint(item)
                    return item
                else:
                    logging.info('Multiple results found.')
                    items = [
                        (
                            selector.css('span.th3::text').get(),
                            selector.xpath('string(//span[@class="th3"]/following-sibling::span)').get(),
                            sel.xpath('string(.//td[last()])').get(),
                            []
                        ) for sel in sels
                    ]

                    tds = selector.xpath('//td[contains(text(),"sample")]')
                    for td in tds:
                        sentences = get_sample_sentences(td)
                        sentences_id = get_sentences_id(td)
                        item_list = list(items[sentences_id - 1])
                        item_list[-1] = sentences
                        items[sentences_id - 1] = tuple(item_list)
                        pprint(items)
                    return items

    elif findall(item_regex, response.url):
        logging.info('No duplicate URLs.')
        selector = Selector(text=response.text)
        return (
            selector.css('span.th3::text').get(),
            selector.xpath('string(//span[@class="th3"]/following-sibling::span)').get(),
            selector.xpath('string(//td[contains(text(),"definition")]/following-sibling::td)').get()
        )


# run the script --------------------------------------------------------------------------------------#
if __name__ == '__main__':
    words: List[str] = words_extractor()
    settings_setter()
    for index, word in enumerate(words):
        logging.info(f'{index} - scraping the word: {word}')
        words_scraper(word)
