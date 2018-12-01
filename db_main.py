import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import sqlite3
import os

# Define the .json to hold all of the scraped information.
INFO_JSON = 'game_info.json'
# Define the name of the games database.
DB_NAME = 'games.db'

def html_request_using_cache(url, header=None, CACHE_FNAME='cache.json'):
    '''
        This function uses Selenium to dynamically load a webpage with Chrome in
        order to initialize all javascript elements. Then, it will save it in the cache.
        If the item required is already in the cache, it is returned from the cache
        directly.
    '''
    unique_ident = url

    try:
        cache_file = open(CACHE_FNAME,'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        #print("Getting cached data for {}...".format(unique_ident))
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        #print("Making a request for new data from {}...".format(unique_ident))
        # Make the request and cache the new data
        driver = webdriver.Chrome()
        driver.implicitly_wait(30)
        driver.get(url)
        html = driver.page_source
        driver.quit()
        CACHE_DICTION[unique_ident] = html
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]



def crawl_top_games(num=5):
    '''
        This function crawls the top-ranked list on boardgamegeek.com and scrapes information
        from each game.
    '''

    # Establish the baseurl:
    burl = 'https://boardgamegeek.com'

    # Establish starting page url extension:
    ext = '/search/boardgame?sort=rank&q=+&B1=Go'

    # Start while loop through the highest ranked games:
    collection_rank = 0

    # Establish empty dict for mechanisms, designers, and publishers:
    tot_publishers = []
    tot_designers = []
    tot_mechanics = {}

    while collection_rank <= num:

        # Initialize list of Boardgame class instances:
        games = []

        # Get html string
        html = html_request_using_cache(burl+ext)
        html_soup = BeautifulSoup(html, 'html.parser')

        # Find the primary table:
        collection_table = html_soup.find(class_='collection_table')
        # Find the list of games:
        rows = collection_table.find_all(id='row_')
        # Loop through each game in the list of games:
        for row in rows:
            # Update the collection rank, use int() to make comparable and get rid of spaces.
            collection_rank = int(row.find(class_='collection_rank').text)
            # End for loop if rank exceeds num.
            if collection_rank > num:
                break
            # Else, pass url to next function to read game page.
            else:
                game_ext_container = row.find(style='z-index:1000;')
                game_ext = game_ext_container.find('a').get('href')
                game_name = game_ext_container.find('a').text
                print('scraping rank {}: {}'.format(collection_rank,game_name))
                a_game,tp,td,tm = create_game_instance(burl,game_ext,tot_publishers,tot_designers,tot_mechanics)
                games.append(a_game)

        # Grab the url for the next page:
        ext = html_soup.find('a',attrs={'target':"_self",'title':"next page"}).get('href')

    game_info = dict(
        games = games,
        tp = tp,
        td = td,
        tm = tm
    )

    # Save game info dictionary as json.
    with open(INFO_JSON,'w') as fw:
        fw.write(json.dumps(game_info))

    return game_info



