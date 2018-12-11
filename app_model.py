import sqlite3 as sql
import numpy as np
import plotly as py


DBNAME = 'games.db'

def get_plot_data(type):
    # Set the proper params for the query:
    if type == 'title':
        statement = '''
        SELECT Id,Title,Rating,Weight FROM Game
        '''
    elif type == 'designer':
        statement = '''
            SELECT d.Id,d.Name,AVG(g.Rating),AVG(g.Weight) FROM Designer as d
            JOIN D2G AS jxn ON jxn.DesignerId = d.Id
            JOIN Game AS g ON jxn.GameId = g.Id
            GROUP BY d.Id
            /*ORDER BY AVG(g.Rating) DESC
        '''
    elif type == 'publisher':
        statement = '''
            SELECT p.Id,p.Name,AVG(g.Rating),AVG(g.Weight) FROM Game as g
            JOIN Publisher AS p ON g.PublisherId = p.Id
            GROUP BY p.Id
            /*ORDER BY AVG(g.Rating) DESC
        '''

    conn = sql.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    out = []
    for r in cur:
        out.append(r)
    conn.close()

    return np.array(out)


def create_plotly(d,choice):

    if choice == 'title':
        plottitle = 'Weight (complexity, max 5) vs. Rating (max 10) of Top 250 Board Games'
    elif choice == 'designer':
        plottitle = 'Average Weight (complexity, max 5) vs. Average Rating (max 10) of Game Designers'
    elif choice == 'publisher':
        plottitle = 'Average Weight (complexity, max 5) vs. Average Rating (max 10) of Game Publishers'

    data = dict(
            type = 'scatter',
            x = d[:,2],
            y = d[:,3],
            text = d[:,1],
            mode = 'markers',
            marker = dict(
                size = 8,
                symbol = 'circle',
                color = "blue"
            ))

    layout = dict(
            title = plottitle,
            xaxis = {'title':"Rating"},
            yaxis = {'title':"Weight"}
    )

    fig = dict( data=[data], layout=layout )
    #py.plot( fig, validate=False, filename='test')
    plot_div = py.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)

    return plot_div

def get_detail_data(choice,name):

    conn = sql.connect(DBNAME)
    cur = conn.cursor()

    if choice == 'title':
        statement = '''
            SELECT g.Title,g.PubYear,p.Name,g.Rank,g.Rating,g.NumVotesRating,g.Weight,g.MinPlaytime,g.MaxPlaytime,g.MinPlayers,g.MaxPlayers
            FROM Game AS g JOIN Publisher AS p ON g.PublisherId=p.Id
            WHERE g.Title='{}'
        '''.format(name)
        cur.execute(statement)
        info = []
        for r in cur:
            info.append(r)

        statement = '''
            SELECT m.Name FROM Mechanic AS m
            JOIN M2G AS jxn ON jxn.MechanicId = m.Id
            JOIN Game AS g ON jxn.GameId = g.Id
            WHERE g.Title='{}'
        '''.format(name)
        cur.execute(statement)
        mechs = []
        for r in cur:
            mechs.append(r)

        return info,mechs

    elif choice == 'designer':
        statement = '''
            SELECT d.Name, COUNT(*), AVG(g.Rating), AVG(g.Weight), AVG((g.MaxPlaytime+g.MinPlaytime)/2) FROM Designer AS d
            JOIN D2G AS jxn ON jxn.DesignerId = d.Id
            JOIN Game AS g ON jxn.GameId = g.Id
            GROUP BY d.Id
            HAVING d.Name='{}'
        '''.format(name)
        cur.execute(statement)
        info = []
        for r in cur:
            info.append(r)
        mechs = []

        return info,mechs

    elif choice == 'publisher':
        statement = '''
            SELECT p.Name, COUNT(*), AVG(g.Rating), AVG(g.Weight), AVG((g.MaxPlaytime+g.MinPlaytime)/2) FROM Publisher AS p
            JOIN Game AS g ON p.Id = g.PublisherId
            GROUP BY p.Id
            HAVING p.Name='{}'
        '''.format(name)
        cur.execute(statement)
        info = []
        for r in cur:
            info.append(r)
        mechs = []

        return info,mechs
