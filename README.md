# SI507_Final
This is a final project for UMSI 507.

The goal of the project is to create a complex database with multiple tables and joins therein, then to create an
application that will use that database to display data requested by a user. Finally, the application should be 
tested thoroughly with unit tests.

DESCRIPTION OF DATA SOURCES:

The data used in this project is entirely from www.boardgamegeek.com and many of its subsidiary web pages. I used Selenium and BeautifulSoup to crawl along hundreds of webpages to retrieve the following board game information:

Title
Publication year
Designer(s)
Publisher
Rating
Number of Voters for the Rating
Weight (AKA complexity)
Number of players
Playtime
Mechanics in the gameplay

BRIEF NOTE ON CODE STRUCTURE:

The data used in this project is saved in a .json file for easy access. Every webpage is also cached in a seperate .json file. Inside the code, the data is typically handled as a list or NumPy array.

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

3. Run 'app_main.py'

       This will start up the local server. You can now visit localhost:5000 on your browser and access the application.
       
4. To interact with the application, simply follow the instructions on the web page. For example, to begin the interaction, select a radio button that will determine whether you want to browse board games by the Title, Deisgner, or Publishers. 