def create_game_instance(burl,game_ext,tp,td,tm):
    '''
        This function creates a Boardgame instance of a game by scraping its page. This function
        also keeps track of all unique publishers, designers, and mechanics (as well as
        recording the text for each mechanic).
    '''

    html = html_request_using_cache(burl+game_ext+'/stats')
    js_soup = BeautifulSoup(html, 'html.parser')

    # Title
    title = js_soup.find('a',attrs={'ui-sref':"geekitem.overview",'ng-href':game_ext}).text
    title = title.strip() # Removes whitespace before and after the alphanumeric characters.
    # print(title)

    # Year
    # QQ Do you want to get rid of the () on the year?
    year = js_soup.find('span',attrs={'class':"game-year"}).text
    year = year.strip()
    # print(year)

    # Rating
    rating = js_soup.find('a',attrs={'ui-sref':"geekitem.ratings({comment:1})"}).text
    rating = rating.strip()
    # print(rating)

    # Num Votes Rating
    numVotesRating = js_soup.find('a',attrs={'ui-sref':"geekitem.ratings({rated:1})"}).text
    numVotesRating = numVotesRating.strip()
    # print(numVotesRating)

    # primPublisher # FOLLOWLINK
    primPublisher_container = js_soup.find('popup-list',attrs={'items':"geekitemctrl.geekitem.data.item.links.boardgamepublisher"})
    primPublisher_container = primPublisher_container.find('span',attrs={'ng-repeat':"item in items|limitTo: listshowcount"})
    primPublisher_href = primPublisher_container.find('a').get('href')
    primPublisher = primPublisher_container.find('a').text
    primPublisher = primPublisher.strip()
    if primPublisher not in tp:
        tp.append(primPublisher)
    # print(primPublisher)

    # Playtime:
    playtime_container = js_soup.find('span',attrs={'min':"::geekitemctrl.geekitem.data.item.minplaytime",
        'max':"::geekitemctrl.geekitem.data.item.maxplaytime"})
    playtime_container = playtime_container.find_all('span')
    time = ''
    for i in playtime_container:
        try:
            time += (' '+i.text.strip().replace('–',''))
        except:
            continue
    timesplit = time.split()
    time_int = [int(i) for i in timesplit]
    minPlaytime = min(time_int)
    maxPlaytime =  max(time_int)
    # print(minPlaytime,maxPlaytime)

    # Players:
    players_container = js_soup.find('span',attrs={'max':"::geekitemctrl.geekitem.data.item.maxplayers",
        'min':"::geekitemctrl.geekitem.data.item.minplayers"})
    players_container = players_container.find_all('span')
    players = ''
    for i in players_container:
        try:
            players += (' '+i.text.strip().replace('–',''))
        except:
            continue
    playersplit = players.split()
    player_int = [int(i) for i in playersplit]
    minPlayers = min(player_int)
    maxPlayers =  max(player_int)
    # print(minPlayers,maxPlayers)

    # Weight
    weight = js_soup.find('a',attrs={'ng-if':"::geekitemctrl.geekitem.data.item.stats.avgweight > 0"})
    weight = weight.find('span',attrs={'class':"c-is-positive"}).text
    weight = weight.strip()
    # print(weight)

    # Rank
    rank = js_soup.find('a',attrs={'class':'rank-value'}).text
    rank = rank.strip()
    # print(rank)

    # Find credits page and load it.
    html = html_request_using_cache(burl+game_ext+'/credits')
    js_soup = BeautifulSoup(html, 'html.parser')

    # Designers:
    designers = []
    container = js_soup.find_all('li',attrs={'class':"outline-item",'ng-class':"{'is-highlighted': info.keyname==creditsctrl.hash}"})
    for entry in container:
        p = entry.find_all('span',attrs={'ng-attr-id':"{{'fullcredits-' + info.keyname}}",'id':"fullcredits-boardgamedesigner"})
        for i in p:
            if i:
                designer_containers = entry.find_all('a')
                for designer in designer_containers[1:]: # Avoid the first empty cell.
                    designers.append(designer.text)
                    if designer.text not in td:
                        td.append(designer.text)
    # print(designers)

    # Mechanisms
    mechanisms = []
    container = js_soup.find_all('li',attrs={'class':"outline-item",'ng-class':"{'is-highlighted': info.keyname==creditsctrl.hash}"})
    for entry in container:
        p = entry.find_all('span',attrs={'ng-attr-id':"{{'fullcredits-' + info.keyname}}",'id':"fullcredits-boardgamemechanic"})
        for i in p:
            if i:
                mechanism_containers = entry.find_all('a')
                for mechanism in mechanism_containers[1:]: # Avoid the first empty cell.
                    mechanism_name = mechanism.text
                    mechanisms.append(mechanism.text)
                    if mechanism_name not in tm:
                        mechanism_url = mechanism.get('href')
                        # Grab the description of the mechanism:
                        html = html_request_using_cache(burl+mechanism_url)
                        mech_soup = BeautifulSoup(html, 'html.parser')
                        desc_container = mech_soup.find('div',attrs={'class':"wiki",'id':"editdesc"})
                        desc = desc_container.find('p').text
                        tm[mechanism_name] = desc
    # print(tm,mechanisms)

    # Create Boardgame instance:
    # inst = Boardgame(title,primPublisher,minPlaytime,maxPlaytime,minPlayers,maxPlayers,
    #     weight,rating,numVotesRating,rank,year,designers,mechanisms)

    inst = dict(
        title=title,
        primPublisher=primPublisher,
        minPlaytime=minPlaytime,
        maxPlaytime=maxPlaytime,
        minPlayers=minPlayers,
        maxPlayers=maxPlayers,
        weight=weight,
        rating=rating,
        numVotesRating=numVotesRating,
        rank=rank,
        pubYear=year,
        designers=designers,
        mechanisms=mechanisms
    )

    return inst,tp,td,tm



