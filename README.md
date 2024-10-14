# RAG demo

This demo is going to show how Postgres can be used to create a generative AI environment.

## Demo preparation
The trick in this demo is to run Postgres in a Python environment where the Postgres instance can see Python modules. You can install the modules globally, but that's no fun. Better to run the modules AND POstgres in a virtual environment.
### Prerequisites
- conda
- ollama
- GPU drivers to make Ollama hurry up.

### Demo setup
#### Set up your virtual environment.
Make sure any running Postgres instances are stopped.
- Create a new virtual environment using `conda create --name ragdemo`.
- Activate the virtual environment using `conda activate ragdemo`.
- Install the required modules for this demo:
	- psycopg2
	- langchain-community
	- tiktoken
	- pypdf
	- pdfplumber
	- streamlit
	- pillow
	- ollama
	- ollama-python
	- transformers
	- pgvector
	- postgresql-plpython

	If you are working on a Mac, `wxPython`. 

	If you are working on Linux, `tk`. 

When you create a virtual environment using conda, conda will automagically add the correct version of `tk` to the environment. Believe me, you want to use conda. This will save you a lot of hea`tk`ache.

#### Set up Postgres
Conda already installed Postgres when you were installing pgvector and PL/Python, so nothing to install here.

Make sure any existing instances of Postgres are stopped. If you cannot stop those instances, make sure you are running this Postgres on a separate port.
- Create a directory for your database `db`and run `initdb -D db`, then start the database using `pg_ctl -D db -l logfile start`.

Postgres is now running under your OS $USER. Feel free to create a user for this demo. I created the standard user `postgres` for this.
- Connect to your Postgres instance and set up a new database in Postgres using `CREATE DATABASE ragdemo;`
- Connect to this database and icreate the pgvector and PL/Python extensions in using `CREATE EXTENSION vector` and  `CREATE EXTENSION plpython3u`.
- Run the four PL/Ppython scripts from the `pl_python` sub-directory
   	- augmented_response.sql
	- process_files_in_directory.sql
	- process_one_image.sql
	- similar_images.sql

#### Set up ollama
- Pull in the following LLM's into ollama:
	- mxbai-embed-large (`ollama pull mxbai-embed-large`)
	- llama3.1 (`ollama pull llama3.1`)

#### Set up demo scripts
- Change the Postgres username, password and database hostname in `.streamlit/secrets.toml` if needed.

## Demo flow
You are now ready to run the demo.

Run the streamlit application using `streamlit run ragdemo.py`.

## Tips
If you have an Nvidia GPU and the GPU is not detected by ollama you will see this and the enconding will be slow.
```
level=INFO source=gpu.go:199 msg="looking for compatible GPUs"
level=WARN source=gpu.go:562 msg="unknown error initializing cuda driver library" library=/usr/lib/x86_64-linux-gnu/libcuda.so.560.35.03 error="cuda driver library init failure: 999"
level=WARN source=gpu.go:563 msg="see https://github.com/ollama/ollama/blob/main/docs/troubleshooting.md for more information"
level=INFO source=gpu.go:347 msg="no compatible GPUs were discovered"
```
Try to unload and reload the uvm module using `sudo rmmod nvidia_uvmand` and then `sudo modprobe nvidia_uv`. 