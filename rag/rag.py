from h2ogpte import H2OGPTE

prompt = """

You are an expert in movies. Using your knowledge and based on the details provided
below, analyse do your best to provide movie recommendations that will appease
to the person asking for movie recommendations.

The person has a preferred genre: {0}. \
The person has a preferred years of releases: {1}. \
Recommend list of candidate movies: []=.\
Return a list of boolean values and explain why the person likes or dislikes.

<< FORMATTING >>
Return a markdown code snippet with a list of JSON object formatted to look like:
{{
    "title": string \ the name of the movie in candidate movies
    "like": boolean \ true or false
    "explanation": string \ explain why the person likes or dislikes the candidate movie
}}

REMEMBER: Each boolean and explanation for each element in candidate movies.
REMEMBER: The explanation must relate to the person's liked and disliked movies.
"""

prompt1 = prompt.format("Horror","2000 to 2010")
prompt2 = prompt.format("fantasy","2010 to 2020")

client = H2OGPTE(
    address='https://h2ogpte.genai.h2o.ai',
    api_key='sk-xxx',       
)

# Create a new collection
collection_id = client.create_collection(
    name='Movie Recommendation System',
    description='To enhance the movie-watching experience, we propose a movie recommendation system which uses data analytics and advanced machine-learning techniques to deliver personalized movie suggestions',
)

# Upload documents
# Many file types are supported: text/image/audio documents and archives

with open('movielens_data.xlsx', 'rb') as f:
    movielens_data = client.upload('movielens_data.xlsx', f)
    
with open('Wikipedia_movie_data.xlsx', 'rb') as f:
    Wikipedia_movie_data = client.upload('Wikipedia_movie_data.xlsx', f)

client.ingest_uploads(collection_id, [movielens_data, Wikipedia_movie_data])

# Create a chat session
chat_session_id = client.create_chat_session(collection_id)

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