def initialize_db():
    '''
        Creates a database and sets up tables for storing game data, publisher data, designer
        data, mechanics data, and junction tables for the many-to-many links between designer
        and game as well as mechanics and game.
    '''

    print('\nRemoving old {}...\n'.format(DB_NAME))
    os.remove(DB_NAME)

    print('\nCreating new {}...\n'.format(DB_NAME))
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Create Mechanic table:
    statement =  '''
        CREATE TABLE 'Mechanic' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Name' TEXT NOT NULL,
        'Description' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    # Create M2G junction table for the many-to-many between Mechanic and Game:
    statement =  '''
        CREATE TABLE 'M2G' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'MechanicId' INTEGER NOT NULL,
        'GameId' INTEGER NOT NULL
        );
    '''
    cur.execute(statement)

    # Create the Designer table.
    statement =  '''
        CREATE TABLE 'Designer' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Name' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    # Create the D2G junction table for the many-to-many between Designer and Game.
    statement =  '''
        CREATE TABLE 'D2G' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'DesignerId' INTEGER NOT NULL,
        'GameId' INTEGER NOT NULL
        );
    '''
    cur.execute(statement)

    # Create the Publisher table.
    statement =  '''
        CREATE TABLE 'Publisher' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Name' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    # Create the Game table.
    statement =  '''
        CREATE TABLE 'Game' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Title' TEXT NOT NULL,
        'PubYear' TEXT NOT NULL,
        'Publisher' INTEGER NOT NULL,
        'Rank' INTEGER NOT NULL,
        'Ratinhg' REAL NOT NULL,
        'NumVotesRating' INTEGER NOT NULL,
        'Weight' REAL NOT NULL,
        'MinPlaytime' INTEGER,
        'MaxPlaytime' INTEGER,
        'MinPlayers' INTEGER,
        'MaxPlayers' INTEGER
        );
    '''
    cur.execute(statement)

    conn.commit()
    print('\nSuccesfully created {}.\n'.format(DB_NAME))

def populate_db(info_file):
    '''
        Populates the games DB with data from the given input file (ideally, the input of this
        function is the writeout file of the 'crawl_top_games' function).
    '''

    
































if __name__=='__main__':

    if len(sys.argv) <= 1:
        print('''
            No action specified. Try again.

            ***Pass the following arguments alone***

            -scrape : Scrape new data from the web. This can take approx. 1 hour and requires the
                      use of a Chrome driver for Selenium to work properly. Chrome driver is provided
                      in this repo for MacOS ONLY.
            -setupDB : Initialize the database and tables.
        ''')
        exit()

    else:
        # Scrape for data:
        if sys.argv[1] == '-scrape':
            games = crawl_top_games(num=250)

        # Set up db:
        elif sys.argv[1] == '-setupDB':
            print('\nInitializing database...\n')
            initialize_db()
