import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys

INFO_JSON = 'game_info.json'

# def params_unique_combination(baseurl, params):
#     alphabetized_keys = sorted(params.keys())
#     res = []
#     for k in alphabetized_keys:
#         res.append("{}-{}".format(k, params[k]))
#     print(baseurl + "_".join(res))
#     return baseurl + "_" + "_".join(res)
#
# def make_request_using_cache(baseurl,params,CACHE_FNAME='cache.json'):
#     # Note, that the params passed to this function must be in dictionary form.
#     try:
#         cache_file = open(CACHE_FNAME,'r')
#         cache_contents = cache_file.read()
#         CACHE_DICTION = json.loads(cache_contents)
#         cache_file.close()
#     except:
#         CACHE_DICTION =  {}
#
#     # actually make the request:
#     unique_ident = params_unique_combination(baseurl, params)
#
#     if unique_ident in CACHE_DICTION:
#         print("\nGetting cached data...\n")
#
#         return CACHE_DICTION[unique_ident]
#
#     else:
#         # go get more new data:
#         print("\nFetching new data from API...\n")
#         resp = requests.get(baseurl,params)
#         #print(resp.text,'\n\n\n')
#         CACHE_DICTION[unique_ident] = json.loads(resp.text)
#         dumped_json_cache = json.dumps(CACHE_DICTION)
#         with open (CACHE_FNAME,'w') as fw: # when the file opens for writing, it clears current data.
#             fw.write(dumped_json_cache) # I believe this method clobbers by default.
#
#         return CACHE_DICTION[unique_ident]
#
# baseurl = 'https://www.boardgamegeek.com/xmlapi2/thing?'
# params = {'type':"boardgame",'id':"278"}
# resp = requests.get(baseurl,params)
# print(resp.url)
# with open('test_resp.json','w') as fw:
#     fw.write(resp.text)


# def html_request_using_cache(url, header=None, CACHE_FNAME='cache.json'):
#     unique_ident = url
#
#     try:
#         cache_file = open(CACHE_FNAME,'r')
#         cache_contents = cache_file.read()
#         CACHE_DICTION = json.loads(cache_contents)
#         cache_file.close()
#     except:
#         CACHE_DICTION = {}
#
#     ## first, look in the cache to see if we already have this data
#     if unique_ident in CACHE_DICTION:
#         #print("Getting cached data for {}...".format(unique_ident))
#         return CACHE_DICTION[unique_ident]
#
#     ## if not, fetch the data afresh, add it to the cache,
#     ## then write the cache to file
#     else:
#         #print("Making a request for new data from {}...".format(unique_ident))
#         # Make the request and cache the new data
#         resp = requests.get(url, headers=header)
#         CACHE_DICTION[unique_ident] = resp.text
#         dumped_json_cache = json.dumps(CACHE_DICTION)
#         fw = open(CACHE_FNAME,"w")
#         fw.write(dumped_json_cache)
#         fw.close() # Close the open file
#         return CACHE_DICTION[unique_ident]

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



class Boardgame(object):
    def __init__(self,title,primPublisher,minPlaytime,maxPlaytime,minPlayers,maxPlayers,
            weight,rating,numVotesRating,rank,pubYear,designer,mechanisms):
        self.title = title
        self.rank = rank
        self.primPublisher = primPublisher
        self.minPlaytime = minPlaytime
        self.maxPlaytime = maxPlaytime
        self.minPlayers = minPlayers
        self.maxPlayers = maxPlayers
        self.weight = weight
        self.rating = rating
        self.numVotesRating = numVotesRating
        self.rank = rank
        self.pubYear = pubYear
        self.designer = designer
        self.mechanisms = mechanisms

    def __str__(self,):
        return('{} {}, published by {}, is ranked {}'.format(self.title,self.pubYear,self.primPublisher,self.rank))



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































if __name__=='__main__':

    if len(sys.argv) <= 1:
        print('No action specified. Try again.')
        exit()

    else:
        # Scrape for data:
        if sys.argv[1] == '-scrape':
            games = crawl_top_games(num=250)
