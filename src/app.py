from h2o_wave import main, app, Q, ui, run_on, copy_expando, on ,data
import os
import toml
import asyncio
import joblib
import pandas as pd
from datetime import datetime
from loguru import logger
from src.wave_utils import heap_analytics
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage
from format_output_combine_result.format_output_combine_result import format_LLM_output
from format_output_combine_result.format_output_combine_result import generate_dataframe_as_h2o_content

@app('/')
async def serve(q: Q):
    logger.info("Starting user request")
    copy_expando(q.args, q.client)  # Save any UI responses of the User to their session

    if not q.client.initialized:
        await initialize_session(q)

    elif not await run_on(q):
        await generate_prompt(q)
    await q.page.save()


async def initialize_session(q: Q):
    logger.info("Initializing the app for this browser session")
    if not q.app.initialized:
        await initialize_app(q)
    
    q.client.genres = ["science fiction", "fantasy", "drama",
              "romance", "comedy", "zombie", "action",
              "historical", "horror", "war"]
    q.client.cooking_instructions = True
    q.client.year_of_release_from = '1980'
    q.client.year_of_release_to = '2023'
    q.client.select_movie = 'Toy Story'

    landing_page_layout(q)

    if os.getenv("MAINTENANCE_MODE", "false") == "true":
        q.page["meta"].dialog = ui.dialog(
            title="",
            blocking=True,
            closable=True,
            items=[
                ui.text_xl("<center>This app is under maintenance!</center>"),
                ui.text("<center>Please come back soon for meal planning assistance.</center>")

            ],
        )
        return

    prompt_generating_form(q)
    await generate_prompt(q)
    q.client.initialized = True


async def initialize_app(q: Q):
    logger.info("Initializing the app for all users and sessions - this runs the first time someone visits this app")
    q.app.toml = toml.load("app.toml")
    movies_list =pd.read_csv('./data/movies_full.csv')
    movies_list.dropna(inplace=True)
    movies_list.reset_index(drop=True, inplace=True)
    
    movies = pd.read_csv("./data/movies_full.csv")
    df = pd.read_csv("./data/ratings.csv", index_col = 0)
    movies = movies[['movieId', 'title', 'year_of_release','genres', 'extract']]
    movies.rename(columns={'extract': 'Explanation', 'year_of_release':'Release Year'}, inplace = True)
    movies = movies.dropna()
    movies['Source'] = 'collaborative filtering'


    pivot_df = df.pivot_table(index='movieId', columns='userId', values='rating')
    pivot_df = pivot_df.fillna(0)


    # Drop columns with all zeros (movies not rated by any user)
    q.app.movies = movies
    q.app.pivot_df_filtered = pivot_df.loc[:, (pivot_df != 0).any(axis=0)]
    q.app.model = joblib.load('collaborative_filtering.pkl' , mmap_mode ='r')
    q.args.select_movie = 'Toy Story'

    q.app.movies_list=movies_list['title'].tolist()
    q.app.initialized = True

