# kaggle-notebook-scraper
WIP. Scraping Kaggle Notebooks to figure out what tools people are using to solve problems.

`meta.py` gets info about all existing kernels on the COVID-19 Challenge in < 1 minute and write a file called `covid-kernels.csv`

`notebook_scraper.py` scrapes all kernels from `covid-kernels.csv` over a longer period of time ~1h (selenium >:(( !!!) for views, length, and modules imported. 

download and open `modules.html` to see what tools people are using.