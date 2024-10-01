import streamlit as st
import sys
import os
import io
import datetime
import time
import json
import wx
import math

import psycopg2
import ollama
from PIL import Image
image_path="logo.png"
icon = Image.open('logo.png')
st.set_page_config(page_title="RAG Upload",page_icon=icon,layout="wide",)
st.logo(icon, link="https://www.enterprisedb.com/")
#hide_decoration_bar_style = '''
#    <style>
#        header {visibility: hidden;}
#    </style>
#'''
#st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


st.markdown(
        """
    <style>
        .st-emotion-cache-1c7y2kd {
            flex-direction: row-reverse;
            text-align: right;
        }
        .block-container {padding: 50px 0px 0px 0px}
        .st-emotion-cache-ocqkz7 {gap:10}
        .st-emotion-cache-1sdqqxz {padding: 0px 0px 0px 10px}
        .stTabs {padding: 0px 10px 0px 10px}
        .st-emotion-cache-1wmy9hl {padding: 0px}  
        [data-testid="stMarkdownContainer"] {padding: 4px 4px 4px 8px} 
        [data-testid="stNotification"] {padding: 4px 4px 4px 8px} 
        [data-testid="stAlert"] {padding: 4px 4px 4px 8px}
        [data-testid="stAlertDynamicIcon"] {padding: 4px 0px 0px 8px}
        .st-emotion-cache-mnxcop {gap:5px}
        .st-emotion-cache-1voybx5 {background-color:white}
    </style>
    """,
        unsafe_allow_html=True,
    )
#'''
#    <style>
#        .st-emotion-cache-1c7y2kd {
#            flex-direction: row-reverse;
#            text-align: right;
#        }
#        //.main {overflow:visible}
#        .block-container {padding: 30px 0px 0px 0px}
#        .st-emotion-cache-j5r0tf {background-color:black}
#        .st-emotion-cache-ocqkz7 {gap:10} //style for buttons
#        //.st-emotion-cache-1sdqqxz {padding: 0px 0px 0px 10px}
#        .stTabs {padding: 0px 10px 0px 10px}
#        //.st-emotion-cache-1wmy9hl {padding: 0px 10}  //top right bottom left
#        
#        [data-testid="stMarkdownContainer"] {padding: 5px 5px 5px 5px} //notification
#        [data-testid="stNotification"] {padding: 5px 5px 5px 10px} //notification
#    </style>
#    '''
def db_connect(_force):
    if _force and 'conn' in st.session_state and st.session_state['conn'].closed==0:
        st.session_state['conn'].close()
    if _force or 'conn' not in st.session_state or st.session_state['conn'].closed ==1:
        st.session_state['conn'] = psycopg2.connect(user=st.secrets["database"]["user"],password=st.secrets["database"]["password"],host=st.session_state['db_ip'],port=st.secrets["database"]["port"],database=st.secrets["database"]["pgvector_db_name"])
    return st.session_state['conn']

def datasets():    
    options=[]
    #options.append('--select dataset --')
    try:
        with db_connect(False).cursor() as cur:        
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            for row in cur.fetchall():
                options.append(row[0])
            cur.close()
        if len(options)>0:
            options.insert(0,"")
    except:
        db_connect(True)
    return options  
def ollama_models():
    options=[]
    ollamamodels = ollama.list()
    for model in ollamamodels['models']:
        if model['details']['quantization_level']!="F16" :
            options.append(model['model'])
    if len(options)>0:
        options.insert(0,"")
    #st.sidebar.write("llama3:8b")
    #st.sidebar.write("llama2:latest")
    #st.sidebar.write("llava-llama3:latest")
    
    #st.sidebar.write("mistral:latest")
    #st.sidebar.write("llama3:latest")
    return options
    
def show_filedialog():
    #root = tk.Tk()
    #root.withdraw()        
    ## Make folder picker dialog appear on top of other windows
    #root.wm_attributes('-topmost', 1)
    #return filedialog.askdirectory(master=root) # st.text_input('Selected folder:', 

    
    if "wx_app" not in st.session_state:
        st.session_state.wx_app = wx.App()
        wx.DisableAsserts()
    path=""
    if wx.Platform == '__WXMSW__':
        path = os.getenv("USERPROFILE")
    else:
        path = os.getenv("HOME")
    dialog=None
    folder_path=None
    dialog = wx.DirDialog(None, "Select a folder:",path, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST )
    
    if dialog!=None and dialog.ShowModal() == wx.ID_OK:
        folder_path = dialog.GetPath() # folder_path will contain the path of the folder you have selected as string
    dialog.Destroy()
    del dialog
    #del app
    #del app
    
    
    
    
    
    
    
    
    
    
    
    return folder_path


