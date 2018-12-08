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
            ORDER BY AVG(g.Rating) DESC
        '''
    elif type == 'publisher':
        statement = '''
            SELECT p.Id,p.Name,AVG(g.Rating),AVG(g.Weight) FROM Game as g
            JOIN Publisher AS p ON g.PublisherId = p.Id
            GROUP BY p.Id
            ORDER BY AVG(g.Rating) DESC
        '''

    conn = sql.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    out = []
    for r in cur:
        out.append(r)
    conn.close()

    return np.array(out)


def create_plotly(d):

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
            title = 'test2',
            xaxis = {'title':"Rating"},
            yaxis = {'title':"Weight"}
    )

    fig = dict( data=[data], layout=layout )
    #py.plot( fig, validate=False, filename='test')
    plot_div = py.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)

    return plot_div
