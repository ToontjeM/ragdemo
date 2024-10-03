# RAG demo

This demo is going to show how Postgres can be used to create a generative AI environment.

## Demo preparation
### Prerequisites
- postgresql
	- To install postgresql with the PL/Python extension using Homebrew on a Mac, do the following:
		- `brew tap petere/postgresql`
		- `brew install petere/postgresql/postgresql@17`
	
		When using Postgres.app, please use the instructions on https://www.enterprisedb.com/postgres-tutorials/installation-postgresql-mac-os
- python3 with pip
- ollama

### Demo setup
#### Set up Postgres
- Set up a new database in Postgres. I created a `./db` directory in case you want to run the Postgres instance isolated.
You can create the new instance using `initdb --pgdata=$PWD/db --encoding=UTF8 --locale=en_US.utf8` and then start the new instance using `pg_ctl -D $PWD/db -l logfile start`
- Create a new database using `CREATE DATABASE ragdemo;`
- Install pgvector using the instructions on https://github.com/pgvector/pgvector and create the extension in Postgres using `CREATE EXTENSION vector`.
- Install PL/Python using `apt install postgresql-plpython3` and create the extension using `CREATE EXTENSION plpython3u`.
- run four pl python scripts, you may find these scripts under pl_python sub-directory
   - augmented_response.sql
	- process_files_in_directory.sql
	- process_one_image.sql
	- similar_images.sql

#### Set up python
- I strong suggest to create virtual environment to host the python libraries. You can create the virtual environment using `virtualenv venv` and activate it using `source venv/bin/activate`.
- Once the virtual environment is created, install the following libraries using `pip install`:
	- sycopg2
	- langchain 
	- langchain_text_splitters (usually installed once you install langchain)
	- tiktoken 
	- pypdf
	- pdfplumber
	- streamlit
   - pillow 
	- ollama 
   - transformers
   - If you are working on a Mac, wxPython. This should fix the file upload problem.
   - If you are working on Linux, tkinter. Same as above.

#### Set up ollama
- Pull in the following LLM's into ollama:
	- mxbai-embed-large (`ollama pull mxbai-embed-large`)
	- llama3.1 (`ollama pull llama3.1`)

#### Set up demo scripts
- Change the db username, password and DB hostname in `.streamlit/secrets.toml`.

## Demo flow
- Run the streamlit application using `streamlit run pgvector_usecases.py`.

