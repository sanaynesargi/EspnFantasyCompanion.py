# **EspnFantasyFootBall Companion**
## A Script to Provide **New** and **Beneficial** Insights
### By: Sanay Nesargi

![Imgur Image](https://i.imgur.com/CZlzqlo.png)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

*App version (maybe) coming soon!*

EspnFantasyFootballCompanion is a python-powered script that allows you to fetch useful and relevant information from your fantasy football leagues, but more than that, it allows you to see new and more relavant statistics than the vanilla ones that ESPN gives you, enabling you to adjust your lineup and increase your success!

- These statistics are meant to help you, it's up to you how you interpret them
- **DON'T** blame the software

## Features

- Calculates many interesting statistics (Most consistent, highest average, etc.)
- Public **and** Private League Support
- Can use test data instead of real data
- Easy to use

## Technologies

Frameworks / Libraries:

- **Requests (ESPN API)** - to make API requests
- **Pandas** - to format and work with the data given
- **Seaborn and Matplotlib** - to plot the data

![Imgur Image](https://i.imgur.com/bPsry6Y.jpeg)

## Before you go
- Be sure that you update calculate_results.py with your *league_id* and *year*
- These variables are located at the top of the main() function

### Private League Users **ONLY**
- get the relevant cookies to simulate a request
- You can find information on that here: you can get more information here: https://stmorse.github.io/journal/espn-fantasy-v3.html
- The program will ask you for those cookies so **be sure to have them!**

### Public League Users **ONLY**
- Disregard the cookies input, as yours is a public league, you will be fine
- You can comment out or delete that code (before the main()), your choice
- Just be sure to put in your *league_id* and *year*

## Installation

- Clone the Repository
- Install the Dependencies
- Add your cookies (private leagues)
- for dummy data uncomment lines in calculate_results.py
- create a custom image for the program to use for your league (1728 × 2304) and place in the **images/** directory
- Run the program and play with the statistics returned at the bottom of main()
- Have fun!

```sh
https://github.com/sanaynesargi/EspnFantasyCompanion.py.git
Create your image (1728 x 2304) image (e.g. Canva) and place it in the images dir 
(not required) but have league name on the image
cd EspnFantasyCompanion.py
(not required) python(version) -m venv env
(not required) activate the environment
pip(version) install -r requirements.txt
python(version) calculate_results.py (for private league put in cookies)
```


## License

MIT
Software is free to all, so feel free to use it as you wish

![Built with the ESPN API](http://a.espncdn.com/i/apis/attribution/espn-api-red_200.png)
