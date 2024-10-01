CREATE OR REPLACE FUNCTION process_one_image(
    dataset_name VARCHAR,
    directory_path VARCHAR,
	filename VARCHAR,
	do_truncate BOOL
) RETURNS VOID AS $$

import os
import time
import requests
last_checkpoint_time = time.time()


#***********************************************************
#***********************************************************
#*************Caching Python Libraries**********************
#****************openai/clip-vit-base-patch32 model*********
#***********************************************************

if 'cached_model' not in SD or 'cached_processor' not in SD or 'cached_tokenizer' not in SD or 'cached_device' not in SD:
    try:
        from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
        import torch
        model_id = "openai/clip-vit-base-patch32"
        SD['cached_device'] = "cuda" if torch.cuda.is_available() else "cpu"
        SD['cached_model'] = CLIPModel.from_pretrained(model_id).to(SD['cached_device'])
        SD['cached_tokenizer'] = CLIPTokenizer.from_pretrained(model_id)
        SD['cached_processor'] = CLIPProcessor.from_pretrained(model_id)
        
        plpy.notice("Model 'cached_model, processor, tokenizer' loaded and cached successfully.")
    except Exception as e:
        plpy.error(f"Failed to load model: {str(e)}")

if 'cached_Image' not in SD:
    try:
        from PIL import Image
        SD['cached_image'] = Image
        plpy.notice("Image loaded and cached successfully.")
    except Exception as e:
        plpy.error(f"Failed to load model: {str(e)}")

plpy.notice(f"Objects loading time: {time.time() - last_checkpoint_time:.2f} seconds.")
last_checkpoint_time = time.time()

device = SD['cached_device']
model = SD['cached_model']
processor = SD['cached_processor']
tokenizer = SD ['cached_tokenizer']
Image = SD['cached_image']

if(do_truncate):
	#drop index, table
	plpy.execute(f"""DROP INDEX IF EXISTS {dataset_name}_vector_index;""")	
	plpy.execute(f"""drop table if exists {dataset_name}""")
#create table, index
plpy.execute(f"""create table IF NOT EXISTS {dataset_name} (id bigserial PRIMARY KEY, filepath varchar(1024), filename varchar(1024), embedding vector(512));""")
#if(do_truncate):
plpy.execute(f"""CREATE INDEX if not exists {dataset_name}_vector_index ON {dataset_name} USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 256);""")
plpy.notice(f"table/index drop/create time: {time.time() - last_checkpoint_time:.2f} seconds.")
last_checkpoint_time = time.time()

insert_plan = plpy.prepare(f"""
    INSERT INTO {dataset_name} (embedding, filepath, filename)
    VALUES ($1, $2, $3)
""", ["vector", "text", "text"])

#file_list = os.listdir(directory_path)
#for filename in file_list:
plpy.notice(f"process file name {filename}")
file_path = os.path.join(directory_path, filename)
#if filename.lower().endswith('.pdf'):
try:
	#***********************************************************
	#***********************************************************
	#****************encode image and generate embedding********
	#***********************************************************
	#***********************************************************
	
	#response = requests.get(file_path)
	my_image = Image.open(open(file_path,"rb"))		
	#my_image = Image.open(BytesSIO(response.content)).convert("RGB")
	image = processor(
		text = None,
		images = my_image,
		return_tensors="pt"
		)["pixel_values"].to(device)
	embedding = model.get_image_features(image)
	embedding = embedding.cpu().detach().numpy().tolist()[0]
	#plpy.notice(f"{img_emb}")
	#plpy.notice(type(img_emb))
	plpy.notice(f"image open time: {time.time() - last_checkpoint_time:.2f} seconds.")
	last_checkpoint_time = time.time()			
	try:
		#***********************************************************
		#***********************************************************
		#****************store generated embedding *****************
		#*****************and image reference in pgvector***********
		#***********************************************************
		
		plpy.execute(insert_plan, [embedding, file_path,filename])
	except Exception as e:
		plpy.warning(f"Failed to process image {filename}: {str(e)}")
except Exception as e:
	plpy.warning(f"Failed to process file {filename}: {str(e)}")
plpy.notice(f"image embedding generation and db insertion time: {time.time() - last_checkpoint_time:.2f} seconds.")
last_checkpoint_time = time.time()
plpy.notice(f"Done: {time.time() - last_checkpoint_time:.2f} seconds.")
$$ LANGUAGE plpython3u;