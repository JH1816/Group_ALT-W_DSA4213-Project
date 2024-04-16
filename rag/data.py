import requests
import pandas as pd
from json import loads, dumps

# Wikipedia Movie Data
def wikipedia_movie_data():
    """
    Retrieves movie data from Wikipedia spanning the years 1960 to 2020.

    Returns:
        pandas.DataFrame: A DataFrame containing movie data with columns for movie title, 
        release year, genres, and additional information.
    Example:
        >>> wikipedia_movie_data()
                      movie title  release year               genres  \
        0  The Shawshank Redemption          1994                Drama   
        1             The Godfather          1972         Crime, Drama   
        2           The Dark Knight          2008  Action, Crime, Drama   

                               additional information  
        0          Description of the Shawshank Redemption  
        1                      Description of The Godfather  
        2                    Description of The Dark Knight  

    """
 

    start_year = 1960
    end_year = 2020
    
    # Generating list of movie years of interest
    list_of_year_of_interest = []
    num_of_year_of_interest = int((end_year - start_year) / 10)
    for i in range(num_of_year_of_interest + 1):
        year_of_interest = str(start_year + 10 * i)
        list_of_year_of_interest.append(year_of_interest)
        
    data_results = []  # List to store fetched movie data
    
    # Iterating through years of interest and fetching movie data
    for year in list_of_year_of_interest:
        # Base URL for retrieving movie data
        Wikipedia_movie_data_URL = f"https://github.com/prust/wikipedia-movie-data/raw/master/movies-{year}s.json"
        response = requests.get(Wikipedia_movie_data_URL)
        
        # Converting JSON response to DataFrame
        movie_json = response.json()
        movie_dataframe = pd.DataFrame.from_dict(movie_json)
        data_results.append(movie_dataframe)  # Appending DataFrame to results list
    
    # Concatenating all DataFrames and returning the combined DataFrame
    final_data = pd.concat(data_results, axis=0)
    
    # Selecting columns useful for data ingestion
    final_data = final_data[["title", "year", "genres", "extract"]]
    
    # Combining multiple genres into a single string
    final_data['genres'] = final_data['genres'].apply(lambda x: ', '.join(map(str, x)))
    
    # Renaming columns for clarity
    final_data.rename(columns={'extract': 'additional information', 'title': 'movie title', 'year': 'release year'}, inplace=True)

    return final_data

## MovieLens Data
def movielens_data():
    """
    Preprocesses MovieLens data.

    Reads movie and tags data from CSV files, preprocesses and merges them. Extracts
    movie title and release year from the 'title' column, creates additional information
    by combining movie title and tags. Removes non-ASCII characters from the data.

    Returns:
        pandas.DataFrame: Preprocessed MovieLens data containing columns:
            'movie title', 'release year', 'genres', 'additional information'.

    Example:
        >>> movielens_data()
                movie title release year  \
        0         Toy Story         1995   
        1           Jumanji         1995   
        2  Grumpier Old Men         1995   
        3           Sabrina         1995   
        4      Tom and Huck         1995   

                                         genres  \
        0  Adventure|Animation|Children|Comedy|Fantasy   
        1                   Adventure|Children|Fantasy   
        2                               Comedy|Romance   
        3                               Comedy|Romance   
        4                           Adventure|Children   

                                   additional information  
        0  Toy Story is animated, Animation, Children, ...  
        1  Jumanji is fantasy, fantasy, Magic Board Game  
        2                Grumpier Old Men is Moldy, Comedy  
        3         Sabrina is Humorous, Romantic, Comedy,...  
        4  Tom and Huck is based on a novel, Adventure,...
    """

    # Read movie data
    movielens_data = pd.read_csv("../data/movies.csv")
    
    # Read tags data and select relevant columns
    tags_data = pd.read_csv("../data/tags.csv")
    tags_data = tags_data[['movieId','tag']]
    
    # Group tags by movieId and join them into a single string
    grouped_tags_data = tags_data.groupby('movieId')['tag'].agg(list).reset_index()
    grouped_tags_data['tag'] = grouped_tags_data['tag'].apply(lambda x: ', '.join(map(str, x)))
    
    # Merge movie data with grouped tags data
    final_movie_data = pd.merge(movielens_data,grouped_tags_data,on="movieId",how='left')
    
    # Extract movie title and release year from the 'title' column
    final_movie_data[['movie title', 'release year']] = final_movie_data['title'].str.extract(r'([^\(]+)\s*\((\d{4})\)')
    
    # Rename 'tag' column to 'additional information'
    final_movie_data.rename(columns={'tag': 'additional information'}, inplace=True)
    
    # Combine movie title and additional information
    final_movie_data['additional information'] = final_movie_data['movie title'] + " is " + final_movie_data['additional information']
    
    # Select desired columns and remove non-ASCII characters
    final_movie_data = final_movie_data[["movie title","release year","genres","additional information"]]
    final_movie_data.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)
    
    return final_movie_data

# Below is to saved the data as Excel (.xlsx) file to be ingested into RAG
# movielens_data_for_ingestion = movielens_data()
# wikipedia_movie_data_for_ingestion = wikipedia_movie_data()
# movielens_data_for_ingestion.to_excel("movielens_data_for_ingestion.xlsx",index=False)
# wikipedia_movie_data_for_ingestion.to_excel("wikipedia_movie_data_for_ingestion.xlsx",index=False)