def get_augemented_answer(_selected_dataset,_user_question,_selected_model,_question_to_model):
    _response=''
    query_text = f"PG Query --> :green[select augmented_response('{_selected_dataset}','{_user_question.strip()}','{_selected_model}',{_question_to_model})]"
    
    with db_connect(False).cursor() as cur:
        time0 = time.time()
        cur.execute(f"select augmented_response ('{_selected_dataset}','{_user_question.strip()}','{_selected_model}',{_question_to_model})")
        
        time1=time.time()
        for row in cur.fetchall():
            row_json = json.loads(row[0])
            _response = f"{row_json['llm_response']} \n\n :red[{_selected_model} total time : {time1-time0:.2f} sec [ LLM time {row_json['llm_time']}, PG time {row_json['pg_time']}, Chunk Count {row_json['chunk_count']}]]"
        cur.close()
    db_connect(False).close()
    return _response,query_text


def get_similar_images(_selected_dataset,_user_question,is_image):
    _response=''
    query_text = f"PG Query --> :green[select similar_images('{_selected_dataset}','{_user_question.strip()}',{is_image})]"
    
    with db_connect(False).cursor() as cur:
        time0 = time.time()
        cur.execute(f"select similar_images ('{_selected_dataset}','{_user_question.strip()}',{is_image})")
        
        time1=time.time()
        result = ""
        for row in cur.fetchall():
            row_json = json.loads(row[0])
            _response = f"{row_json['llm_response']} \n\n total time : {time1-time0:.2f} sec [ LLM time {row_json['llm_time']}, PG time {row_json['pg_time']})]]"
            result = row_json['llm_response']
        cur.close()
    db_connect(False).close()
    return _response, result,query_text


def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

def show_db_ip(container_,key):
    db_ip = container_.text_input(key, 'localhost',label_visibility="collapsed",key=key, placeholder ="Choose a Postgres db")
    
    if not db_ip:
        container_.error(f"Please choose PG database server", icon="⚠️")
    if 'db_ip' not in st.session_state:
        st.session_state['db_ip'] = db_ip
        db_connect(True)  
                
    if st.session_state['db_ip'] != db_ip:
        st.session_state['db_ip'] = db_ip
        db_connect(True)
    return db_ip

def show_selectbox(container_,key,options, placeholder, validate=True):
    selected_dataset = container_.selectbox(key,options,key=key,label_visibility="collapsed",index=None, placeholder=placeholder)
    if not selected_dataset and validate:
        container_.error(f"Please {placeholder}", icon="⚠️")
    return selected_dataset

def show_image_result(container_, result):
    c = container_.container()
    col=[0,0,0]
    col[0],col[1],col[2] = c.columns(3)
    i=0
    for img in result:
        col[i%3].image(img,width=200)
        col[i%3].write(result[img])
        i=i+1   
tab1, tab2, tab3, tab4 = st.tabs(["Vectorize Documents", "RAG Documents", "Vectorize Images", "Search Images"])
with tab1:
    db_ip=show_db_ip(tab1,"db_ip_upload_files")
    existing_dataset_name = show_selectbox(tab1,"select_dataset_files_upload",datasets(),"Choose a dataset",False)
    new_dataset_name = st.text_input(", or new dataset",key="new_dataset_upload_files",placeholder="New Dataset name",label_visibility="collapsed")
    
    dataset_name=None
    if existing_dataset_name:
        dataset_name = existing_dataset_name
    elif new_dataset_name:
        dataset_name = new_dataset_name
    else:
        st.error("Please select either existing or new dataset name")            
    
    if dataset_name:
        truncate = st.checkbox('Truncate',key="truncate_update_rag_files")  
        if st.button('Select a folder', key="select_folder_upload_rag_files"): 
            dirname = show_filedialog()
            if dirname!= None and dirname.strip() != "" :    
                with st.spinner(f"processing files from {dirname}..."): 
                    st.write(f"PG query \n\n :green[select process_files_in_directory ('{dataset_name}','{dirname}',{truncate})]")
                    time0=time.time()
                    with db_connect(False).cursor() as cur:
                        cur.execute(f"select process_files_in_directory ('{dataset_name}','{dirname}',{truncate})")
                        st.write(f"processing directory {dirname} time {time.time()-time0:.2f}")                          
                        cur.close()
                        #conn.close()
                        db_connect(False).commit()
                        st.success("Done!")

with tab2:
    sec1,sec2 = st.columns([.2,.8])    
    db_ip = show_db_ip(sec1,"db_ip_rag_files")
        
    if "messages_rag" not in st.session_state:
        st.session_state.messages_rag = []  
        
    selected_dataset = show_selectbox(sec1,"select_dataset_rag",datasets(),"Choose a dataset",)
    selected_model = show_selectbox(sec1,"select_dataset_rag_ollama",ollama_models(),"Choose a LLM model", )    
    sec1.write(f":green[*gemma2:2b , *llama3.1:latest]")
    
    if db_connect(False).closed==0 and selected_dataset and selected_model:   
        # Accept user input
        workspace = sec2.container(height=None)
        with workspace:
            question_to_model = False
            #question_to_model = col4.checkbox('Question to the model')
            
            history = st.container(height=550,border=True)
            #st.sidebar.write(len(st.session_state.messages_rag))
            for message in st.session_state.messages_rag:
                with history.chat_message(message["role"]):
                    st.write(message["content"])
            if user_question := st.chat_input("What's on your mind?",key="chat_input_rag"):
                with history.chat_message("user"):                               
                    # Display user message in chat message container
                    st.write(user_question)   
                    # Add user message to chat history
                    st.session_state.messages_rag.append({"role": "user", "content": user_question})              
                with history.chat_message("assistant"):
                    with st.spinner('Searching the local knowledgebase ...'):
                        response,query_text = get_augemented_answer(selected_dataset,user_question,selected_model,question_to_model)                    
                    # Display postgres response message in chat message container
                    st.write_stream(stream_data(response))
                    # Add assistant message to chat history
                    st.session_state.messages_rag.append({"role": "assistant", "content": response}) 
