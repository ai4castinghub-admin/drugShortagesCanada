
import time
import random
from GoogleNews import GoogleNews
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from datetime import datetime, timedelta

SHORTAGE_KEYWORDS = {
    "shortage", "out of stock", "supply issue", "unavailable",
    "backordered", "delayed", "running low", "supply disruption",
    "not available", "in limited supply", "distribution issue",
    "increased demand", "supply constraint", "hard to find"
}


def parse_google_date(date_str):
    try:
        return datetime.strptime(date_str, '%d %b %Y')
    except ValueError:
        match = re.match(r'(\d+)\s+(hour|day|week|month|year)s?\s+ago', date_str)
        if match:
            value, unit = int(match.group(1)), match.group(2)
            delta = {
                'hour': timedelta(hours=value),
                'day': timedelta(days=value),
                'week': timedelta(weeks=value),
                'month': timedelta(days=30 * value),
                'year': timedelta(days=365 * value),
            }.get(unit, timedelta(0))
            return datetime.today() - delta
       
        print('wrong datetime')
        return datetime.today()
    

def fetch_news_by_region(regions, start_year=2018, end_year=2025, max_pages=5):
    all_results = []
    
    for year in range(start_year, end_year + 1):
        start_date_str = f'01/01/{year}'
        end_date_str = f'12/31/{year}'
        print(f"\n===== Fetching for Year: {year} ({start_date_str} to {end_date_str}) =====")
        #time.sleep(random.uniform(45, 60))

        for region in regions:
            time.sleep(random.uniform(30, 90))
            #query = f"drug shortage medication shortage {region}"
            shortage_terms = ' OR '.join([f'"{kw}"' for kw in SHORTAGE_KEYWORDS])
            query = f'(drug OR medication) AND ({shortage_terms}) {region}'

            print(f"\nSearching: {query} | Year: {year} | Region: {region}")
            
            googlenews = GoogleNews(lang="en", region="CA")
            googlenews.set_time_range(start_date_str, end_date_str)
            googlenews.search(query)
            

            for page in range(1, max_pages + 1):
                try:
                    googlenews.get_page(page)
                    results = googlenews.results(sort=True)
                    time.sleep(random.uniform(2, 5))
                except Exception as e:
                    print(f"Page {page} failed for {region} ({year}) | Error: {e}")
                    break

                if not results:
                    break  # stop if no results on this page

                for r in results:
                    pub_date = parse_google_date(r.get('date', ''))
                    all_results.append({
                        'region_search': region,
                        'year': year,
                        'title': r.get('title', ''),
                        'date': pub_date.date(),
                        'media': r.get('media', ''),
                        'desc': r.get('desc', ''),
                        'link': r.get('link', '')
                    })
                    
    return pd.DataFrame(all_results)


regions = [
 
    # "Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba",
    # "Saskatchewan", "Nova Scotia", "New Brunswick", "Newfoundland and Labrador",
    # "Prince Edward Island", "Northwest Territories", "Yukon", "Nunavut",
 
    # "Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa", "Edmonton",
    # "Winnipeg", "Halifax", "Quebec City", "Regina", "St. John's", "Victoria",
 
    "Canada"
]
 
 
df_region = fetch_news_by_region(regions)
df_region = df_region.sort_values(by='date', ascending=False)
df_region.drop_duplicates(subset="link", inplace=True, keep='last')
 
 
df_region.reset_index(drop=True, inplace=True)
 
def clean_google_news_url(url):
    if not isinstance(url, str):
        return url  
    for param in ['&ved=']: #, '&usg=', '&utm_'
        if param in url:
            url = url.split(param)[0]
    return url.rstrip('/')
 
df_region['link'] = df_region['link'].apply(clean_google_news_url)
 

def save_dataframe_safely(df, filepath):
    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        if df.shape[1] == existing_df.shape[1]:
            # Same number of columns — concatenate and deduplicate
            combined_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset=['link'])
            combined_df.to_csv(filepath, index=False)
            print(f"DataFrame appended and saved to {filepath}")
        else:
            # Mismatched column count — save with new name
            base, ext = os.path.splitext(filepath)
            new_filepath = f"{base}_new{ext}"
            df.to_csv(new_filepath, index=False)
            print(f"Column mismatch. DataFrame saved as {new_filepath}")
    else:
        # File doesn't exist — just save
        df.to_csv(filepath, index=False)
        print(f"DataFrame saved to {filepath}")


save_dataframe_safely(df_region, "news-data/data.csv")     

#df_region.to_csv('news-data/data.csv', index=False)