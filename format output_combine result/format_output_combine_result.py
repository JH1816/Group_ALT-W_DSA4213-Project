import re
import pandas as pd


def format_LLM_output(reply):
    reply_content = reply.content
    pattern1 = r'\[([^\]]+)\]'
    movie_recommendations_string = re.findall(pattern1,reply_content)[0]
    movie_string_processed1 = movie_recommendations_string.replace("\n", "")

    pattern2 = r'\{(.*?)\}'
    movie_string_processed2 = re.findall(pattern2,movie_string_processed1)
    
    title_data = []
    like_data = []
    explanation_data = []


    title_pattern = r'"title":\s*"([^"]*)"'
    like_pattern = r'"like":\s*(.*?)(?=,)'
    explanation_pattern = r'"explanation":\s*"([^"]*)"'

    for s in movie_string_processed2:
        title = re.search(title_pattern,s).group(1)
        like = re.search(like_pattern,s).group(1)
        explanation = re.search(explanation_pattern,s).group(1)

        title_data.append(title)
        like_data.append(like)
        explanation_data.append(explanation)

    source_data = ["LLM + RAG"]*len(title_data)

    data = {
        'Title': title_data,
        'Like': like_data,
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
    like_data = ["true"]*len(title_data)
    source_data = ["collborative filtering"]*len(title_data)
    explanation_data = []

    sequence = sequence_of_ordinals(1, 10)
    for i in range(len(title_data)):
        explanation = "This is the " + sequence[i] + " movie recommended by Collaborative Filtering algorithm."
        explanation_data.append(explanation)
    data = {
        'Title': title_data,
        'Like': like_data,
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
    


