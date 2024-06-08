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
    firstPlayerTeamId = request.args.get('firstPlayerTeamId')
    firstPlayerShirtId = request.args.get('firstPlayerShirtId')
    secondPlayerTeamId = request.args.get('secondPlayerTeamId')
    secondPlayerShirtId = request.args.get('secondPlayerShirtId')
    try:
        query=f"select * from players where teamId = {firstPlayerTeamId} and shirtId = {firstPlayerShirtId}"
        cursor.execute(query)
        firstPlayerData = cursor.fetchone()

        query=f"select * from players where teamId = {secondPlayerTeamId} and shirtId = {secondPlayerShirtId}"
        cursor.execute(query)
        secondPlayerData = cursor.fetchone()

        if firstPlayerData and secondPlayerData:
            totalData = [firstPlayerData, secondPlayerData]

        else:
            print(f"error")

        return render_template('comparePlayers.html', data=totalData)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    return render_template('comparePlayers.html')  # Handle the case where an error occurs

@app.route('/choosePlayers', methods=['POST', 'GET'])
def choosePlayers():
"""     if request.method == 'POST':
        firstPlayerTeamId = request.form.get('firstPlayerTeamId')
        firstPlayerShirtId = request.form.get('firstPlayerShirtId')
        secondPlayerTeamId = request.form.get('secondPlayerTeamId')
        secondPlayerShirtId = request.form.get('secondPlayerShirtId')

        if firstPlayerTeamId and firstPlayerShirtId and secondPlayerTeamId and secondPlayerShirtId:
            print(firstPlayerShirtId)
            print(firstPlayerTeamId)
            print(secondPlayerShirtId)
            print(secondPlayerTeamId)
            return redirect('/result')
 """
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