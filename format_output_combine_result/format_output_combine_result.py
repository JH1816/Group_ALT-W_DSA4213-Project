import re
import pandas as pd
from h2o_wave import site, ui,main, app, Q, ui
import pandas as pd

def format_LLM_output(reply_content):
    pattern1 = r'\[([^\]]+)\]'
    movie_recommendations_string = re.findall(pattern1,reply_content)[0]
    movie_string_processed1 = movie_recommendations_string.replace("\n", "")

    pattern2 = r'\{(.*?)\}'
    movie_string_processed2 = re.findall(pattern2,movie_string_processed1)
    
    title_data = []
    release_year_data = []
    genre_data = []
    explanation_data = []


    title_pattern = r'"title":\s*"([^"]*)"'
    release_year_pattern = r'"release year":\s*(.*?)(?=,)'
    genre_pattern = r'"genre":\s*(.*?)(?=,)'
    explanation_pattern = r'"explanation":\s*"([^"]*)"'

    for s in movie_string_processed2:
        title = re.search(title_pattern,s).group(1)
        release_year = re.search(release_year_pattern,s).group(1)
        genre = re.search(genre_pattern,s).group(1)
        explanation = re.search(explanation_pattern,s).group(1)

        title_data.append(title)
        release_year_data.append(release_year)
        genre_data.append(genre)
        explanation_data.append(explanation)

    source_data = ["LLM + RAG"]*len(title_data)

    data = {
        'Title': title_data,
        'Release Year': release_year_data,
        'Genre': genre_data,
        'Source': source_data,
        'Explanation': explanation_data
    }

    result_df = pd.DataFrame(data)

    # Displaying the DataFrame
    return(result_df)


def number_to_ordinal(n):
    suffix = ['th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th']
    if 10 <= n % 100 <= 20:
        suffix_index = 0
    else:
        suffix_index = n % 10
    return str(n) + suffix[suffix_index]

def sequence_of_ordinals(start, end):
    return [number_to_ordinal(i) for i in range(start, end + 1)]


def format_collaborative_output(list_of_movies_recommended):
    title_data = list_of_movies_recommended
    source_data = ["collborative filtering"]*len(title_data)
    explanation_data = []

    sequence = sequence_of_ordinals(1, 10)
    for i in range(len(title_data)):
        explanation = "This is the " + sequence[i] + " movie recommended by Collaborative Filtering algorithm."
        explanation_data.append(explanation)
    
    # Need to be modified for the Release Year and Genre
    
    data = {
        'Title': title_data,
        'Release Year': [2010]*5,
        'Genre': ["Fantasy"]*5,
        'Source': source_data,
        'Explanation': explanation_data
    }
    result_df = pd.DataFrame(data)
    return(result_df)


def combine_LLM_CF_results(reply, list_of_movies_recommended):
    LLM_df = format_LLM_output(reply)
    CF_df = format_collaborative_output(list_of_movies_recommended)
    result_df = pd.concat([LLM_df, CF_df], axis=0,ignore_index=True)
    return result_df
    
def generate_dataframe_as_h2o_content(df):

    def df_to_list_of_dicts(df):
        return df.to_dict(orient='records')

    # Convert Pandas DataFrame to list of dictionaries
    table_data = df_to_list_of_dicts(df)

    # Define CSS for table borders
    table_style = """
            .custom-table table {
                border-collapse: collapse;
                width: 100%;
            }
            .custom-table th, .custom-table td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            """

    content = ui.form_card(
            box='right',
            items=[
                ui.markup(
                    f'<style>{table_style}</style>'
                    '<div class="custom-table">'
                    '<table>'
                    f'<tr>{" ".join([f"<th>{col}</th>" for col in df.columns])}</tr>'
                    f'{" ".join([f"<tr>{"".join([f"<td>{row[col]}</td>" for col in df.columns])}</tr>" for row in table_data])}'
                    '</table>'
                    '</div>'
                ,name="movie_recommendation")
                
            ]
        )
            
        
            
    return content