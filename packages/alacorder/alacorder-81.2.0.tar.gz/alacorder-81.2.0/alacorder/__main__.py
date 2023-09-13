"""
┏┓┓ ┏┓┏┓┏┓┳┓┳┓┏┓┳┓
┣┫┃ ┣┫┃ ┃┃┣┫┃┃┣ ┣┫
┛┗┗┛┛┗┗┛┗┛┛┗┻┛┗┛┛┗
(c) 2023 Sam Robson

Alacorder collects case detail PDFs from Alacourt.com and processes them into
data tables suitable for research purposes.

Dependencies: Python 3.9+, Google Chrome, brotli 1.0.9+, polars 0.18.1+,
pymupdf 1.21.1+, rich 13.3.3+, selenium 4.8.3+, typer 0.9.0+,
xlsx2csv 0.8.1+, xlsxwriter 3.0.9+
"""

from .alac import app

if __name__ == "__main__":
    app()
