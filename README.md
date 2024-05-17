# tkfmRecruitment

![Python](https://img.shields.io/badge/python-3.12-blue)

This repository contains a Telegram bot for automatically querying recruitment tag combinations from
the [TenkafuMA! toolbox](https://purindaisuki.github.io/tkfmtools/enlist/filter/) for the TenkafuMA! mobile game.

## Table of Contents

- [Demo](#demo)
- [Installation](#installation)
    - [Python Environment](#python-environment)
    - [Docker Container](#docker-container)
- [Usage](#usage)
- [Configuration](#configuration)
    - [User-defined OCR Word Replacement](#user-defined-ocr-word-replacement)
- [Additional Information](#additional-information)
    - [Enable GPU](#enable-gpu)
    - [Cannot Read Text from the Screenshot](#cannot-read-text-from-the-screenshot)
    - [Multi-language Support](#multi-language-support)
- [Credit](#credit)
- [License](#license)

## Demo

<p>
  <img src="./images/demo_1.png" alt="Demo 1" style="width: 45%; display: inline-block; margin-right: 5%;">
  <img src="./images/demo_2.png" alt="Demo 2" style="width: 45%; display: inline-block;">
</p>

## Installation

### Python Environment

1. **Clone the Repository**

    ```sh
    git clone https://github.com/gordon0907/tkfmRecruitment.git
    cd tkfmRecruitment
    ```

2. **Install Required Modules**

    ```sh
    pip install -r requirements.txt
    ```

3. **Define Telegram Bot Token**

   If you don't already have a Telegram bot token, you can obtain one from [BotFather](https://telegram.me/BotFather).

    - **Unix**

      ```sh
      # Replace "your-telegram-bot-token" with your actual Telegram bot token
      export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
      ```

    - **Windows (cmd)**

      ```sh
      # Replace "your-telegram-bot-token" with your actual Telegram bot token
      set TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
      ```

4. **Run the Script**

    ```sh
    python main.py
    ```

   Note: You may need to install additional dependencies as per the module's instructions.

### Docker Container

1. **Clone the Repository**

    ```sh
    git clone https://github.com/gordon0907/tkfmRecruitment.git
    cd tkfmRecruitment
    ```

2. **Build the Docker Image**

    ```sh
    sudo docker build --tag tkfm-recruitment .
    ```

3. **Run the Docker Image in a Container**

    ```sh
    # Replace "your-telegram-bot-token" with your actual Telegram bot token
    # Replace "/path/to/local/data" with the path to your local data directory
    sudo docker run --env TELEGRAM_BOT_TOKEN="your-telegram-bot-token" --volume /path/to/local/data:/app/data tkfm-recruitment
    ```

4. **Save the Docker Image**

   If you need to save the Docker image for future use:

    ```sh
    sudo docker save --output tkfm-recruitment.tar tkfm-recruitment
    ```

## Usage

1. **Start the Bot**: Use the `/start` command in the Telegram chat to receive a welcome message.
2. **Send a Screenshot**: Send a screenshot of the Recruitment page in TKFM to the bot via Telegram as a photo (not as a
   file). The bot will reply with the query result in PDF format in the chat.

## Configuration

### User-defined OCR Word Replacement

To handle OCR misreading similar words, you can add word mappings for replacement in `./data/word_mappings.yaml`. This
file is generated after the first run and supports hot-editing, meaning you can edit `word_mappings.yaml` anytime
without restarting the bot.

## Additional Information

### Enable GPU

By default, the OCR process does not utilize the GPU. To enable CUDA or MPS, you must install `torch` and `torchvision`
before installing `easyocr`. For the installation command, please refer to the
official [PyTorch](https://pytorch.org/get-started/locally/) page.

For Docker users, you may need to modify the `Dockerfile` accordingly.

Refer to [EasyOCR](https://github.com/JaidedAI/EasyOCR) for more details on enabling GPU for the OCR process.

### Cannot Read Text from the Screenshot

If the OCR fails to read text from the image, it is likely due to low image quality. In this case, try cropping the tags
section and sending it to the bot. Ensure the word `招募條件` is included in the image, as it is used as a reference
point during the tags filtering process.

For iOS users, **do not** use the Drag-and-Drop screenshot function, as it significantly reduces image quality.

### Multi-language Support

Currently, there are no plans to support other languages for the game interface. However, you can manually change the
language settings by editing `image_ocr.py` and `tkfmtools.py`. You can also modify `main.py` to support other languages
for the Telegram bot.

## Credit

[TenkafuMA! toolbox](https://github.com/purindaisuki/tkfmtools)

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE.md) file for details.

© 2024 gordon0907
