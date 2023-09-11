# 🌐 Easy Chromium Controller

[![PyPI version](https://img.shields.io/badge/PyPI_package-1.0.9-green)](https://pypi.org/project/easy-chromium-controller/)
[![Python Version](https://img.shields.io/badge/Python-3.6_or_higher-blue)](https://www.python.org/)
[![GitHub license](https://img.shields.io/badge/License-MIT-purple)](https://github.com/gonfdez/easy-chromium-controller/blob/main/LICENSE)

Python library for easy control and automation of Chromium.

## ✨ Key features:

- **No need to configure or install anything**, we do it for you.
- Simple interaction with the **Chromium browser**.
- Automated **captcha resolution**.
- Useful **functions for web automation tasks**.
- Intercept **network traffic**.
- **Screenshots** of web pages and elements.
- Web element handling using **locators**.
- **Docker compatible**.

## 📋 Requirements

Python 3.6 or higher.

## 🚀 Installation

To install easy-chromium-controller, you can use pip:
```bash
pip install easy-chromium-controller
```

## 💡 Usage

Basic example:
```python
from easy_chromium_controller import PageEnum, Browser, By

# Setup windows
class Windows(PageEnum):
  GOOGLE = 0

# Create a browser instance
browser = Browser()
browser.open(Windows)  # Open the browser

# Navigate to a URL
browser.goTo('https://www.google.com')

# Perform actions on the page
browser.click((By.XPATH, '/html/body/div[2]/div[3]/div[3]/span/div/div/div/div[3]/div[1]/button[1]/div') )
element = browser.findElement((By.CSS_SELECTOR, 'textarea[aria-activedescendant][role="combobox"]'))
element.send_keys('This is the magic of "easy-chromium-controller"')

input('Press any key to exit test...')

# Close the browser
browser.close()
```

## 📖 Full Documentation
You can find the complete documentation in the official [**documentation**](easy-chromium-controller.dev/docs).

## 📝 License
This project is licensed under the MIT License. For more details, see the [LICENSE](https://github.com/gonfdez/easy-chromium-controller/blob/main/LICENSE) file.
