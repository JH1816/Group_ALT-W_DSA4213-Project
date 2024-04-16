import re
import pandas as pd
from h2o_wave import site, ui,main, app, Q, ui
import pandas as pd

def format_LLM_output(reply_content):
    """
    Extracts movie recommendations from the LLM reply content and formats them into a Pandas DataFrame.

    Parameters:
        reply_content (str): The content containing movie recommendations.

    Returns:
        pd.DataFrame: A DataFrame containing movie recommendations with columns for title, release year, genre, source, and explanation.

    Example:
        >>> reply_content = 'Here are some movie recommendations: [{"title": "Movie1", "release year": 2020, "genre": "Action", "explanation": "A thrilling action-packed movie."}, {"title": "Movie2", "release year": 2019, "genre": "Comedy", "explanation": "A hilarious comedy with great performances."}]'
        >>> format_LLM_output(reply_content)
           Title  Release Year   Genre      Source                               Explanation
        0  Movie1          2020  Action  LLM + RAG               A thrilling action-packed movie.
        1  Movie2          2019  Comedy  LLM + RAG  A hilarious comedy with great performances.
    """
    # Extracting movie recommendations from the reply content
    pattern1 = r'\[([^\]]+)\]'
    movie_recommendations_string = re.findall(pattern1,reply_content)[0]
    movie_string_processed1 = movie_recommendations_string.replace("\n", "")

    pattern2 = r'\{(.*?)\}'
    movie_string_processed2 = re.findall(pattern2,movie_string_processed1)
    
    # Extracting data from each movie recommendation
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

    # Creating a DataFrame with the extracted data
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

def generate_dataframe_as_h2o_content(df):
    """
    Generates a UI form card in h2o wave containing a table representing the provided Pandas DataFrame.

    Parameters:
        df (pd.DataFrame): The Pandas DataFrame to be displayed.

    Returns:
        ui.FormCard: A UI form card containing the table representing the DataFrame.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Title': ['Movie1', 'Movie2'], 'Release Year': [2020, 2019], 'Genre': ['Action', 'Comedy']})
        >>> generate_dataframe_as_h2o_content(df)
    """
    
    def df_to_list_of_dicts(df):
        """
        Converts a Pandas DataFrame to a list of dictionaries.

        Parameters:
            df (pd.DataFrame): The Pandas DataFrame to be converted.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the DataFrame rows.

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'Title': ['Movie1', 'Movie2'], 'Release Year': [2020, 2019], 'Genre': ['Action', 'Comedy']})
            >>> df_to_list_of_dicts(df)
            [{'Title': 'Movie1', 'Release Year': 2020, 'Genre': 'Action'}, {'Title': 'Movie2', 'Release Year': 2019, 'Genre': 'Comedy'}]
        """
        return df.to_dict(orient='records')

    # Convert Pandas DataFrame to list of dictionaries
    table_data = df_to_list_of_dicts(df)

    # Define CSS for table borders
    table_style = """
            .custom-table table {
                border-collapse: collapse;
                width: 150%;
            }
            .custom-table th, .custom-table td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            """
    # Generate UI form card with table
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