def landing_page_layout(q: Q):
    logger.info("")
    q.page['meta'] = ui.meta_card(
        box='',
        title=q.app.toml['App']['Title'],
        icon="https://icons.veryicon.com/png/o/miscellaneous/general-bottom-guide-monochrome-icon/movie-night-movie-list.png",
        theme="lighting",
        script=heap_analytics(),
        stylesheet=ui.inline_stylesheet("""
            [data-test="footer"] a {color: #0000EE !important;}
             
            [data-test="source_code"] {background-color: #FFFFFF !important;}
            [data-test="app_store"] {background-color: #FFFFFF !important;}
            [data-test="support"] {background-color: #FFFFFF !important;}
            
        """),
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width="1600px",
                zones=[
                    ui.zone(name='header'),
                    ui.zone(name="mobile", size="1"),
                    ui.zone(name="footer")
                ]
            ),
            ui.layout(
                breakpoint='l',
                min_height='100vh',
                max_width="1600px",
                zones=[
                    ui.zone(name='header'),
                    ui.zone('body', size='1', direction=ui.ZoneDirection.ROW, zones=[
                        ui.zone('left', size='40%'),
                        ui.zone('right', size='60%'),
                    ]),
                    ui.zone(name="footer")
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title=q.app.toml['App']['Title'],
        subtitle=q.app.toml["App"]["Description"],
        icon="https://icons.veryicon.com/png/o/miscellaneous/general-bottom-guide-monochrome-icon/movie-night-movie-list.png",
        items=[
            ui.button(
                name="source_code",
                icon="Code",
                path="https://github.com/h2oai/genai-app-store-apps/tree/main/weekly-dinner-plan",
                tooltip="View the source code",
            )
        ]
    )

    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with [Wave](https://wave.h2o.ai), [h2oGPTe](https://h2o.ai/platform/enterprise-h2ogpte)",
    )

def generate_year_choices(from_year_str):
    from_year = int(from_year_str)
    return [ui.choice(name=str(i), label=str(i)) for i in range(from_year, 2025)]

def movie_recommender(movie_title,movies, pivot_df_filtered, model,k=10):
    # Find the movieId of the input movie title
    movie_id = movies[movies['title'].str.contains(movie_title, case=False)]['movieId'].values[0]

    # Find the k-nearest neighbors of the input movie
    distances, indices = model.kneighbors(pivot_df_filtered.loc[movie_id].values.reshape(1, -1), n_neighbors=k+1)

    # Get the movieIds of the k-nearest neighbors
    neighbor_movie_ids = pivot_df_filtered.iloc[indices[0][1:]].index.tolist()

    # Get the movie titles and genres from the movies DataFrame
    neighbor_movies_info = movies[movies['movieId'].isin(neighbor_movie_ids)][['title', 'Release Year', 'genres','Source', 'Explanation']]

    neighbor_movies_df = pd.DataFrame(neighbor_movies_info)
    neighbor_movies_df['genres'] = neighbor_movies_df['genres'].str.replace('|', ',')
    neighbor_movies_df = neighbor_movies_df.rename(columns={'title': 'Title', 'genres': 'Genres'})

    return neighbor_movies_df

def make_markdown_row(values):
    return f"| {' | '.join([str(x) for x in values])} |"


def make_markdown_table(fields, rows):
    return '\n'.join([
        make_markdown_row(fields),
        make_markdown_row('-' * len(fields)),
        '\n'.join([make_markdown_row(row) for row in rows]),
    ])



@on("year_of_release_from")
async def update_release_to(q: Q):
    from_year = int(q.args.year_of_release_from)
    q.page['input_form'].year_of_release_to.choices = generate_year_choices(from_year)
    await q.page.save()


def prompt_generating_form(q):
    logger.info("")

    # Options for movie recommendation
    year_of_release_from = range(1980, 2024)
    genres = ["science fiction", "fantasy", "drama",
              "romance", "comedy", "zombie", "action",
              "historical", "horror", "war"]

    q.page['input_form'] = ui.form_card(
        box=ui.box('left', size="0"),
        items=[
            ui.text_l("<b>Get Started</b>"),
            ui.text("Provide information about your movie preferences to generate a list of movie recommendations from our AI model!"),
            ui.inline(justify='around',
                      items=[
                          ui.dropdown(
                              name='year_of_release_from',
                              label='Year of release from',
                              width='50%',
                              value=q.client.year_of_release_from,
                              trigger=True,
                              choices=[ui.choice(name=str(i), label=str(i)) for i in year_of_release_from]
                          ),
                          ui.dropdown(
                              name='year_of_release_to',
                              label='Year of release to',
                              width='50%',
                              value=q.client.year_of_release_from_to,
                              trigger=True,
                              choices=generate_year_choices(q.client.year_of_release_from)
                          ),
                      ]),

            ui.dropdown(
                name='select_movie',
                label='Select a favourite movie from this list',
                trigger=True,
                value=q.app.movies_list[0] if len(q.app.movies_list) > 0 else 'Toy Story',
                choices=[ui.choice(name=m, label=m) for m in q.app.movies_list]
            ),

            ui.checklist(
                name='genres',
                label='Genres',
                inline=True,
                trigger=True,
                values=q.client.genres,
                choices=[ui.choice(name=i, label=i) for i in genres]
            ),
        ]
    )

    q.page["movie_recommendation"] = ui.form_card(title="Movie Recommendations", box="right", items=[ui.text(name="movie_recommendation", content="Waiting for Input")])
    q.page["movie_recommendation2"] = ui.form_card(title="Movie Recommendations from collaborative filtering", box="right", items=[ui.text(name="movie_recommendation2", content="Waiting for Input")])

@on()
async def generate_prompt(q: Q):
    logger.info("")
    # movie_description = ""
    # if q.client.movie_description
    #     movie_description = " Include  movie description for each movie."

    q.client.prompt = f'''
    As a movie enthusiast with expertise in the field, your task is to utilize your 
    knowledge and the given information to analyze and offer tailored movie
    suggestions that align with the preferences of the person seeking recommendations.

    The person has a preferred genre: {q.client.genres}. \
    The person has a preferred years of releases: {q.client.year_of_release_from} to {q.client.year_of_release_to}. \
    The person's favourite movie: {q.client.select_movie}
    Recommend list of movies using below formatting:

    << FORMATTING >>
    Return a markdown code snippet with a list of JSON object formatted as below:
    {{
        "title": string \ Denotes the title of a movie
        "release year": integer \ Denotes the released year of the movie
        "genre": string \ Denotes the genre of the movie
        "explanation": string \ Provide an explanation about why the person likes this movie.
    }}

    Important Note: The movie release year must be within the person's preferred years of releases.
    Important Note: The explanation must be relevant to the person's preferences for the movies.
    '''

    q.page['prompt_card'] = ui.form_card(
        box='left',
        items=[
            ui.text_l("<b>Customized Prompt</b>"),
            ui.textbox(name='prompt', label="", value=q.client.prompt, multiline=True, height='200px'),
            ui.inline(
                justify='center',
                items=[ui.button(name='generate_movie', label='Generate Movie recommendations', primary=True)]
            )
        ]
    )
    


@on()
async def generate_movie(q: Q):
    """
    Handle a user interacting with the chat bot component.

    :param q: The query object for H2O Wave that has important app information.
    """
    collaborative_filterring_df = movie_recommender(q.client.select_movie,q.app.movies, q.app.pivot_df_filtered, q.app.model)
    q.page["movie_recommendation2"] = ui.form_card(
            box='right',
            items=[
                ui.text(make_markdown_table(
                    fields=collaborative_filterring_df.columns.tolist(),
                    rows=collaborative_filterring_df.values.tolist(),
                ))
        ]  
    )
    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt)
    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))
    await q.run(chat, q.client.chatbot_interaction)
    await update_ui


