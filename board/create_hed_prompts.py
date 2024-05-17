# from datasets import Dataset
import pandas as pd
import requests
from io import StringIO
from bs4 import BeautifulSoup
import os
        
def create_examples():
    HED = [
        "(Visual-presentation,(Background-view,Black),(Foreground-view,((Center-of,Computer-screen),(Cross,White)),(Grayscale,(Face,Hair,Image))))",
        "(Foreground-view, ((Item-count, High), Ingestible-object)), (Background-view, ((Human, Body, Agent-trait/Adult), Outdoors, Furnishing, Natural-feature/Sky, Urban, Man-made-object))"
    ]

    description = [
        "The visual presentation has a black background view. In its foreground view, the center is associated with a computer screen and there's a white cross. There's also a grayscale element that includes features like a face, hair, and an image.",
        ""
    ]

    return {"HED": HED, "description": description}

# def create_hugging_dataset():
#     df = get_examples_from_github()
#     examples_dict = df.to_dict(orient='list')
#     return Dataset.from_dict(examples_dict)

def create_instructions():
    '''
    Create a list of intruction options in tuples of (<instruction>, <query>)
    '''
    options = [
        ("Translate the following tagging into sentences assuming that parentheses mean association:", "Translation:"),
        ("The following tagging give short hand annotations with parentheses grouping related concepts together:", "Convert the tagging into full sentences:")
    ]
    for idx, option in enumerate(options):
        print(f'''Option {idx}:\n\tInstruction: "{option[0]}"\n\tQuery: "{option[1]}"\n\n''')
    return options

def get_examples_from_github():
    endpoint = "https://raw.githubusercontent.com/dungscout96/HED-LLM/main/examples.tsv"
    result = requests.get(endpoint)
    return pd.read_csv(StringIO(result.text), sep="\t")

def examples_to_tsv():
    # examples_dict = create_examples()
    examples_dict = get_examples_from_github().to_dict()
    df = pd.DataFrame.from_dict(examples_dict)
    with open('examples.tsv', 'w') as fout:
        df.to_csv(fout, index=False, sep='\t')

def make_prompt(dataset, example_indices_full, example_index_to_translate, instruction, query):
    prompt = ''
    for index in example_indices_full:
        hed = dataset[index]['HED']
        desc = dataset[index]['description']
        
        # The stop sequence '{summary}\n\n\n' is important for FLAN-T5. Other models may have their own preferred stop sequence.
        prompt += f"""
{instruction}

{hed}

{query}
{desc}


"""
    
    hed = dataset[example_index_to_translate]['HED']
    
    prompt += f"""
{instruction}

{hed}

{query}
"""
        
    return prompt

def get_hed_vocab():
    if os.path.exists('HEDLatest_terms'):
        with open('HEDLatest_terms', 'r') as fin:
            return fin.read()
    else:
        # URL of the XML file
        url = "https://raw.githubusercontent.com/hed-standard/hed-schemas/main/standard_schema/hedxml/HEDLatest.xml"
        
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the XML content
            xml_content = response.text
            soup = BeautifulSoup(xml_content, "lxml")
        
            # Find all nodes and extract their names
            all_nodes = soup.find_all('node')
            node_names = [node.find('name', recursive=False).string for node in all_nodes]
        
            return ','.join(node_names)
        else:
            print(f"Failed to retrieve data from the URL. Status code: {response.status_code}")

def get_coco_hed():
    url = "https://raw.githubusercontent.com/MultimodalNeuroimagingLab/nsd_hed_labels/main/shared1000_HED.tsv"
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the XML content
        tsv_table = response.text
        df = pd.read_csv(StringIO(tsv_table), sep="\t")
        return df
    else:
        return print(f"Failed to retrieve data from the URL. Status code: {response.status_code}")
        
if __name__ == "__main__":
    # examples_to_tsv()
    get_coco_hed_annotations()
