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
- Nvidia GPU drivers (`sudo apt install nvidia-driver-535`)


### Demo setup
#### Set up Postgres
- Set up a new database in Postgres using `CREATE DATABASE ragdemo;`
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
	- psycopg2
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
   	- If you are working on Linux, tk. Same as above.
	- If you want to use your GPU, make sure CUDA is installed and run `pip install torch`.
		If the GPU is not detected by ollama, try to unload and reload the uvm module using `sudo rmmod nvidia_uvm`and `sudo modprobe nvidia_uv`. See https://github.com/ollama/ollama/blob/main/docs/troubleshooting.md

Example: `pip install psycopg2 langchain tiktoken pypdf pdfplumber streamlit pillow ollama transformers tk torch`

#### Set up ollama
- Pull in the following LLM's into ollama:
	- mxbai-embed-large (`ollama pull mxbai-embed-large`)
	- llama3.1 (`ollama pull llama3.1`)

#### Set up demo scripts
- Change the db username, password and DB hostname in `.streamlit/secrets.toml`.

## Demo flow
- Run the streamlit application using `streamlit run ragdemo.py`.

