
from GoogleNews import GoogleNews
import time
import pandas as pd

all_results=[]

googlenews = GoogleNews(lang='en', region='Canada',encode='utf-8',period='7d')
query = 'Drug Shortages in Canada'
googlenews.search(query)
#time.sleep(7)

results= googlenews.results(sort=True)

for r in results:
  all_results.append({
      'title': r.get('title',''),
      'media': r.get('media',''),
      'desc': r.get('desc',''),
      'link': r.get('link',''),
      'pub_date': r.get('date','')
  })


temp = pd.DataFrame(all_results)
temp.to_csv('news-data/drug-shortage-news.csv',index=False)