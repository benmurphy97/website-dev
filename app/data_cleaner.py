import pandas as pd
import datetime
import re


def clean_matches(df):

    df['match_date_dt'] = pd.to_datetime(df['match_date'])
    df['match_date_str'] = df['match_date_dt'].dt.strftime("%Y-%m-%d")

    df['home_score'] = df['match_result'].apply(lambda x: re.findall(r'[\d]+', x)[0]).astype(int)
    df['away_score'] = df['match_result'].apply(lambda x: re.findall(r'[\d]+', x)[1]).astype(int)

    def match_outcome(h,a):
        if h > a: # home win
            if (h - a) > 7:
                return 2
            else:
                return 1 # away team gets bonus pt
            
        elif h < a: # away win
            if (a - h) > 7:
                return -2
            else:
                return -1 # home team gets bonus pt
        else:
            return 0
    
    df['long_outcome'] = df.apply(lambda x: match_outcome(x.home_score, x.away_score), axis=1)

    df.loc[df['match_date_dt'] >= datetime.datetime.today(), 'home_score'] = 0
    df.loc[df['match_date_dt'] >= datetime.datetime.today(), 'away_score'] = 0

    df['home_n_conversions'] = df['home_n_conversions'] + df['home_n_pen_tries']
    df['away_n_conversions'] = df['away_n_conversions'] + df['away_n_pen_tries']

    cols_to_write = ['match_date_str', 'season', 'league', 'home_team', 'away_team', 'link',
                     
                     'match_result', 'home_score', 'away_score', 'long_outcome',

                     'home_n_tries', 'away_n_tries',
                     'home_n_conversions', 'away_n_conversions',
                     'home_n_pen_kicks', 'away_n_pen_kicks',
                     'home_n_pen_tries', 'away_n_pen_tries'
                     ]
    

    df.fillna(0, inplace=True)

    print(df[cols_to_write].tail())

    return df[cols_to_write]

