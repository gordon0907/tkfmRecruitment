import asyncio
import io
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import TimedOut
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest

from image_ocr import img_to_tags
from tkfmtools import recruitment_query

# Initialize a logger for this module
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User '{user.username}' (ID: {user.id}) has initiated the `/start` command")

    # Send the welcome message
    await update.message.reply_text(
        r"""
你好！歡迎使用 *TKFM 全境徵才*。🎉🎉

這是一個 *半自動* 的徵才標籤篩選助手。🤖

*【使用指引】*
1️⃣ 在遊戲內的「招募頁面」截圖。
2️⃣ 將截圖傳送到此對話視窗。

*【注意事項】*
⚠️ 目前只支援 *繁體中文* 遊戲界面。
🖼️ 請確保截圖清晰，以便讀取截圖內容。
📱 iPhone 用戶請避免使用 `跨應用程式拖放` 功能，該功能會明顯降低圖片清晰度。
📐 傳送未裁剪的全屏截圖即可。如自行進行裁剪，請保留標籤上方的 `招募條件` 四字，用作讀取時的位置參考。
        """,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    logger.info(f"Sent welcome message in chat {update.effective_chat.id}")


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def overwrite_message_text(message, new_text):
        """
        Update an existing message with new text.
        """
        updated_message = await context.bot.edit_message_text(
            text=new_text,
            chat_id=update.effective_chat.id,
            message_id=message.message_id,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        logger.info(f'Updated message in chat {update.effective_chat.id} with text: "{updated_message.text}"')

    user = update.effective_user
    logger.info(f"Received an image from user '{user.username}' (ID: {user.id}) in chat {update.effective_chat.id}")

    # Send initial status message in the form of a reply message (1/4)
    reply_message = await update.message.reply_text(
        r"⬇️ *正在下載圖片\.\.\.* _\(1/4\)_",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_to_message_id=update.message.message_id
    )
    logger.info(f'Sent reply message in chat {update.effective_chat.id} with text: "{reply_message.text}"')

    # Download the image
    image_file = await update.message.photo[-1].get_file()  # Get the highest resolution version
    image_bytearray = await image_file.download_as_bytearray()

    # Update status (2/4)
    await overwrite_message_text(reply_message, r"🔍 *正在提取圖片中的文字\.\.\.* _\(2/4\)_")

    # Convert the image to a NumPy array
    pil_image = Image.open(io.BytesIO(image_bytearray))
    image_np = np.array(pil_image)

    # Extract tags using OCR
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        # Run a blocking synchronous function inside an asynchronous function
        extracted_tags = await loop.run_in_executor(pool, lambda: img_to_tags(image_np))

    if len(extracted_tags) != 5:
        # Handle extraction exception
        await overwrite_message_text(reply_message, "❌ *抱歉，無法從圖片中提取文字。請嘗試其他圖片。*")
        return

    # Update status (3/4)
    await overwrite_message_text(reply_message, r"📜 *正在篩選可行的標籤組合\.\.\.* _\(3/4\)_")

    # Perform recruitment query
    with ThreadPoolExecutor(max_workers=1) as pool:
        # Run a blocking synchronous function inside an asynchronous function
        pdf_bytes_io = await loop.run_in_executor(pool, lambda: recruitment_query(extracted_tags))

    if pdf_bytes_io is None:
        # Handle query exception
        await overwrite_message_text(reply_message, "❌ *抱歉，標籤組合篩選失敗。請稍後再試。*")
        return

    # Update status (4/4)
    await overwrite_message_text(reply_message, r"📤 *正在傳送結果\.\.\.* _\(4/4\)_")

    # Send the result PDF
    while True:
        try:
            await update.message.reply_document(
                pdf_bytes_io,
                reply_to_message_id=update.message.message_id,
                filename=f"{str(extracted_tags).replace("'", '')}.pdf"
            )
            break
        except TimedOut:
            pdf_bytes_io.seek(0)
    logger.info(f"Sent result PDF document as a reply message in chat {update.effective_chat.id}")

    # Delete the status message
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=reply_message.message_id
    )
    logger.info(
        f"Deleted status message in chat {update.effective_chat.id} with message_id: {reply_message.message_id}"
    )


async def handle_non_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(
        f"Received a non-image message from user '{user.username}' (ID: {user.id}) in chat {update.effective_chat.id}"
    )

    reply_message = await update.message.reply_text(
        "⚠️ *請傳送圖片，而非文字或其他格式的媒體* ⚠️",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_to_message_id=update.message.message_id
    )
    logger.info(f'Sent reply message in chat {update.effective_chat.id} with text: "{reply_message.text}"')


def main(token: str):
    # Build the application
    request = HTTPXRequest(connection_pool_size=20, read_timeout=60)  # 60 seconds
    application = ApplicationBuilder().token(token).request(request).build()

    # Register the /start command handler
    application.add_handler(CommandHandler('start', start))

    # Register the handler for photo messages
    application.add_handler(MessageHandler(filters.PHOTO, handle_image, block=False))

    # Register the handler for non-photo messages
    application.add_handler(MessageHandler(~filters.PHOTO, handle_non_image))

    # Start polling for updates
    application.run_polling()


if __name__ == '__main__':
    # Configure the logging format and logging level
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Retrieve environment variable
    token_ = os.getenv('TELEGRAM_BOT_TOKEN')
    if token_ is None:
        logger.error("Environment variable `TELEGRAM_BOT_TOKEN` is not set. Please set this variable to run the bot.")
        sys.exit(1)

    main(token_)
