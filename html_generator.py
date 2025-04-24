# importation part -------------------------------------------------------------------------------------------#
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
import pickle
import re
import traceback
from typing import List, Dict, Any

# global variable and initialization -------------------------------------------------------------------------#
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
dictionary_list: List[List[tuple]] = pickle.load(
    open('Scraping/Jennie_Bairfern_new_vocab_sorted_dictionary_lookup.pickle', 'rb')
)

# helper functions -------------------------------------------------------------------------------------------#

def rows_items_extractor() -> List[Dict[str, Any]]:
    """
    Extracts and processes sections from the text file `Text_to_translate.txt`.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing:
            - 'first_part': title or identifier string
            - 'second_part': Thai sentence
            - 'content': translated dictionary items in the sentence
    """
    with open('Scraping/Text_to_translate.txt', 'r', encoding='utf-8') as file:
        raw_list = re.split(r'\n{2,}', file.read())
        return [
            {
                'first_part': section.split('\n')[0],
                'second_part': section.split('\n')[1],
                'content': get_row_sentences_item(section.split('\n')[1])
            }
            for section in raw_list[1:-1]  # Skip first and last if not content
        ]

def get_row_sentences_item(thai_sentence: str) -> Dict[str, List[str]]:
    """
    Translates words in the given Thai sentence using the loaded dictionary list.

    Args:
        thai_sentence (str): The Thai sentence to be translated.

    Returns:
        Dict[str, List[str]]: A dictionary where each key is a Thai word found,
        and the value is a list of translation strings.
    """
    item: Dict[str, List[str]] = defaultdict(list)
    for dictionary_item in dictionary_list:
        for tuple_item in dictionary_item:
            word = tuple_item[2]
            translation = tuple_item[4]
            if word in thai_sentence and translation != 'Word not found in dictionary':
                index = len(item[word]) + 1
                item[word].append(f'{index} {word}: {translation}')
    return item

# main logic -------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    try:
        rows = rows_items_extractor()
        template = env.get_template('index.html')
        with open('templates/test.html', 'w', encoding='utf-8') as file:
            file.write(template.render(rows=rows))
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