async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 1/10th of a second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """
    

    while q.client.chatbot_interaction.responding:
        q.page["movie_recommendation"].movie_recommendation.content = q.client.chatbot_interaction.content_to_show
        #q.page["movie_recommendation2"] = ui.form_card(title="Movie Recommendations from collaborative filtering", box="right", items=[ui.text(name="movie_recommendation2", content="loading recommendation")])
        await q.page.save()
        await q.sleep(0.1)
    try:
        #collaborative_filterring_df = movie_recommender(q.args.select_movie,q.app.movies, q.app.pivot_df_filtered, q.app.model)
        reply_content = q.client.chatbot_interaction.content_to_show
        result_df = format_LLM_output(reply_content)
        #df = pd.concat([result_df,collaborative_filterring_df])
        #result_content = generate_dataframe_as_h2o_content(result_df)
        #collaborative_filterring_df = movie_recommender(q.args.select_movie,q.app.movies, q.app.pivot_df_filtered, q.app.model)
        
        q.page["movie_recommendation"] = ui.form_card(
            box='right',
            items=[
                ui.text(make_markdown_table(
                    fields=result_df.columns.tolist(),
                    rows=result_df.values.tolist(),
                ))
                ]  
            )
    #     collaborative_filterring_df = movie_recommender(q.client.select_movie,q.app.movies, q.app.pivot_df_filtered, q.app.model)
    #     q.page["movie_recommendation2"] = ui.form_card(
    #         box='right',
    #         items=[
    #             ui.text(make_markdown_table(
    #                 fields=collaborative_filterring_df.columns.tolist(),
    #                 rows=collaborative_filterring_df.values.tolist(),
    #             ))
    #     ]  
    # )
        #q.page["movie_recommendation"] = result_content
        #q.page["movie_recommendation"] = collaborative_filterring_df
    except Exception as e:
        q.page["movie_recommendation"].movie_recommendation.content = q.client.chatbot_interaction.content_to_show
    await q.page.save()
 


def chat(chatbot_interaction):
    """
    Send the user's message to the LLM and save the response
    :param chatbot_interaction: Details about the interaction between the user and the LLM
    :param chat_session_id: Chat session for these messages
    """

    def stream_response(message):
        """
        This function is called by the blocking H2OGPTE function periodically for updating the UI
        :param message: response from the LLM, this is either a partial or completed response
        """
        chatbot_interaction.update_response(message)

    try:
        client = H2OGPTE(address='https://h2ogpte.genai.h2o.ai', api_key='sk-Xe7ocXvl1gW4HzLnMTh8QQuIutmb6OwBAHF2sQvCgxbbeSB2')
        collection_id = '3cdf2f07-c4cb-4d05-9cf7-9935488fab27'

        #chat_session_id = client.create_chat_session(collection_id)
        chat_session_id = '6fbe24d2-5fcb-493d-9984-85140434cbdf'

        with client.connect(chat_session_id) as session:
            session.query(
                system_prompt="You are an expert at movie recommendations.",
                message=chatbot_interaction.user_message,
                timeout=60,
                callback=stream_response,
            )

        #client.delete_chat_sessions([chat_session_id])

    except Exception as e:
        logger.error(e)
        return f""


class ChatBotInteraction:
    def __init__(self, user_message) -> None:
        self.user_message = user_message
        self.responding = True

        self.llm_response = ""
        self.content_to_show = "🔵"

    def update_response(self, message):
        if isinstance(message, ChatMessage):
            self.content_to_show = message.content
            self.responding = False
        elif isinstance(message, PartialChatMessage):
            self.llm_response += message.content
            self.content_to_show = self.llm_response + " 🔵"