with tab3:
    existing_dataset_name = show_selectbox(tab3,"select_dataset_image_upload",datasets(),"Choose a dataset",False)
    new_dataset_name = st.text_input(", or new dataset",key="new_dataset_upload_image",placeholder="New Dataset name",label_visibility="collapsed")
    
    dataset_name=None
    if existing_dataset_name:
        dataset_name = existing_dataset_name
    elif new_dataset_name:
        dataset_name = new_dataset_name
    else:
        st.error("Please select either existing or new dataset name")    
    
    if dataset_name:
        truncate = False #st.checkbox('Truncate',key="truncate_update_images")  
        if st.button('Select a folder', key="select_folder_upload_images"): 
            dirname = show_filedialog()
            if dirname!= None and dirname.strip() != "" :    
                #with st.spinner(f"processing files from {dirname}..."): 
                progress_bar = st.progress(0, f"processing files in {dirname}")
                with progress_bar:
                    file_list = os.listdir(dirname)   
                    #st.write(len(file_list))
                    #st.stop()
                    index=0
                    conn = db_connect(True)
                    conn.autocommit = False
                    cur = conn.cursor()                
                    for filename in file_list:
                        progress_bar.progress(math.floor(100*index/len(file_list)),f"processing {filename} {index}/{len(file_list)} ({math.floor(100*index/len(file_list))/100}) :green[select process_one_image  ('{dataset_name}','{dirname}','{filename}',{truncate})]")
                        time0=time.time()
                        
                        cur.execute(f"select process_one_image  ('{dataset_name}','{dirname}','{filename}',{truncate})")
                        st.write(f"processing file {dirname} time {time.time()-time0:.2f}")
                        
                        if index % 100 == 0:
                            progress_bar.progress(math.floor(100*index/len(file_list))/100,f"committing {index} files")
                            conn.commit()
                        index=index+1
                    cur.close()
                    st.success("Done!")
                    
                conn.commit()
with tab4:
    sec1,sec2 = st.columns([.2,.8])    
    db_ip = show_db_ip(sec1,"db_ip_search_images")
        
    selected_dataset = show_selectbox(sec1,"select_dataset_images_search",datasets(),"Choose a dataset",)
    
    if "messages_search_images" not in st.session_state:
        st.session_state.messages_search_images = []  

  

    if db_connect(False).closed == 0 and selected_dataset:
        # Accept user input
        with sec2.container(height=None):
            question_to_model = False
            #question_to_model = col4.checkbox('Question to the model')
            
            history = st.container(height=500,border=True)
            search_c1, search_c2 = st.columns([.65,.35])
            user_question = search_c1.chat_input("What's on your mind?")
            search_image = search_c2.file_uploader("search by image", key="search_by_image",label_visibility="collapsed")
            
            for message in st.session_state.messages_search_images:
                if message["role"] == "user":
                    with history.chat_message("user"):
                        if message["type"] == "text":
                            history.chat_message("user").write(message["content"])
                        else:
                            history.chat_message("user").image(message["content"],width=200)
                else:
                    with history.chat_message("assistant"):
                        show_image_result(history.chat_message("assistant"),message["content"])
            
            # Accept user input
            #temp_file_path = "_st_search_image.png"#os.path.join(tempfile.gettempdir(), "_st_search_image.png")
            file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "_st_search_image.png")
            if user_question or search_image:
                with history.chat_message("user"):                               
                    # Display user message in chat message container
                    if isinstance(user_question,str) == False and search_image is not None:
                        img = Image.open(io.BytesIO(search_image.getvalue()))
                        #img.save("_st_search_image.png")  
                        img.save(file_path)                
                        #st.write(file_path)
                        c = st.container()
                        c1,c2 = c.columns(2)
                        c1.image(img,width=200)
                        c2.write("Get similar images")
                        st.session_state.messages_search_images.append({"role": "user", "content": img, "type":"image"})
                    elif isinstance(user_question,str) and user_question.strip !="":
                        st.write(user_question)   
                        st.session_state.messages_search_images.append({"role": "user", "content": user_question, "type":"text"})
                with history.chat_message("assistant"):
                    result={}
                    response = ""
                    with st.spinner('Searching the local knowledgebase ...'):
                        if isinstance(user_question,str) == False and search_image is not None:
                            response, result,query = get_similar_images(selected_dataset,file_path,True)
                        elif isinstance(user_question,str) and user_question.strip !="":
                            response, result,query = get_similar_images(selected_dataset,user_question,False)
                    show_image_result(st,result)
                    st.session_state.messages_search_images.append({"role": "assistant", "content": result}) 