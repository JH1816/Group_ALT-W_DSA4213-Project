from h2o_wave import main, app, Q, ui, run_on, copy_expando, on ,data
import os
import toml
import asyncio
from datetime import datetime
from loguru import logger
from src.wave_utils import heap_analytics
from h2ogpte import H2OGPTE
from h2ogpte.types import ChatMessage, PartialChatMessage


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

    q.client.restrictions = []
    q.client.genres = ["science fiction", "fantasy", "drama",
              "romance", "comedy", "zombie", "action",
              "historical", "horror", "war"]
    q.client.cooking_instructions = True
    q.client.year_of_release_from = '1980'
    q.client.year_of_release_to = '2024'

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



@on("year_of_release_from")
async def update_release_to(q: Q):
    from_year = int(q.args.year_of_release_from)
    q.page['input_form'].year_of_release_to.choices = generate_year_choices(from_year)
    await q.page.save()


def prompt_generating_form(q):
    logger.info("")

    # Options for movie recommendation
    year_of_release_from = range(1980, 2025)
    year_of_release_from_to = range(1980, 2025)
    restrictions = ['G', 'PG', 'PG13', 'NC16', 'M18', 'R21']
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
                        #   ui.toggle(
                        #       name='movie_description',
                        #       label='Movie Description',
                        #       trigger=True,
                        #       value=q.client.movie_description)
                      ]),

            ui.checklist(
                name='restrictions',
                label='Restrictions',
                inline=True,
                trigger=True,
                values=q.client.restrictions,
                choices=[ui.choice(name=i, label=i) for i in restrictions]
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

    q.page["movie_recommendation"] = ui.form_card(box="right", items=[ui.text(name="movie_recommendation", content="")])

@on()
async def generate_prompt(q: Q):
    logger.info("")
    # movie_description = ""
    # if q.client.movie_description
    #     movie_description = " Include  movie description for each movie."

    prompt = f'''
    You are an expert in movies. Using your knowledge and based on the details provided
    below, analyse do your best to provide movie recommendations that will appease
    to the person asking for movie recommendations.

    The person has a preferred genre: {q.client.genres}. \
    The person has a preferred years of releases: {q.client.year_of_release_from} to {q.client.year_of_release_to}. \
    Movie rating restrictions: {q.client.restrictions} \
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

    '''

    q.page['prompt_card'] = ui.form_card(
        box='left',
        items=[
            ui.text_l("<b>Customized Prompt</b>"),
            ui.textbox(name='prompt', label="", value=prompt, multiline=True, height='200px'),
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
        await q.page.save()
        await q.sleep(0.1)
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
        collection_id = '00a25338-035a-467f-a6d0-fcdb6f8fdcf4'

        chat_session_id = client.create_chat_session(collection_id)

        with client.connect(chat_session_id) as session:
            session.query(
                system_prompt="You are an expert at movie recommendations.",
                message=chatbot_interaction.user_message,
                timeout=60,
                callback=stream_response,
            )

        client.delete_chat_sessions([chat_session_id])

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
