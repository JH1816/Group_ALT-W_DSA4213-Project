import requests
import pandas as pd
from json import loads, dumps

# Wikipedia Movie Data
def wikipedia_movie_data():
    """
    Obtained movie data from Wikipedia from 1960 to 2020.
    """
    start_year = 1960
    end_year = 2020
    
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
    # Select columns that are useful for the data ingestion
    final_data = final_data[["title","year","genres","extract"]]
    final_data['genres'] = final_data['genres'].apply(lambda x: ', '.join(map(str, x)))
    final_data.rename(columns={'extract': 'additional information','title':'movie title','year':'release year'}, inplace=True)

    return final_data

## MovieLens Data
def movielens_data():
    """
    Preprocess movielens_data.
    """
    movielens_data = pd.read_csv("../data/movies.csv")
    tags_data = pd.read_csv("../data/tags.csv")
    tags_data = tags_data[['movieId','tag']]
    grouped_tags_data = tags_data.groupby('movieId')['tag'].agg(list).reset_index()
    grouped_tags_data['tag'] = grouped_tags_data['tag'].apply(lambda x: ', '.join(map(str, x)))
    final_movie_data = pd.merge(movielens_data,grouped_tags_data,on="movieId",how='left')
    final_movie_data[['movie title', 'release year']] = final_movie_data['title'].str.extract(r'([^\(]+)\s*\((\d{4})\)')
    final_movie_data.rename(columns={'tag': 'additional information'}, inplace=True)
    final_movie_data['additional information'] = final_movie_data['movie title'] + " is " + final_movie_data['additional information']
    final_movie_data = final_movie_data[["movie title","release year","genres","additional information"]]
    return final_movie_data

# movielens_data_for_ingestion = movielens_data()
# wikipedia_movie_data_for_ingestion = wikipedia_movie_data()

# df = pd.DataFrame(movielens_data_for_ingestion)

# # Step 1: Identify non-ASCII characters
# non_ascii_columns = df.select_dtypes(include=['object']).apply(lambda x: x.str.contains('[^\x00-\x7F]', regex=True)).any()

# # Step 2: Check encoding (Assuming UTF-8 by default)
# print(df.head())

# # Step 3: Remove non-ASCII characters
# df.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)

# df.to_excel("movielens_data_for_ingestion.xlsx")

# wikipedia_movie_data_for_ingestion.to_excel("wikipedia_movie_data_for_ingestion.xlsx",index=False)

