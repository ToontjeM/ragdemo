CREATE OR REPLACE FUNCTION public.similar_images(
	dataset_name character varying,
	image_path character varying,
	is_image BOOL)
    RETURNS text AS $$

import os
import time
import json


#***********************************************************
#***********************************************************
#*************Caching Python Libraries**********************
#****************openai/clip-vit-base-patch32 model*********
#***********************************************************

last_checkpoint_time=time.time()
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

#***********************************************************
#***********************************************************
#*******PGVector SQL statement to find similarities*********
#***********************************************************
#***********************************************************

plan = plpy.prepare(f"""
		SELECT id, filepath, 1-(embedding <=> $1) AS DIST
			FROM {dataset_name}
			WHERE (1-(embedding <=> $1)) > 0.2
			ORDER BY DIST DESC;
			""", ["vector"])
#WHERE (1-(embedding <=> $1)) > 0.1
#<#>
#<+>
# get image embedding and search for similar records
emb=''
emb_np=''

if is_image:

	#***********************************************************
	#*************user is searching by image********************
	#****************encode image and generate embedding********
	#***********************************************************
	#***********************************************************
	
	my_image = Image.open(open(image_path,"rb"))		
	#my_image = Image.open(BytesIO(response.content)).convert("RGB")
	image = processor(
		text = None,
		images = my_image,
		return_tensors="pt"
		)["pixel_values"].to(device)
	emb = model.get_image_features(image)
	emb = emb.cpu().detach().numpy().tolist()[0]
else:
	#***********************************************************
	#*************user is searching by text*********************
	#****************encode text and generate embedding*********
	#***********************************************************
	#***********************************************************
	
	inputs = tokenizer(image_path, return_tensors = "pt")
	plpy.notice("inputs")
	plpy.notice(inputs)
	emb = model.get_text_features(**inputs)
	emb = emb.cpu().detach().numpy().tolist()[0]
#plpy.notice("emb")
plpy.notice(emb)
llm_time = f"{time.time() - last_checkpoint_time:.2f}"
#***********************************************************
#***********************************************************
#*************pgvector query using the *********************
#****************generated embeeding************************
#***********************************************************
rv = plpy.execute(plan,[emb],10)

query_result={}
generated_result=''

#concatenate the similar chunks
for row in rv:
	query_result[row['filepath']]=row['dist']
plpy.notice(f"row fetching loading time: {time.time() - last_checkpoint_time:.2f} seconds.")
pg_time = f"{time.time() - last_checkpoint_time:.2f}"
last_checkpoint_time = time.time()

resp = {}
resp['llm_response'] = query_result
resp['pg_time'] = pg_time
resp['llm_time'] = llm_time

return json.dumps(resp)
$$ LANGUAGE plpython3u;
