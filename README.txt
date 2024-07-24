plPlayerComparison
This site is a database of each player in the Premier League, with their personal information, game statistics and wage/transfer fee. 
You can choose two players to compare to see who is the more overpaid player and who is the better player to buy.


scripting:
python3 -m venv env
source env/bin/activate
pip install Flask
pip install mysql-connector-python

to run: 
*when you are in FlaskProject2*
source ./env/bin/activate
cd project 
python3 app.py

to push:
git add .
git commit -m ''
git push -u -f origin main

########
for Transfer Value I use transfermarkt
for Data and Wage I use fbref