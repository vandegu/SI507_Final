# SI507_Final
This is a final project for UM's SI 507.

The goal of the project is to create a complex database with multiple tables and joins therein, then to create an
application that will use that database to display data requested by a user. Finally, the application should be 
tested thoroughly with unit tests.

TO OPERATE THIS PROJECT:

1. Run 'db_main.py -scrape'
    
      This will crawl www.boardgamegeek's website to retrieve information on the 250 highest-ranked board games.
      The crawler will start on the listing page, then descend into each board game's page in turn. Once on the 
      board game page, the crawler uses Selenium to activates the javascript links for that game's stats page and 
      credits page. The source code of each page is passed off to BeautifulSoup for data scraping.
      
      In order for this section of the code to work, you must have the Google Chrome driver located in your PATH. 
      The chromedriver file included in this repo should do the trick.
      
      Ultimately, this code produces a game_info.json file of all of the necessary board game information. To 
      explore this file further, I recommend copying and pasting the contents of game_info.json to 
      https://jsoneditoronline.org/.
      
2. Run 'db_main.py -populate'

      This will set up the database file games.db and then populate multiple tables with the games_info.json contents.
      The database created here contains 6 tables:
      
          Game        : Primary table of all the information for each board game
          Publisher   : Contains publisher information
          Designer    : Contians designer information
          Mechanic    : Contains information on the game mechanisms present in the database
          D2G         : Junction table that contains information about which designers worked on which games
          M2G         : Junction table that contains information about which games have what mechanics
