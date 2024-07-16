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

def fetchPositions():
    cursor.execute('select * from positions')
    positions=cursor.fetchall()

    return positions
def fetchGk(teamId, shirtId):
    query = """
        SELECT 
            goalsAgainst,
            shotsOnTargetConceeded,
            savePer,
            cleanSheets,
            launchCompPer,
            goalsAgainstExpected,
            goalsAgainstExpectedPer,
            crossesStoppedPer,
            sweeps,
            penaltiesSavedPer,
            errors
        FROM gkStats
        WHERE teamId = %s AND shirtId = %s
    """
    cursor.execute(query, (teamId, shirtId))
    stats = cursor.fetchall()
    return stats

def fetchDf(teamId, shirtId):
    query = """
        SELECT 
            onGoalsAgainst,
            tackles,
            tacklesWon,
            dribblesStoppedPer,
            blocks,
            interceptions,
            clearances,
            errors,
            carries,
            aerialDuelsWon
        FROM dfStats
        WHERE teamId = %s AND shirtId = %s
    """
    cursor.execute(query, (teamId, shirtId))
    stats = cursor.fetchall()
    return stats

def fetchMf(teamId, shirtId): 
    query = """
        SELECT 
            xG,
            xA,
            proCarries,
            proPasses,
            shotsOnTargetPer,
            passesAttempted,
            passesCompleted,
            passesToShot,
            crosses,
            shotCreatingActions,
            dribblesStoppedPer,
            blocks,
            interceptions,
            touches,
            takeOnsAtt,
            takeOnsSucc,
            dispossessed,
            aerialDuelsWon
        FROM mfStats
        WHERE teamId = %s AND shirtId = %s
        """ 
    cursor.execute(query, (teamId,shirtId))
    stats = cursor.fetchall()
    return stats

def fetchFw(teamId, shirtId): 
    query = """
        SELECT 
            pkScored,
            pkAttempt,
            xG,
            npxG,
            xA,
            proCarries,
            shotsOnTargetPer,
            goalsPerShot,
            passesToShot,
            crossesIntoArea,
            shotCreatingActions,
            succTakeOn,
            foulsWon,
            goalCreatingActions,
            miscontrols,
            dispossessed,
            offsides,
            aerialDuelsWon
        FROM fwStats
        WHERE teamId = %s AND shirtId = %s
    """

    cursor.execute(query, (teamId,shirtId))
    stats = cursor.fetchall()
    return stats

@app.route('/compare')
def compare():
    positionStats = []
    pos1 = []
    pos2 = []
    def safe_int(val, default=0):
        return val if val is not None else default

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

        if not players:
            return render_template('comparePlayers.html', error="One or both players not found.")

        if players[0]['mainPos'] == 1:
            pos1 = fetchGk(params['firstPlayerTeamId'], params['firstPlayerShirtId'])
        elif players[0]['mainPos'] == 2:
            pos1 = fetchDf(params['firstPlayerTeamId'], params['firstPlayerShirtId'])
        elif players[0]['mainPos'] == 3:               
            pos1 = fetchMf(params['firstPlayerTeamId'], params['firstPlayerShirtId'])
        elif players[0]['mainPos'] == 4:
            pos1 = fetchFw(params['firstPlayerTeamId'], params['firstPlayerShirtId'])

        if players[1]['mainPos'] == 1:
            pos2 = fetchGk(params['secondPlayerTeamId'], params['secondPlayerShirtId'])
        elif players[1]['mainPos'] == 2:
            pos2 = fetchDf(params['secondPlayerTeamId'], params['secondPlayerShirtId'])
        elif players[1]['mainPos'] == 3:
            pos2 = fetchMf(params['secondPlayerTeamId'], params['secondPlayerShirtId'])
        elif players[1]['mainPos'] == 4:
            pos2 = fetchFw(params['secondPlayerTeamId'], params['secondPlayerShirtId'])

        comparisons = {
            'ageIndex': (safe_int(players[0]['age']), safe_int(players[1]['age']), lambda x, y: x > y),
            'annualIndex': (safe_int(players[0]['annual']), safe_int(players[1]['annual']), lambda x, y: x > y),
            'transferIndex': (safe_int(players[0]['transfer']), safe_int(players[1]['transfer']), lambda x, y: x > y),
            'appsIndex': (safe_int(players[0]['apps']), safe_int(players[1]['apps']), lambda x, y: x > y),
            'fullGamesIndex': (safe_int(players[0]['fullGames']), safe_int(players[1]['fullGames']), lambda x, y: x > y),
            'goalsIndex': (safe_int(players[0]['goals']), safe_int(players[1]['goals']), lambda x, y: x > y),
            'assistsIndex': (safe_int(players[0]['assists']), safe_int(players[1]['assists']), lambda x, y: x > y),
            'foulsIndex': (safe_int(players[0]['fouls']), safe_int(players[1]['fouls']), lambda x, y: x < y),
            'yellowIndex': (safe_int(players[0]['yellow']), safe_int(players[1]['yellow']), lambda x, y: x < y),
            'redIndex': (safe_int(players[0]['red']), safe_int(players[1]['red']), lambda x, y: x < y)
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
        #render_template('comparePlayers.html', players=players, ageIndex=1, annualIndex=0, etc...)
        return render_template('comparePlayers.html', players=players, **comparisonResults, pos1 = pos1, pos2 = pos2)

    except mysql.connector.Error as err:
        print("yooo")
        print(f"Error: {err}")
        error_message = str(err)
        return render_template('comparePlayers.html', error=error_message, players=[])


#start   choosePlayers.html or "Choose Two Players"
@app.route('/choosePlayers', methods=['POST', 'GET'])
def choosePlayers():

    totalData=fetchData()
    teams=fetchTeams()
    return render_template('showPlayers.html', data=totalData, teams=teams)

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
        
        #print(combinedEntry)
        #print('\n')

        combinedData.append(combinedEntry)

    return combinedData

def fetchTeams():
    cursor.execute('select * from teams')
    teams=cursor.fetchall()
    return teams

#end   choosePlayers.html or "Choose Two Players"







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
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)