import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
import warnings
warnings.filterwarnings('ignore')



def get_base_url(league, season):
    season = int(season)

    if league.lower() in ['urc', 'premiership', 'top-14', 'champions-cup']:
        if season < 2025:
            url = f"https://all.rugby/tournament/{league}-{str(season)}/fixtures-results"
        elif season == 2025:
            url = f"https://all.rugby/tournament/{league}/fixtures-results"
    else: 
        print("league not recognised")
        url = "Incorrect"

    return url



# links_df containing the end of the url for each match
# scores is a list containing the score or the time of fixture if the hasnt happened yet
def get_links_df(url):

    # text of fixtures page
    fixture_text = requests.get(url, headers={ "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
                                                AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"})
    fixture_soup = BeautifulSoup(fixture_text.text)
    li = fixture_soup.find_all("li", class_="clearfix")

    fixture_links = [] # list of links to each fixture
    scores = [] # scores of matches

    # iterate over fixture li elements, getting url and score for match
    for i in li:
        scores.append(i.text.split("\n")[3])
        fix_link = i.find("a")['href']
        fixture_links.append(fix_link)
        
    # create df with all fixture links in it
    links_df = pd.DataFrame(fixture_links,columns=['links'])

    return links_df, scores



# parse the mins of events in the match
def parse_mins(messy_mins):
    if messy_mins is np.nan:
        mins=''
        n=0
    else:
        mins = re.findall(r'[\d]+', messy_mins)
        n = len(mins)
        mins = '_'.join(mins)
    return mins, n


# parse the mins of events in the match
def parse_mins(messy_mins):
    if messy_mins is np.nan:
        mins=''
        n=0
    else:
        mins = re.findall(r'[\d]+', messy_mins)
        n = len(mins)
        mins = '_'.join(mins)
    return mins, n




def scrape_matches_from_links(links_df, scores):
    # list to store data from each fixture
    list_of_match_dataframes = []
    list_of_player_dataframes = []

    non_events = []

    count_ = 0
    # loop over links and get match data
    for link in links_df['links']:
        # print("\nhttps://all.rugby"+link)
        
        count_+=1
        if count_ % 10 == 0:
            print(count_)
            
        match_link = "https://all.rugby" + link
        # print("\n\n\n",match_link)
        match_html_text = requests.get(match_link, 
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
                            AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15" }).text

        
        # date, time, venue
        match_soup = BeautifulSoup(match_html_text)
        match_meta = match_soup.find("div", class_="txtcenter").text
        match_meta_str = match_meta.replace("\t", "").replace("\n", " ")
        # print(match_meta_str)
        
        # matches called off by covid, ignore
        if 'Coronavirus' in match_meta_str:
            non_events.append(count_)
            print("Covid postponed")
            continue
        if 'blessures' in match_meta_str:
            non_events.append(count_)
            print("Blessures postponed")
            continue
        if 'suspension' in match_meta_str:
            non_events.append(count_)
            print("Suspension match cancelled")
            continue
            
        # time of match on website, french time by default
        french_time = re.findall('\d\d:\d\d', match_meta_str)[0]

        # stadium
        stadium_start_index = re.search('Venue : ', match_meta_str).span()[1]
        stadium_end_index = re.search(' Tournament :', match_meta_str).span()[0]
        stadium = match_meta_str[stadium_start_index:stadium_end_index]

        # date
        date_start_index = re.search('Date :  ', match_meta_str).span()[1]
        date_end_index = re.search(' Kick Off :', match_meta_str).span()[0]
        match_date = match_meta_str[date_start_index:date_end_index]

        dfs = pd.read_html(match_html_text)
        # print(f"Number of dataframes: {len(dfs)}")

        # fixture, we dont know team news - just grab meta and home + away team
        if len(dfs) in [5,6,7]:
            
            # print("Fixture - no team news")

            if 'December 7' in match_meta_str or 'December 8' in match_meta_str:
                print("December 7 or 8")
                equipes = match_soup.find_all("div", class_="equipe")
                teams = [e.text for e in equipes]
                home_team = teams[0]
                away_team = teams[1]
            else:
                # print(dfs[0])
                home_team = dfs[0].columns[0]
                away_team = dfs[0].columns[2]
            # print(home_team, away_team)
            match_df = pd.DataFrame([{"Home team": home_team,
                                    "Away team": away_team,
                                    "Stadium": stadium,
                                    "Match Date": match_date,
                                    "Match Time French": french_time}])
        

        # matches that havent happened yet but we know team news
        elif len(dfs) in [8,9]:
            # print("We know team news")
            # pack weight and age
            if len(dfs)==9:
                meta_df = dfs[2]
            else:
                meta_df = dfs[1]
            home_team = meta_df.columns[0]
            away_team = meta_df.columns[2]

            cols = meta_df['VS'].tolist()
            cols.append('team')
            data = meta_df[[home_team, away_team]].T

            data['team'] = data.index
            data.columns = cols

            data_home = data.head(1)
            data_away = data.tail(1)

            data_home = data_home.add_prefix("Home ").reset_index(drop=True)
            data_away = data_away.add_prefix("Away ").reset_index(drop=True)

            match_df = pd.concat([data_home, data_away], axis=1)
            
            match_df["Stadium"] = stadium
            match_df["Match Date"] = match_date,
            match_df["Match Time French"] = french_time
            
                
        # if the match is a past result
        elif len(dfs) < 5:
            # pack weight and age
            meta_df = dfs[1]

            home_team = meta_df.columns[0]
            away_team = meta_df.columns[2]

            cols = meta_df['VS'].tolist()
            cols.append('team')
            data = meta_df[[home_team, away_team]].T

            data['team'] = data.index
            data.columns = cols

            data_home = data.head(1)
            data_away = data.tail(1)

            data_home = data_home.add_prefix("Home ").reset_index(drop=True)
            data_away = data_away.add_prefix("Away ").reset_index(drop=True)

            match_df = pd.concat([data_home, data_away], axis=1)
            # match_df['meta'] = match_meta_str
            # print(match_meta_str)

            match_df["Stadium"] = stadium
            match_df["Match Date"] = match_date,
            match_df["Match Time French"] = french_time

            # Players in match with events and substitutions 
            # dfs[0]

            match_events = dfs[0]

            # n_tries - must account for penalty tries appearing a row after the players if one is present.
            if match_events['Try'][24] == 'Replacements':
                last_index = 24
                home_pen_try_str = ''
                home_n_pen_tries = 0
                
                away_pen_try_str = ''
                away_n_pen_tries = 0
                
            else: # pen try scored
                last_index = 25
                home_pen_try_mins_messy = match_events['Try'].iloc[24]
                home_pen_try_str, home_n_pen_tries = parse_mins(home_pen_try_mins_messy)

                away_pen_try_mins_messy = match_events['Try.1'].iloc[24]
                away_pen_try_str, away_n_pen_tries = parse_mins(away_pen_try_mins_messy)

            # tries
            home_try_mins_messy = ' '.join(match_events['Try'].iloc[:last_index].dropna().values)
            home_tries_str, home_n_tries = parse_mins(home_try_mins_messy)

            away_try_mins_messy = ' '.join(match_events['Try.1'].iloc[:last_index].dropna().values)
            away_tries_str, away_n_tries = parse_mins(away_try_mins_messy)

            # n_penalties
            home_pen_kicks_mins_messy = ' '.join(match_events['Penalty'].iloc[:24].dropna().values)
            home_pen_kicks_str, home_n_pen_kicks = parse_mins(home_pen_kicks_mins_messy)

            away_pen_kicks_mins_messy = ' '.join(match_events['Penalty.1'].iloc[:24].dropna().values)
            away_pen_kicks_str, away_n_pen_kicks = parse_mins(away_pen_kicks_mins_messy)

            # n_conversions
            home_conversions_mins_messy = ' '.join(match_events['Conversion'].iloc[:24].dropna().values)
            home_conversions_str, home_n_conversions = parse_mins(home_conversions_mins_messy)

            away_conversions_mins_messy = ' '.join(match_events['Conversion.1'].iloc[:24].dropna().values)
            away_conversions_str, away_n_conversions = parse_mins(away_conversions_mins_messy)

            # yellow cards
            home_yc_mins_messy = ' '.join(match_events['YC'].iloc[:24].dropna().values)
            home_yc_str, home_n_ycs = parse_mins(home_yc_mins_messy)

            away_yc_mins_messy = ' '.join(match_events['YC.1'].iloc[:24].dropna().values)
            away_yc_str, away_n_ycs = parse_mins(away_yc_mins_messy)

            # red cards
            home_rc_mins_messy = ' '.join(match_events['RC'].iloc[:24].dropna().values)
            home_rc_str, home_n_rcs = parse_mins(home_rc_mins_messy)

            away_rc_mins_messy = ' '.join(match_events['RC.1'].iloc[:24].dropna().values)
            away_rc_str, away_n_rcs = parse_mins(away_rc_mins_messy)


            match_df['home_n_tries'] = home_n_tries
            match_df['home_n_conversions'] = home_n_conversions
            match_df['home_n_pen_kicks'] = home_n_pen_kicks
            match_df['home_n_pen_tries'] = home_n_pen_tries

            match_df['away_n_tries'] = away_n_tries
            match_df['away_n_conversions'] = away_n_conversions
            match_df['away_n_pen_kicks'] = away_n_pen_kicks
            match_df['away_n_pen_tries'] = away_n_pen_tries

            match_df['mins_of_home_tries'] = home_tries_str
            match_df['mins_of_home_conversions'] = home_conversions_str
            match_df['mins_of_home_pen_kicks'] = home_pen_kicks_str
            match_df['mins_of_home_pen_tries'] = home_pen_try_str

            match_df['mins_of_away_tries'] = away_tries_str
            match_df['mins_of_away_conversions'] = away_conversions_str
            match_df['mins_of_away_pen_kicks'] = away_pen_kicks_str
            match_df['mins_of_away_pen_tries'] = away_pen_try_str

            match_df['home_n_yellow_cards'] = home_n_ycs
            match_df['mins_of_home_yellow_cards'] = home_yc_str

            match_df['away_n_yellow_cards'] = away_n_ycs
            match_df['mins_of_away_yellow_cards'] = away_yc_str

            match_df['home_n_red_cards'] = home_n_rcs
            match_df['mins_of_home_red_cards'] = home_rc_str

            match_df['away_n_red_cards'] = away_n_rcs
            match_df['mins_of_away_red_cards'] = away_rc_str


        match_df['link'] = match_link
        list_of_match_dataframes.append(match_df)
    
    
    matches_df = pd.concat(list_of_match_dataframes)

    def format_cols(col_name):
        col_name = re.sub(r'[()]', '', col_name)
        col_name = col_name.lower()
        col_name = col_name.replace(' ', '_')
        return col_name
    
    matches_df.columns = [format_cols(c) for c in matches_df.columns]
    matches_df.columns

    scores = [i for i in scores if i != 'cancelled']
    matches_df['match_result'] = scores

    return matches_df
