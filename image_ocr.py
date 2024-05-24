import logging
import os

import easyocr
import numpy as np
import yaml

# Define the set of valid tags
TAGS = {
    '火屬性', '水屬性', '風屬性', '光屬性', '闇屬性',
    '攻擊者', '守護者', '治療者', '妨礙者', '輔助者',
    '人類', '魔族', '亞人',
    '小體型', '中體型',
    '貧乳', '美乳', '巨乳',
    '士兵', '菁英', '領袖',
    '輸出', '保護', '防禦', '回復', '干擾', '支援',
    '削弱', '爆發力', '生存力', '越戰越強', '群體攻擊', '回擊'
}

# Define the template for the YAML file containing word mappings for correcting OCR misread words
YAML_TEMPLATE = """\
# This YAML file contains word mappings for correcting misread words in the 
# Optical Character Recognition (OCR) process.
# Each line in this file represents a mapping from an incorrectly read word 
# (original_word) to the correct word (replacing_word).
#
# Please ensure that:
# - You include the entire word for mapping, not just individual characters.
# - Each mapping follows the format:
#   original_word: replacing_word

土兵: 士兵
"""

# Initialize a logger for this module
logger = logging.getLogger(__name__)

# Initialize the EasyOCR reader
reader = easyocr.Reader(['ch_tra'])


def yaml_to_dict(file_path: str) -> dict:
    """
    Load a YAML file and return its contents as a dictionary.
    If the file does not exist, create it using the predefined template.

    :param file_path: The path to the YAML file.
    :return: A dictionary containing the YAML file contents.
    """
    try:
        # Check if the file exists
        if not os.path.isfile(file_path):
            # Create the directory if it doesn't exist
            directory, filename = os.path.split(file_path)
            os.makedirs(directory, exist_ok=True)
            logger.info(f'Directory created: "{directory}"')

            # Create the file with the YAML template
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(YAML_TEMPLATE)
                logger.info(f'File created: "{file_path}"')

        # Load the YAML file and return its contents as a dictionary
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    except Exception as e:
        logger.warning(f"An exception caught while loading the YAML file: {e}")
        return {}


def img_to_tags(image_arr: np.ndarray) -> list:
    """
    Extract tags from an image using OCR.

    :param image_arr: The input image as a numpy array.
    :return: A list of valid tags found in the image.
    """
    logger.info("Starting OCR process")

    # Perform OCR on the image
    results: list[tuple[list, str, float]] = reader.readtext(image_arr)
    logger.debug(f"OCR raw results: {results}")

    # Extract the recognized words from the OCR results
    result_words = [result[1] for result in results]

    # Find the index of the reference word '招募條件'
    try:
        ref_word_idx = result_words.index('招募條件')
    except ValueError:
        logger.warning("'招募條件' not found in the OCR results")
        return []  # Return an empty list if '招募條件' is not found

    # Limit the scope for filtering tags
    # E.g., ['招募條件', '最多選擇三項', '中體型', '風屬性', '土兵', '亞人', '防禦', '本日剩餘更換2次']
    result_words = result_words[ref_word_idx:ref_word_idx + 8]
    logger.debug(f"Words in scope for tag extraction: {result_words}")

    # Load the word mapping dictionary
    word_mappings = yaml_to_dict("./data/word_mappings.yaml")
    logger.debug(f"Loaded word mappings from 'word_mappings.yaml': {word_mappings}")

    # Replace similar words using the mapping dictionary
    result_words = [word_mappings.get(word, word) for word in result_words]
    logger.debug(f"Words after applying word mappings: {result_words}")

    # Find valid tags by filtering recognized words that are in predefined tags
    tags = [word for word in result_words if word in TAGS]
    logger.info(f"Extracted tags: {tags}")

    return tags


# Example usage (for debugging)
if __name__ == '__main__':
    from PIL import Image

    # Load and convert the image
    image_path = "./test_images/screenshot_1.jpg"
    pil_image = Image.open(image_path).convert('RGB')
    image_np = np.array(pil_image)

    # Extract tags from the image
    extracted_tags = img_to_tags(image_np)
    print(extracted_tags)
