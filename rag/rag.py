from h2ogpte import H2OGPTE

prompt = '''
    As a movie enthusiast with expertise in the field, your task is to utilize your 
    knowledge and the given information to analyze and offer tailored movie
    suggestions that align with the preferences of the person seeking recommendations.

    The person has a preferred genre: {0}. \
    The person has a preferred years of releases: {1} to {2}. \
    User favourite movie: {3}
    Recommend list of movies using below formatting:

    << FORMATTING >>
    Return a markdown code snippet with a list of JSON object formatted as below:
    {{
        "title": string \ Denotes the title of a movie
        "released year": integer \ Denotes the released year of the movie
        "genre": string \ Denotes the genre of the movie
        "like": boolean \ true or false
        "explanation": string \ Provide an explanation about why this person likes or dislikes this movie.
    }}

    Important Note: Provide a boolean value and an explanation for each movie in the list of recommended movies.
    Important Note: The explanation must be relevant to the individual's preferences for liked and disliked movies.
    '''

prompt1 = prompt.format("Horror","2000","2010","Playback")
prompt2 = prompt.format("fantasy","2010", "2020", "Toy Story")

client = H2OGPTE(
    address='https://h2ogpte.genai.h2o.ai',
    api_key='sk-Xe7ocXvl1gW4HzLnMTh8QQuIutmb6OwBAHF2sQvCgxbbeSB2',       
)

# Create a new collection
collection_id = client.create_collection(
    name='Movie Recommendation System_Collection',
    description='To enhance the movie-watching experience, we propose a movie recommendation system which uses data analytics and advanced machine-learning techniques to deliver personalized movie suggestions',
)

# Upload documents
# Many file types are supported: text/image/audio documents and archives

with open('movielens_data_for_ingestion.xlsx', 'rb') as f:
    movielens_data_for_ingestion = client.upload('movielens_data_for_ingestion.xlsx', f)

with open('wikipedia_movie_data_for_ingestion.xlsx', 'rb') as f:
    wikipedia_movie_data_for_ingestion = client.upload('wikipedia_movie_data_for_ingestion.xlsx', f)


client.ingest_uploads(collection_id, [movielens_data_for_ingestion, wikipedia_movie_data_for_ingestion])

# Create a chat session
chat_session_id = client.create_chat_session('3cdf2f07-c4cb-4d05-9cf7-9935488fab27')

# Query the collection
with client.connect(chat_session_id) as session:
    reply = session.query(
        prompt1,
        timeout=60,
    )
    print(reply.content)

    reply = session.query(
        prompt2,
        timeout=60,
    )
    print(reply.content)