# pgvector_usecases 
![Short videos for the pgvector use cases files rag and image similarity search.](https://github.com/TamerAElhity/pgvector_usecases/blob/main/pgvecotr_usecases.gif)
## Prerequisites
1. Postgres
   - create a database and install pgvector and PL/Python extensions
   - run four pl python scripts, you may find these scripts under pl_python sub-directory
     - augmented_response.sql
	 - process_files_in_directory.sql
	 - process_one_image.sql
	 - similar_images.sql
2. python 3
3. pip
4. psycopg2 (https://pypi.org/project/psycopg2/)
5. langchain (https://pypi.org/project/langchain/)
6. langchain_text_splitters (https://pypi.org/project/langchain-text-splitters/)
7. tiktoken (https://pypi.org/project/tiktoken/)
8. wxPython (https://www.wxpython.org/pages/downloads/)
   - this should fix the file upload problem on mac
9. pillow (https://pypi.org/project/pillow/)
10. streamlit (https://docs.streamlit.io/get-started/installation)
11. ollama
   - Ollama Python Library (https://pypi.org/project/ollama/)
   - ollama service (https://ollama.com/download and/or https://github.com/ollama/ollama)
   - models to pull 
     - mxbai-embed-large (command line to execute on ollama cli: ollama pull mxbai-embed-large)
	 - llama3.1 (command line to execute on ollama cli: ollama pull llama3.1) 
12. Give postgres service or user folder access permission on the directory from which you are running the streamlit python file
13. "openai/clip-vit-base-patch32" transformers (https://huggingface.co/docs/transformers/installation)

 
## Database configuration for streamlit
you may adjust database configuration (database name, port, username, password) in ".streamlit/secrets.toml" file

## Run the application
streamlit run pgvector_usecases.py

