# GetaJob
A web app made using dash dashboard to get jobs scraped from multiple websites and to track the number of jobs applied, pending and rejected

## Problem
Everymorning need to open up multiple websites to apply for jobs. Moreover, it is hard for me to remember which jobs I have applied to.

## Solution
Build a dashboard application that could display jobs from various websites and keep track on the jobs status

## Parts
These project consist of three parts: database, scraper and dashboard

### Database
SQLite was used to construct the database for this project, as it is native for Python (does not require any package installation). The ER diagram of the database can be seen from this link: https://github.com/nyoewono/GetaJob/blob/main/database/er_diag.png.

### Scraper
Currently, the jobs were scraped from Indeed and Seek using Selenium and beautifulSoup. Selenium was used to iterate over every page and read of the job cards. BeautifulSoup was used to open the job link and scrape the job details. The job details was not recorded in the database at the moment, only being read from the original link everytime the user is selecting a job. Since selenium may not be robust tools for webscraping a large data from a website, I have decided to store every available information for the job immediately to the database, just in case is the selenium abruptly had an error while scraping the site. 

### Dashboard
Dash was used to construct the dashboard application, as it offered a very good user interactivity using its callback function, which is not that hard to learn. However, designing the callback logic might be challenging.

## Progress
Currently, the application can only be launched on local devices just for demo purposes. Also, when trying to find new roles or update a role, chrome might pop up on the user's screen, as hiding the pop up may often lead to error in selenium (need further investigation).

## Future Improvement
Functionalities that I would like to add for improving this project:
- Applying machine learning model to analyse and learn the user's job preferences (which one is the user more likely to apply and which is not)
- Remove jobs that may not correlate with the role using machine learning and NLP (sometimes, website like Seek give the result using sorting mechanism; thus, not all jobs are related)
- Use NLP and machine learning again to study the requirements of a specific role (summarize it for you from multiple job posts)
- Deploy a database automatic cleaning mechanism in which if a job is not applied for almost a month, it will be discarded automatically.

## Potential Bug
- Bad internet connection will definately lead to a high chance of selenium crash
- If the selenium chromedriver's version is not the same as your chrome's version, then it will crash. Here is the link to download the chrome for selenium: https://chromedriver.chromium.org/downloads.
- Sometime, the callback might fail in dash ( I am quite new with Dash so please forgive me XD )

## Installation
These are the libraries or packages that you may need to install before using the code:
- pip install selenium
- pip install beautifulsoup4
- pip install dash==1.19.0
- pip install dash-bootstrap-components
- pip install pandas

## Run The Application
To run the application, go to the directory of where you put this code, cd to the dash folder and type "python app.py". This will automatically open up your browser and show the dashboard in the local host on where it is hosted. Or, you could type a bash script which will create a clickable icon to run the dashboard automatically on your desktop (click this link: https://github.com/nyoewono/GetaJob/blob/main/desktop_click.txt).

# Goodluck and happy job hunting :)
