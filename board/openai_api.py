from openai import OpenAI
import os
# import pandas as pd
# import subprocess
import argparse

client = OpenAI()
# openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openaikey():
    return os.getenv("OPENAI_API_KEY")
    
def train(model):
	dataset_jsonl = './hed_dataset_openai_cli_nodef_prepared.jsonl'
	# dataset = pd.read_json(dataset_jsonl, orient='records', lines=True)
	
	# validate training dataset
	os.system(f"openai tools fine_tunes.prepare_data -f {dataset_jsonl}")
	
	# train model
	os.system(f"openai api fine_tunes.create -t {dataset_jsonl} -m {model}")

	# check training status
	# os.system("openai api fine_tunes.follow -i ft-H5XbCckrFlxpWietUammyGdV")

def to_hed(desc):
	print(f"Event description prompt: {desc}")
	prompt = desc + '->'
	res = client.chat.completions.create(
		model='davinci:ft-sccn:hed-nodef-2023-08-15-07-32-36',
		prompt=prompt)
	return res.choices[0].message

def prompt_engineer(messages, model):
	response = client.chat.completions.create(
		model=model,
		messages=messages
	)
	return response.choices[0].message.content 
    
if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="Finetune OpenAI model for HED translation"
	)
	parser.add_argument(
		"--train",
		required=False,
		help="Finetune a new model",
		action='store_true'
	)
	parser.add_argument(
		"--model",
		required=False,
		help="OpenAI model to finetune",
		default="ada"
	)
	parser.add_argument(
		"--input",
		required=False,
		help="Event text description to convert to HED tags"
	)

	args = parser.parse_args()
	desc = args.input
	is_train = args.train
	model = args.model

	if is_train:
		train(model)
	else:
		resp = to_hed(desc)
		print(resp)
