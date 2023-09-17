# Kabupy: A Python Library for Japanese Stock Market Analysis

[![codecov](https://codecov.io/gh/ReiRev/kabupy/graph/badge.svg?token=3G3EEB7KEZ)](https://codecov.io/gh/ReiRev/kabupy)

Kabupy is a Python library that aims to provide easy and fast access to various data sources and tools for Japanese stock market analysis.
Currently it supports fetching technical and fundamental data from the following site.

- kabuyoho.jp

The following website will be supported in the future version.

- minkabu.jp
- www.nikkei.com
- kabutan.jp
- www.sbisec.co.jp
- www.bloomberg.co.jp
- moneyworld.jp
- shikiho.toyokeizai.net

## Installation

Kabupy is available on PyPI.

```bash
pip install kabupy
```

## Usage

To use Kabupy, you need to import it in your Python script or notebook:

```python
import kabupy
```

Then you can use the various modules and functions provided by Kabupy.
For example, you can fetch Stock object of Sony Corporation (6758) from kabuyoho.jp using the `kabupy.kabuyoho.stock`:

```python
stock = kabupy.kabuyoho.stock(6758)
```

The Stock object has various properties that you can use to fetch the data you need.
Note that `stock.report_target` corresponds to [https://kabuyoho.jp/sp/reportTarget?bcode=6758](https://kabuyoho.jp/sp/reportTarget?bcode=6758).

```python
price = stock.report_target.price
ceiling = stock.report_target.per_based_ceiling
floor = stock.report_target.per_based_floor
```

For more examples and details on how to use Kabupy, please refer to the [documentation](https://reirev.github.io/kabupy/index.html).

## License
Kabupy is licensed under the MIT License. See the [LICENSE file](LICENSE) for more information.

## Disclaimer
Kabupy is provided for educational and research purposes only. It is not intended to be used for any financial or investment decisions. The author of Kabupy is not responsible for any losses or damages caused by using Kabupy. Please use Kabupy at your own risk and discretion.

Kabupy uses web scraping techniques to fetch data from various websites. Web scraping is a method of extracting information from web pages by using programs. Web scraping may involve legal, ethical, and technical issues depending on the target website and the purpose of use. Please be aware of the following points when using Kabupy:

Respect the terms of use of the target website. Some websites may prohibit or restrict web scraping in their terms of use. Violating the terms of use may result in legal actions or penalties from the website owner.

Check if the target website provides an official API. An API is a way of accessing information from a website in a standardized and authorized manner. Using an API is preferable to web scraping as it reduces the risk of violating the law or the terms of use, and it also reduces the load on the target website.
Do not overload the target website with excessive requests. Web scraping may cause a heavy load on the target website, which may affect its performance or availability. This may be considered as a denial-of-service attack, which is illegal in some countries. To avoid this, limit the frequency and volume of your requests, and use a reasonable delay between requests.

Do not use the scraped data for illegal or unethical purposes. Web scraping may involve accessing personal or sensitive information from the target website. You must respect the privacy and intellectual property rights of the data owner, and obtain their consent before using or disclosing their data. You must also comply with the relevant laws and regulations regarding data protection and security in your country or region.

By using Kabupy, you agree to follow these precautions and assume full responsibility for your actions. Kabupy does not guarantee the accuracy, completeness, or timeliness of the scraped data, nor does it endorse or support any opinions or recommendations derived from the data. Kabupy is not affiliated with or endorsed by any of the target websites.
