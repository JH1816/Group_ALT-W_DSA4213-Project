# Group ALT+W DSA4213-Project

Let AI recommend movies to you

## To run the app Locally

python3.10 -m venv venv

./venv/bin/pip install -r requirements.txt

./venv/bin/wave run src/app.py

export H2OGPT_API_TOKEN=""

export H2OGPT_URL="https://**.h2ogpt.h2o.ai"

## To run the app Locally (Windows version)

### Create virtual environment
py -m venv venv

### Activate virtual environment
venv\Scripts\activate

### Install requirements
venv\Scripts\pip install -r requirements.txt

### Run application
venv\Scripts\wave run src\app.py

## RAG Framework (rag directory)

### Overview
This folder contains scripts for implementing the RAG (Retrieval-Augmented Generation) framework, specifically for a movie recommendation system. 

### Contents
1. `data.py`: This script is used to obtain and preprocess data for ingestion into the RAG framework. It likely includes functionalities for fetching data from external sources, cleaning, and formatting it for further processing.

2. `rag.py`: This script implements the RAG framework using the H2OGPTE (H2O.ai's Gradient Powered Transformer Embedding) library. It includes functions to initialize the H2OGPTE client, create a new collection for the movie recommendation system, and upload movie data documents to the collection. Additionally, it may contain other functionalities for building the RAG model and performing recommendation tasks.

3. `movielens_data_for_ingestion.xlsx` and `wikipedia_movie_data_for_ingestion.xlsx`: The data that created from `data.py` and to be ingested to create a new collection in `rag.py`.

### Usage
1. **data.py**: Before running `rag.py`, ensure that `data.py` has been executed to obtain and preprocess the necessary data. Modify `data.py` as needed to suit your specific data sources and preprocessing requirements.

2. **rag.py**: Run this script to initialize the RAG framework and perform movie recommendations. Ensure that the H2OGPTE library is installed and properly configured before running this script.

### Note
Embedding Model: The RAG framework utilizes the `bge-large-en-v1.5` embedding model for generating contextual embeddings of input text.

Large Language Model: The RAG framework incorporates the `LLM Mixtral-8x7B` language model for text generation tasks. It is configured with a low temperature (0.1) setting and moderate output tokens (1024) generation for balanced output quality and diversity.

## Format LLM Output (format_LLM_output directory)

### Overview
This folder contains scripts for formatting the output of a Language Model (LLM) into a structured format, specifically tailored for movie recommendations. 

### Contents
1. `format_LLM_output.py`: This script includes two functions designed to handle the output of an LLM model and format it into a Pandas DataFrame:
   - **`format_LLM_output`**: Extracts movie recommendations from the LLM reply content and formats them into a Pandas DataFrame. This function parses the output text of the LLM model and extracts relevant movie recommendations.
   - **`generate_dataframe_as_h2o_content`**: Generates a UI form card in H2O Wave containing a table representing the provided Pandas DataFrame. This function prepares the DataFrame in a format suitable for displaying in a UI, facilitating easy visualization and interaction.

### Usage
The two functions (**`format_LLM_output`** and *`generate_dataframe_as_h2o_content`**) are imported to the `app.py` in `src` directory to process the output of the LLM model and generate a UI form card in H2O Wave containing a table representing the provided DataFrame.

