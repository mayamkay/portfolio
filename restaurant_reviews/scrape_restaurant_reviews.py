''' This script scrapes the Yelp website to get the names, ratings, number of ratings and neighborhoods
 of the top 100 restaurants in 40 cities around the world. Note that yelp will change its html structure occasionally so the
html tags may need to be updated to reflect these changes. The data is saved to a csv file called mean_review.csv.'''

import urllib
from bs4 import BeautifulSoup
import urllib.request
from time import sleep
import pandas as pd
import numpy as np

def get_names(soup):
    '''Get the names of the restaurants from the soup object.'''
    names = []
    base = soup.find_all("h3", class_="y-css-hcgwj4")
    for r in base:
        names.append(r.text.strip().split('\xa0', 1)[1])
    return names

def get_ratings(soup):
    '''Get the ratings and number of ratings of the restaurants from the soup object.'''
    rating = []
    num_ratings = []
    base = soup.find_all("div", class_="y-css-1fnvi93")
    for r in base:
        try:
            rate = r.find("span", class_="y-css-jf9frv")
            rating.append(float(rate.text.strip()))
            num = r.find("span", class_="y-css-wfbtsu").text.strip()
            num = num.replace('(', '').replace(" reviews)", "")

            # Yelp uses 'k' to indicate thousands so this needs to be converted
            if num.find('k') > 0:
                num = float(num.replace('k', '')) * 1000
            num_ratings.append(int(num))
        except:
            continue
    return rating, num_ratings

def get_neighborhoods(soup):
    '''Get the neighborhoods of the restaurants from the soup object.'''
    neighborhood = []
    base = soup.find_all("div", class_="y-css-1lvo3zq")
    for r in base:
        r = r.find("span", class_="y-css-wfbtsu")
        neighborhood.append(r.text.strip())
    return neighborhood

# List of cities and countries, these can be adapted to any cities for which Yelp has results
locs = ["london", "newyork", "hongkong", "chicago", "losangeles", "berlin", "paris", "tokyo", "sydney", 
            "singapore", "toronto", "sanfrancisco", "barcelona", "amsterdam", "rome",  "istanbul",
            "mexicocity", "saopaulo",    "kualalumpur", "prague", "Seattle", "Portland", "SanDiego", "Denver",
            "Austin", "Boston", "Philadelphia", "Atlanta", "Miami", "NewOrleans","Nashville", "Detroit", 
            "Minneapolis", "KansasCity", "SaltLakeCity", "LasVegas", "Albuquerque", "Honolulu", "Anchorage"]

country = ["UK", "USA", "China", "USA", "USA", "Germany", "France", "Japan", "Australia",
            "Singapore","Canada", "USA", "Spain", "Netherlands", "Italy", "Turkey", "Mexico", 
            "Brazil", "Malaysia", "Czech Republic", "USA", "USA", "USA", "USA", "USA", "USA", 
            "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA"]

# Initialize lists to store the data
mean_review = []

# If save_all_data is set to True, the data for each individual city will be saved to a csv file
save_all_data = False

for location in locs:
    
    # Initialize variables
    done = False
    page_number = 0
    names = []
    ratings = []
    number_of_ratings = []
    neighborhoods = []

    while done == False:
        # Get the html content of the page
        url = "https://www.yelp.com/search?find_desc=Restaurants&find_loc={}&sortby=review_count&start={}".format(location, page_number)
        ourUrl = urllib.request.urlopen(url)
        soup = BeautifulSoup(ourUrl,'html.parser')

        # If there are no more pages or we have collected information about 100 restaurants stop the loop
        if len(soup.find_all("h3", class_="y-css-hcgwj4"))==0 or len(names)>=100:
            done = True
            print("done colecting data for {}".format(location))

            # Calculate the mean review for the restaurants
            try:
                mean_review.append(sum(np.asarray(ratings)*np.asarray(number_of_ratings))/sum(number_of_ratings))
            except:
                mean_review.append(np.nan)

            # Save the data to a csv file
            if save_all_data==True:
                try:
                    data = {"name": names, "rating": ratings, "number_of_ratings": number_of_ratings, "neighborhood": neighborhoods}
                    df = pd.DataFrame(data)
                    df.to_csv("{}_ratings.csv".format(location), index=False)
                except:
                    continue
        
        # If there are more pages to scrape, get the information from the current page and move to the next page
        else:
            neighborhoods.extend(get_neighborhoods(soup))
            rating, num_ratings = get_ratings(soup)
            ratings.extend(rating)
            number_of_ratings.extend(num_ratings)
            names.extend(get_names(soup))

            # Move to the next page
            page_number += 10

        # to avoid Yelp flagging the requests pause between requests
        sleep(7)

# Save the data to a csv file using pandas
data = {"city": locs, "country": country, "mean_review": mean_review}
mean_review = pd.DataFrame(data)
mean_review.to_csv("mean_review.csv", index=False) 
