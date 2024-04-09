import requests
import pandas as pd
from json import loads, dumps
import pdfkit
import glob

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
    final_movie_data = final_movie_data[["movie title","release year","genres","additional information"]]
    return final_movie_data

def process_data_for_ingestion():
    """
    Combine movie data of Wikipedia and Movie Lens.
    """
    movielens_data_ = movielens_data()
    Wikipedia_movie_data = wikipedia_movie_data()
    final_data = pd.concat([movielens_data_,Wikipedia_movie_data],axis=0)
    final_data = final_data.reset_index(drop=True)
    return final_data

# Below is to convert dataframe to html
# data_for_ingestion = process_data_for_ingestion()
# data_for_ingestion.to_html('movie_data_for_ingestion.html')

# Below is to convert html to pdf
# config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
# for file in glob.glob('./*.html'):
#     pdfkit.from_file(file, file[:-4]+'.pdf', configuration=config)


