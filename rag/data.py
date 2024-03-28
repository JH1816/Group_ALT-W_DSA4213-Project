import requests
import pandas as pd

# Wikipedia Movie Data

# Base URL for retrieving movie data
Wikipedia_movie_data_URL = "https://github.com/prust/wikipedia-movie-data/raw/master/movies-{}s.json"

import pandas as pd
import requests

# Wikipedia Movie Data
def wikipedia_movie_data(start_year: int = 1960, end_year: int = 2020):
    """Fetches Wikipedia movie data for specified years.
    
    Parameters:
    start_year: Starting year of the movie required
    end_year: Ending year of the movie required
    """
    
    # Generating list of movie years of interest
    list_of_year_of_interest = []
    num_of_year_of_interest = int((end_year-start_year)/10)
    for i in range(num_of_year_of_interest + 1):
        year_of_interest = str(start_year + 10*i)
        list_of_year_of_interest.append(year_of_interest)
        
    data_results = []  # List to store fetched movie data
    
    # Iterating through year_of_interest and fetching movie data
    for i in range(len(list_of_year_of_interest)):
        year = list_of_year_of_interest[i]
        # Base URL for retrieving movie data
        Wikipedia_movie_data_URL = f"https://github.com/prust/wikipedia-movie-data/raw/master/movies-{year}s.json"
        response = requests.request("GET",Wikipedia_movie_data_URL)
        
        # Converting JSON response to DataFrame
        movie_json = response.json()
        movie_dataframe = pd.DataFrame.from_dict(movie_json)
        data_results.append(movie_dataframe)  # Appending DataFrame to results list
    
    # Concatenating all DataFrames and returning the combined DataFrame
    final_data = pd.concat(data_results, axis=0)

    return final_data

## MovieLens Data
def movielens_data():
    movielens_data = pd.read_csv("../data/ml-25m/movies.csv")
    tags_data = pd.read_csv("../data/ml-25m/tags.csv")
    tags_data = tags_data[['movieId','tag']]
    grouped_tags_data = tags_data.groupby('movieId')['tag'].agg(list).reset_index()
    final_movie_data = pd.merge(movielens_data,grouped_tags_data,on="movieId",how='left')
    return final_movie_data

movielens_data = movielens_data()
Wikipedia_movie_data = wikipedia_movie_data()

# movielens_data.to_excel("movielens_data.xlsx")
# Wikipedia_movie_data.to_excel("Wikipedia_movie_data.xlsx")
