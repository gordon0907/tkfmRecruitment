import logging

import easyocr
import numpy as np

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

# TODO: Move this dictionary to a YAML file for better maintainability and configuration
# Define a dictionary to map similar words to actual tags
SIMILAR_WORD_MAP = {
    '土兵': '士兵',
    '人頸': '人類',
    '妨暱者': '妨礙者',
    '庭族': '魔族',
    '中腥型': '中體型',
    '鞘出': '輸出',
}

# Initialize a logger for this module
logger = logging.getLogger(__name__)

# Initialize the EasyOCR reader
reader = easyocr.Reader(['ch_tra'], gpu=False)  # Disable GPU


def img_to_tags(image_arr: np.ndarray) -> set:
    """
    Extract tags from an image using OCR.

    :param image_arr: The input image as a numpy array.
    :return: A set of valid tags found in the image.
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
        return set()  # Return an empty set if '招募條件' is not found

    # Limit the scope for filtering tags
    # E.g., ['招募條件', '最多選擇三項', '中體型', '風屬性', '土兵', '亞人', '防禦', '本日剩餘更換2次']
    result_words = result_words[ref_word_idx:ref_word_idx + 8]
    logger.debug(f"Words in scope for tag extraction: {result_words}")

    # Replace similar words using the mapping dictionary
    result_words = [SIMILAR_WORD_MAP.get(word, word) for word in result_words]
    logger.debug(f"Words after applying similar word mapping: {result_words}")

    # Find valid tags by intersecting recognized words with predefined tags
    tags = TAGS.intersection(result_words)
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
