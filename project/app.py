from flask import Flask, render_template, url_for, request, redirect
import os
import mysql.connector
from dbConfig import DBCONFIG

app=Flask(__name__)

#configure mysql
db=mysql.connector.connect(**DBCONFIG)
cursor = db.cursor(dictionary=True)

#shortcut for interacting with db
def executeQuery(query, params=None):
    cursor.execute(query, params)
    db.commit()

def fetchTeams():
    cursor.execute('select * from teams')
    teams=cursor.fetchall()
    print(teams)

    return teams

def fetchPositions():
    cursor.execute('select * from positions')
    positions=cursor.fetchall()

    return positions

#getting all data from db
def fetchData():
    cursor.execute('select * from playerInfo')
    playerInfo=cursor.fetchall()

    cursor.execute('select * from playerWages')
    playerWages=cursor.fetchall()

    cursor.execute('select * from playerStats')
    playerStats=cursor.fetchall()

    combinedData = []

    for player in playerInfo:
        teamId = player['teamId']
        shirtId = player['shirtId']
        
        wage = next((w for w in playerWages if w['teamId'] == teamId and w['shirtId'] == shirtId), None)
        stat = next((s for s in playerStats if s['teamId'] == teamId and s['shirtId'] == shirtId), None)

        combinedEntry = {
            'teamId': teamId,
            'shirtId': shirtId,
            'name': player['name'],
            'nation': player['nation'],
            'mainPos': player['mainPos'],
            'priPos': player['priPos'],
            'age': player['age'],
            'annual': wage['annual'] if wage else None,
            'transfer': wage['transfer'] if wage else None,
            'joined': wage['joined'] if wage else None,
        }
        
        print(combinedEntry)
        print('\n')

        combinedData.append(combinedEntry)

    return combinedData


@app.route('/compare')
def compare():
    #make a dictionary of parameters for each id in the array, such that it returns:
    #{'firstPlayerTeamId': request.args.get('firstPlayerTeamId'), etc...}
    params = {id: request.args.get(id) for id in ['firstPlayerTeamId', 'firstPlayerShirtId', 'secondPlayerTeamId', 'secondPlayerShirtId']}

    try:
        #combine three data tables, based on teamId and shirtId
        query = """
        SELECT 
            pi.teamId, pi.shirtId, pi.name, pi.nation, pi.mainPos, pi.priPos, pi.age,
            pw.annual, pw.transfer, pw.joined, ps.apps, ps.fullGames, ps.goals, ps.assists,
            ps.fouls, ps.yellow, ps.red
        FROM playerInfo pi
        LEFT JOIN playerWages pw ON pi.teamId = pw.teamId AND pi.shirtId = pw.shirtId
        LEFT JOIN playerStats ps ON pi.teamId = ps.teamId AND pi.shirtId = ps.shirtId
        WHERE (pi.teamId = %s AND pi.shirtId = %s) OR (pi.teamId = %s AND pi.shirtId = %s)
        """
        cursor.execute(query, (params['firstPlayerTeamId'], params['firstPlayerShirtId'], params['secondPlayerTeamId'], params['secondPlayerShirtId']))
        #get an array, players of two dictionaries, each with the information of the two players youre comparing
        players = cursor.fetchall()
        print(players[0])
        print(players[1])
        if not players:
            return render_template('comparePlayers.html', error="One or both players not found.")

        #NEED TO FIX THIS
        playerData = [{'info': player, 'wage': player, 'stat': player} for player in players]

        comparisons = {
            'ageIndex': (playerData[0]['info']['age'], playerData[1]['info']['age'], lambda x, y: x > y),
            'annualIndex': (playerData[0]['wage']['annual'], playerData[1]['wage']['annual'], lambda x, y: x > y),
            'transferIndex': (playerData[0]['wage']['transfer'], playerData[1]['wage']['transfer'], lambda x, y: x > y),
            'appsIndex': (playerData[0]['stat']['apps'], playerData[1]['stat']['apps'], lambda x, y: x > y),
            'fullGamesIndex': (playerData[0]['stat']['fullGames'], playerData[1]['stat']['fullGames'], lambda x, y: x > y),
            'goalsIndex': (playerData[0]['stat']['goals'], playerData[1]['stat']['goals'], lambda x, y: x > y),
            'assistsIndex': (playerData[0]['stat']['assists'], playerData[1]['stat']['assists'], lambda x, y: x > y),
            'foulsIndex': (playerData[0]['stat']['fouls'], playerData[1]['stat']['fouls'], lambda x, y: x < y),  # Less fouls is better
            'yellowIndex': (playerData[0]['stat']['yellow'], playerData[1]['stat']['yellow'], lambda x, y: x < y),  # Less yellow cards is better
            'redIndex': (playerData[0]['stat']['red'], playerData[1]['stat']['red'], lambda x, y: x < y)  # Less red cards is better
        }
        #dictionary comprehension: for loop for name and comp in each item of the comparisons dictionary
        #name is for example, 'ageIndex'
        #comp is for example, (age of first player, age of second player, the comparison to be made), so (32,25,x>y?)
        #lets iterate over the comparisons, 'ageIndex','anualIndex', and make a new dictionary
        #comparisonResults, which has { 'ageIndex': 1 , 'annualIndex': 0 }
        comparisonResults = {name: 0 if comp[2](comp[0], comp[1]) else 1 for name, comp in comparisons.items()}

        #by returning **comparisonResults in Python, we unpack the dictionary into keyword arguments, for example, it goes from:
        #{ 'ageIndex': 1 , 'annualIndex': 0 } into arguments, 'ageIndex= 1] , 'annualIndex= 0'
        #therefore, the return call really looks like this:
        #render_template('comparePlayers.html', players=playerData, ageIndex=1, annualIndex=0, etc...)
        return render_template('comparePlayers.html', players=playerData, **comparisonResults)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        error_message = str(err)
        return render_template('comparePlayers.html', error=error_message)

@app.route('/choosePlayers', methods=['POST', 'GET'])
def choosePlayers():

    totalData=fetchData()
    return render_template('showPlayers.html', data=totalData)

@app.route('/addPlayer', methods=['POST', 'GET'])
def addPlayer():
    if request.method == 'POST':
        playerId = request.form['playerId']
        name = request.form['name']
        teamId = request.form['teamId']
        nation = request.form['nation']
        fieldPos = request.form['fieldPos']
        age = request.form['age']

        #query
        query = 'insert into players (playerId, name, teamId, nation, fieldPos, age) values (%s, %s, %s, %s, %s, %s)'
        params = (playerId, name, teamId, nation, fieldPos, age)
        executeQuery(query, params)

        return redirect('/')
    else:
        return render_template('addPlayers.html')

@app.route('/addWage', methods=['POST', 'GET'])
def addWage():
    if request.method == 'POST':
        playerId = request.form['playerId']
        annual = request.form['annual']
        transfer = request.form['transfer']
        joined = request.form['joined']

        #query
        query = 'insert into wages (playerId, annual, transfer, joined) values (%s, %s, %s, %s)'
        params = (playerId, annual, transfer, joined)
        executeQuery(query, params)

        return redirect('/')
    else:
        return render_template('addPlayers.html')

@app.route('/')
def index():
    totalData=fetchData()
    return render_template('index.html', data=totalData)




if __name__ == '__main__':
    app.run(debug=True)