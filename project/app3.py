@app.route('/compare')
def compare():
    firstPlayerTeamId = request.args.get('firstPlayerTeamId')
    firstPlayerShirtId = request.args.get('firstPlayerShirtId')
    secondPlayerTeamId = request.args.get('secondPlayerTeamId')
    secondPlayerShirtId = request.args.get('secondPlayerShirtId')
    
    try:
        # Retrieve basic player info
        def getPlayerInfo(teamId, shirtId):
            query = "SELECT * FROM playerInfo WHERE teamId = %s AND shirtId = %s"
            cursor.execute(query, (teamId, shirtId))
            return cursor.fetchone()
        
        def getPlayerWage(teamId, shirtId):
            query = "SELECT * FROM playerWages WHERE teamId = %s AND shirtId = %s"
            cursor.execute(query, (teamId, shirtId))
            return cursor.fetchone()

        def getPlayerStats(teamId, shirtId):
            query = "SELECT * FROM playerStats WHERE teamId = %s AND shirtId = %s"
            cursor.execute(query, (teamId, shirtId))
            return cursor.fetchone()

        def getPositionStats(mainPos, teamId, shirtId):
            positions = {
                1: 'gkStats',
                2: 'dfStats',
                3: 'mfStats',
                4: 'fwStats'
            }
            posTable = positions.get(mainPos)
            if posTable:
                query = f"SELECT * FROM {posTable} WHERE teamId = %s AND shirtId = %s"
                cursor.execute(query, (teamId, shirtId))
                return cursor.fetchone()
            return None

        firstPlayerInfo = getPlayerInfo(firstPlayerTeamId, firstPlayerShirtId)
        secondPlayerInfo = getPlayerInfo(secondPlayerTeamId, secondPlayerShirtId)

        firstPlayerWage = getPlayerWage(firstPlayerTeamId, firstPlayerShirtId)
        secondPlayerWage = getPlayerWage(secondPlayerTeamId, secondPlayerShirtId)

        firstPlayerStat = getPlayerStats(firstPlayerTeamId, firstPlayerShirtId)
        secondPlayerStat = getPlayerStats(secondPlayerTeamId, secondPlayerShirtId)

        firstPlayerPos = getPositionStats(firstPlayerInfo['mainPos'], firstPlayerTeamId, firstPlayerShirtId)
        secondPlayerPos = getPositionStats(secondPlayerInfo['mainPos'], secondPlayerTeamId, secondPlayerShirtId)

        if not all([firstPlayerInfo, secondPlayerInfo]):
            error_message = "One or both players not found."
            return render_template('comparePlayers.html', error=error_message)

        totalData = {
            'firstPlayer': {
                'info': firstPlayerInfo,
                'wage': firstPlayerWage,
                'stats': firstPlayerStat,
                'position': firstPlayerPos
            },
            'secondPlayer': {
                'info': secondPlayerInfo,
                'wage': secondPlayerWage,
                'stats': secondPlayerStat,
                'position': secondPlayerPos
            }
        }
        print(totalData)

        return render_template('comparePlayers.html', data=totalData)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        error_message = str(err)
        return render_template('comparePlayers.html', error=error_message)

    return render_template('comparePlayers.html', error="Unexpected error occurred")