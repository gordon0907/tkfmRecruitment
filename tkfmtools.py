import io
import logging

from PIL import Image
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

# Initialize a logger for this module
logger = logging.getLogger(__name__)


def recruitment_query(tags: list) -> io.BytesIO | None:
    """
    Performs a recruitment query using the specified tags and returns the results as a PDF.

    :param tags: A list of tags to apply in the query.
    :return: A BytesIO object containing the PDF file if the query is successful, or None if a timeout occurs.
    """
    logger.info(f"Starting recruitment query with tags: {tags}")

    with sync_playwright() as p:
        # Launch the browser
        logger.debug("Launching browser")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 2160, 'height': 17280})  # 1:8 aspect ratio
        page = context.new_page()

        # Set default timeout
        page.set_default_timeout(10000)  # 10 seconds

        try:
            # Navigate to the TenkafuMA Toolbox
            logger.debug("Navigating to TenkafuMA Toolbox")
            page.goto("https://purindaisuki.github.io/tkfmtools/enlist/filter/")

            # Wait until the page is fully loaded (i.e., all 7 tag categories are present)
            logger.debug("Waiting for the page to load completely")
            page.wait_for_function("['屬性', '定位', '種族', '體型', 'ㄋㄋ', '階級', '其他']"
                                   ".every(word => document.body.innerText.includes(word));")

            # Open the settings menu
            logger.debug("Opening settings menu")
            page.get_by_label('顯示設定').click()

            # Change the result display format
            logger.debug("Changing result display format to '依標籤組合'")
            page.get_by_label('依標籤組合').click()

            # Close the settings menu
            logger.debug("Closing the settings menu")
            page.get_by_text('×').click()

            # Click on each tag in the `tags` list
            for tag in tags:
                logger.debug(f"Selecting tag: {tag}")
                page.get_by_text(tag).click()

            # Wait for all images to load completely
            logger.debug("Waiting for all images to load completely")
            page.wait_for_function("Array.from(document.getElementsByTagName('img')).every(img => img.complete);")

            # Capture the result as image bytes
            logger.debug("Capturing the result as an image")
            screenshot_bytes = page.locator('table').screenshot()

            # Convert bytes to a PIL image
            logger.debug("Converting screenshot bytes to a PIL image")
            pil_image = Image.open(io.BytesIO(screenshot_bytes))

            # Convert to 'RGB' for consistency across platforms (Windows: 'RGBA', macOS: 'RGB')
            pil_image = pil_image.convert('RGB')

            # Save the PIL image as a PDF in a BytesIO object
            logger.debug("Saving the PIL image as a PDF")
            pdf_bytes_io = io.BytesIO()
            pil_image.save(pdf_bytes_io, 'PDF', quality=100)

            # Reset the seek position to the beginning of the BytesIO object
            pdf_bytes_io.seek(0)

            logger.info("Recruitment query completed successfully")
            return pdf_bytes_io

        except PlaywrightTimeoutError:
            logger.error("Timeout occurred during the recruitment query")
            return None

        finally:
            # Ensure resources are closed properly
            logger.debug("Closing page, context, and browser")
            page.close()
            context.close()
            browser.close()


# Example usage (for debugging)
if __name__ == '__main__':
    example_tags = ['中體型', '風屬性', '士兵', '亞人', '防禦']
    result = recruitment_query(example_tags)

    if result:
        # Save the result to a PDF file
        with open("./recruitment_query_debug.pdf", 'wb') as f:
            f.write(result.getvalue())
            print(f'Saved result to "{f.name}".')
    else:
        print("Query failed.")
