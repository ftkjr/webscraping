# Import Packages
import csv
from datetime import *
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


def get_job_results(url: str, info_id: str) -> list:
    """Return page results from job site"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id=info_id) 
    return results

# def collect_individual_search_info(site: str, individual_searches: list, total_results_frame, unique_results_frame, search_times: list, total_search_time: float, notes:str = None):
#     """Return individual search info as one DataFrame"""
#     # Create framework for the individual search data. 
#     individual_searches_frame = pd.DataFrame(individual_searches, columns=['search_location', 'search_title'])
#     individual_searches_frame['SearchTimes'] = search_times
#     individual_searches_frame['Site'] = site
#     individual_searches_frame['Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # Collect the counts for the results before removing duplicates.
#     total_results = total_results_frame[['search_title', 'search_location', 'description']].groupby(['search_title', 'search_location'], as_index=False).count()

#     # Collect the counts for the results after removing duplicates.
#     unique_results = unique_results_frame[['search_title', 'search_location', 'description']].groupby(['search_title', 'search_location'], as_index=False).count()

#     # Add the Total Results count to the individual searches frame.
#     individual_searches_frame = pd.merge(
#         individual_searches_frame, 
#         pd.DataFrame({
#             'search_title': total_results['search_title'], 
#             'search_location': total_results['search_location'], 
#             'TotalResults': total_results['description']
#             }),
#         on=['search_title', 'search_location'], 
#         how='left'
#         )

#     # Add the Unique Results count to the individual searches frame.
#     individual_searches_frame = pd.merge(
#         individual_searches_frame, 
#         pd.DataFrame({
#             'search_title': unique_results['search_title'], 
#             'search_location': unique_results['search_location'], 
#             'UniqueResults': unique_results['description']
#             }),
#             on=['search_title', 'search_location'], 
#             how='left'
#             )
    
#         individual_searches_frame[col][individual_searches_frame[col].isnull()] = 0

#     # Add the total search time to the data frame.
#     individual_searches_frame['TotalSearchTime'] = total_search_time
#     # Add any notes we have to the frame.
#     individual_searches_frame['Notes'] = notes
#     individual_searches_frame.to_csv('Diagnostics/ScraperPerformancebySearch.csv', mode='a+', header=False)
  

def preprocess_jobs(initial_data):
    """Clean up the jobs frame"""
    for col in initial_data.columns:
        if col != 'posted': 
            initial_data[col] = initial_data[col].str.replace('\n', ' ')
    processed_data = initial_data.drop_duplicates(subset=['link'], keep='first')
    processed_data['description'] = processed_data['description'].str.replace(r"([a-z])([A-Z])", r"\1 \.\2")
    processed_data['description'] = processed_data['description'].str.replace(r' \\.', '')
    return processed_data

        
# def save_search_stats(site: str, total_returned_jobs: int, unique_jobs: int, search_time: float, total_searches: int, notes = None):
#     """Write search statistics as new row in ScraperPerformance.csv"""
#     with open('Diagnostics/ScraperPerformance.csv', 'a+', newline='') as file:
#         write = csv.writer(file, delimiter=',')
#         if notes is not None:
#             notes = notes.replace(',', ';')
#         write.writerow([site, total_returned_jobs, unique_jobs, search_time, total_searches, date.today(), notes])

####################
# Data Frame Columns
columns = [
    'posting_id',
    'search_title', 'search_location', 
    'location', 'title', 'company', 'posted', 
    'salary', 'summary', 'link', 'description'
    ]

###############
# Job titles
prefixes = [
    'entry level ', 
    'junior ', 'associate ', 
    ''
    ]


titles = [
    'data',
    'data analyst',
    'data scientist', 
    'business analyst', 'financial analyst', 
    # 'macro analyst', 
    # 'data engineer'
            ]
 

search_locations = [
    'New York, NY',
    'Stamford, CT', 'Greenwich, CT',
    'Newark, NJ', 'Princeton, NJ', 'Jersey City, NJ', 
    'Trenton, NJ', 'Bridgewater, NJ', 'Somerville, NJ', 
    'Summit, NJ', 'Morristown, NJ', 'Edison, NJ', 'Metuchen, NJ', 'Hackensack, NJ', 'NJ',
    # 'Philadelphia, PA',
    # 'New York', 'New Jersey', 'New Hampshire', 'Pennsylvania', 'Connecticut',
    # 'NY', 'NJ', 'CT', 
    # 'NH', 'PA',
    #'NH', "New Hampshire", "Manchester, NH", "Concord, NH", "Nashua, NH", "Brattleboro, NH", "Keene, NH",
    'remote' 
    ]

n_searches = (len(titles) * len(prefixes)) * len(search_locations)

#####################################################
# Scrape Monster.com
# Empty container for posting info
jobs_monster = []
visited_link = set()

# Since this is the limited search, prompt the user for the posting date bounds.
n_days_ago = pd.to_numeric(input("Within how many days are we restricting the job posts?\nIntegers only please.\n"))

search_times_monster = []
individual_searches = []

if input("Would you like to see information about the search while it's ongoing? (y/n)\n").lower() == "y":
    ttm = True
elif input("Would you like to see information about the search while it's ongoing? (y/n)\n").lower() == "n":
    ttm = False 
else:
    ttm = True
start_time = time.time()
counter = 1


for search_location in search_locations:
    for search_title in [(s + t) for s in prefixes for t in titles]:

    ####################################
        # Monitoring Chunk
        individual_searches.append([search_location, search_title])
        if counter > 1: 
            search_time = time.time() - search_start
            # search_times_monster.append(search_time)
            
            # If we get blocked from the servers, stop hitting them. 
            if search_time < .01:
                 print("We appear to have overstayed our welcome.")
                 break
 
            if ttm:
                print(f'The search took {search_time} seconds.\n')
        if ttm:
            print(f'Searching Monster for {search_title} positions in {search_location}.\nSearch number {counter} of {n_searches}') 
        counter += 1
        search_start = time.time()
    #####################################
        for pages in ["1&page=8", "9&page=15"]:
            st = search_title.replace(' ', '-')
            sl = search_location.replace(' ', '-').replace(',', '__2C')
            URL = f'https://www.monster.com/jobs/search/?q={st}&where={sl}&stpage={pages}'
            try:
                results = get_job_results(URL, 'ResultsContainer')
            except:
                continue
            
            try:
                job_elems = results.find_all('section', class_='card-content')
            except:
                continue

            for job in job_elems:
                # If the title or company isn't present, continue to the next one
                title_elem = job.find('h2', class_='title')
                if title_elem is None:
                    continue
                else:
                    title = title_elem.text.strip()
                
                link = job.find('a')['href']
                if link in visited_links:
                    continue
                else:
                    visited_links.add(link)
                ###########################
                # Restrict the search     #
                ###########################
                # Only get info for jobs posted within a certain range 
                posted = job.find('time').text.strip()
                if posted[0] == "+":
                    continue
                elif (posted[0] == "P") | (posted[0] == "J"):
                    posted = 0 
                elif pd.to_numeric(posted[:1]) > n_days_ago:
                    continue
                else:
                    posted = pd.to_numeric(posted[:1])

 
                try:
                    posting_id = job.attrs['data-postingid']
                except:
                    posting_id = None
                
                # If the company element isn't present continue to the next
                company_elem = job.find('div', class_='company')
                if company_elem is None:
                    continue
                else:
                    company = company_elem.text.strip()
                
                # If there isn't a job location provided, indicate that
                location_elem = job.find('div', class_='location')
                if location_elem is None:
                    location = 'No Location Found'
                else:
                    location = location_elem.text.strip()

                # When was the job posted
                

                time.sleep(2)
                try:
                    description_results = get_job_results(link, 'main-content')
                except:
                    continue
                try:
                    details_elem = description_results.findAll('div', class_='detail-row')
                except:
                    continue

                salary = None
                job_type = None
                for detail in details_elem:
                    dt = detail.text.strip()
                    if 'Salary' in dt:
                        salary = dt
                    if 'Job Type' in dt:
                        job_type = dt                    
                    if posted is None and 'Posted' in dt:
                        posted = dt

                if salary is None:
                    salary = 'No Salary Provided'
                if job_type is None:
                    job_type = 'No Job Type Provided'
                

                description_elem = description_results.find('div', class_='job-description')
                if description_elem is None:
                    description = 'No Description Found'
                else:
                    description = description_elem.text.strip()
                
                item = [
                    posting_id, 
                    search_title,
                    search_location,
                    location,
                    title,
                    company,
                    posted,
                    salary,
                    job_type,
                    link,
                    description
                ]
                jobs_monster.append(item)
    
# This adds the time for the final search.
search_time = time.time() - search_start
print("Final search took", search_time, "seconds.")
# search_times_monster.append(search_time)
tdy = datetime.now().strftime("%Y-%m-%d")
total_search_time_monster = time.time() - start_time

if ttm:
     print(f'Monster search took {total_search_time_monster} seconds to retreive {len(jobs_monster)} total results (including some duplicates).')

# Convert array of arrays into data frame
monster_0 = pd.DataFrame(jobs_monster, columns=columns)
monster_0.to_csv(f"data/rawdata/{tdy}_monster.csv", index=False)
monster_0.to_csv(f"/home/pi/ShareDrive/data/0rawdata/{tdy}_monster.csv", index=False)

# filter and modify df going forward
monster_1 = preprocess_jobs(monster_0)

# Save the monitoring data into their respective csv's for later analysis.
# collect_individual_search_info saves into a new csv which monitors performance of each individual search
# collect_individual_search_info('Monster', individual_searches, monster_0, monster_1, search_times_monster, total_search_time_monster)
# save_search_stats('Monster', len(monster_0), len(monster_1), total_search_time_monster, n_searches)


monster_1.to_csv(f"/home/pi/ShareDrive/data/{tdy}_monster.csv")
monster_1.to_csv(f"data/{tdy}_monster.csv")
print(f'Returned {len(monster_1)} unique entries from Monster.com \n file date: {tdy}')
