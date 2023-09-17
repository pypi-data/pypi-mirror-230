import os
import sys
sys.path.append(os.getcwd())

from sentence_transformers import SentenceTransformer
from typing import List
import json
import spacy.cli
spacy.cli.download("en_core_web_sm")
import spacy

import openai

from geopy.geocoders import Nominatim

# Initialize the geocoder
geolocator = Nominatim(user_agent="location_expansion")

if "OPENAI_API_KEY" in os.environ:
    openai.api_key = os.environ["OPENAI_API_KEY"]

# Load the Sentence Transformers model for text embedding
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')

# Load spaCy's English language model
nlp_spacy = spacy.load("en_core_web_sm")

def extract_skills(query: str) -> List[str]:
    '''The function `extract_skills` takes a query as input and uses text-davinci-003 language model to extract the
    skills mentioned in the query.
    
    Parameters
    ----------
    query : str
        The `query` parameter is a string that represents the query from which we want to extract skills.
    It should be a sentence or a phrase that mentions the skills we are interested in. For example,
    "Looking for candidates with programming and data analysis skills"
    
    Returns
    -------
        returns a list of skills extracted from the given query.
    
    '''
    prompt = (
        f"You are a language model that can extract skills from queries. Please provide the list of skills mentioned in the following queries.\n\n"
        "Examples:\n"
        "1. Query: \"Looking for candidates with programming and data analysis skills\"\n"
        "   Skills: [\"programming\", \"data analysis\"]\n\n"
        "2. Query: \"Searching for profiles with communication and leadership abilities\"\n"
        "   Skills: [\"communication\", \"leadership\"]\n\n"
        "3. Query: \"Find candidates experienced in project management and teamwork\"\n"
        "   Skills: [\"project management\", \"teamwork\"]\n\n"
        f"Query: \"{query}\""
    )

    # Use the appropriate engine - cheapest preferred
    # max_tokens can be adjusted as needed
    response = openai.Completion.create(
        temperature=0,
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=50,  
        stop=None  
    )

    extracted_text = response.choices[0].text
    start_index = extracted_text.find("[\"")
    end_index = extracted_text.find("\"]")
    extracted_skills = extracted_text[start_index + 2:end_index].split("\", \"")
    
    return [s.lower() for s in extracted_skills]
    

def extract_education(query:str)->dict:
    '''The function `extract_education` takes a query as input and extracts the education information
    mentioned in the query, returning it as a dictionary. 
        {"Degree":["degree_0",,,"degree_n"], 
        "Specialization":["major_0",,,"major_n"],
        "Institution": ["school_0",,,"school_n"],
        }
        If it doesn't find a mention of a degree/major/school then instead of an empty list for that value,
        the key will just not be in the dict.
    
    Parameters
    ----------
    query : str
        The query parameter is a string that represents the query for which you want to extract education
    information.
    
    Returns
    -------
        The function `extract_education` returns a dictionary containing the extracted education
    information from the given query.
    
    '''
    prompt=(
        "Examples:\n"
        "1. Query: \"Looking for candidates with a phd in history\"\n"
        "Education: \{\"Degree\": [\"phd\"], \"Specialization\": [\"history\"]\}\n\n"
        "2. Query: \"Searching for profiles with a major in computer science from harvard or yale\""
        "Education: \{\"Specialization\": [\"computer science\"], \"Institution\": [\"harvard\",\"yale\"]\}\n\n"
        "3. Query: \"Find people who have a masters in statistics, math or finance from new york university or university of chicago\""
        "Education: \{\"Degree\": [\"masters\"],\"Specialization\": [\"statistics\",\"math\",\"finance\"], \"Institution\": [\"new york university\",\"university of chicago\"]\}\n\n"
        "4. Query: \"Get me someone who attended princeton university\""
        "Education: \{\"Institution\": [\"princeton university\"]\}\n\n"
        "5. Query: \"Hello\""
        "Education: \{\}\n\n"
        "6. Query: \"Looking for candidates with a degree in history\"\n"
        "Education: \{\"Specialization\": [\"history\"]\}\n\n"
    f"Query: \"{query}\"")

    response = openai.Completion.create(
        temperature=0,
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=75,  
        stop=None  
    )

    extracted_text = response.choices[0].text.strip()
    try:
        education_dict= json.loads(extracted_text[len("Education: "):].replace("\\",""))
        if "Degree" in education_dict:
            education_dict["Degree"]=[v for v in education_dict['Degree'] if v not in ['degree', 'Degree']]
        education_dict={
            k:[word.lower() for word in v] for k,v in education_dict.items() if len(v)>0 and k in ["Institution", "Specialization", "Degree"]
        }
        return education_dict
    except json.decoder.JSONDecodeError as error:
        raise json.decoder.JSONDecodeError(error.msg+f" could not parse {extracted_text}",doc=error.doc, pos=error.pos)

def extract_employment(query:str)->dict:
    prompt=(
        f"You are a language model that can job descriptions from queries. Please provide the list of jobs mentioned in the following queries.\n\n"
        "Examples:\n"
        "1. Query: \"Looking for candidates who are carpenters\"\n"
        "Employment: \{\"Specialization\":[\"carpenter\"]\}\n\n"
        "2. Query: \"Looking for software engineers or data scientists\"\n"
        "Employment: \{\"Specialization\":[\"software engineer\", \"data scientist\"]\}\n\n"
        "3. Query: \"find me someone who worked at microsoft, google or facebook\"\n"
        "Employment: \{\"Institution\":[\"microsoft\", \"google\", \"facebook\"]\}\n\n"
        "4. Query: \"find me a vice president at jp morgan or wells fargo\"\n"
        "Employment: \{\"Institution\":[\"jp morgan\", \"wells fargo\"], \"Specialization\":[\"vice president\"]\}\n\n"
        "5. Query: \"Hello\""
        "Employment: \{\}\n\n"
        f"Query: \"{query}\""
    )

    response = openai.Completion.create(
        temperature=0,
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=75,  
        stop=None  
    )
    extracted_text = response.choices[0].text.strip()
    try:
        employment_dict= json.loads(extracted_text[len("Employment: "):].replace("\\",""))
        employment_dict={
            k:[word.lower() for word in v] for k,v in employment_dict.items() if len(v)>0 and k in ['Institution', 'Specialization']
        }
        return employment_dict
    except json.decoder.JSONDecodeError as error:
        raise json.decoder.JSONDecodeError(error.msg+f" could not parse {extracted_text}",doc=error.doc, pos=error.pos)

# Location extraction to extract locations from the query
# spaCy has GPE tags
# However spacy cannot resolve location names in case of typos
def extract_location_mentions_spacy(query: str) -> List[str]:
    locations = []
    doc = nlp_spacy(query)
    for entity in doc.ents:
        # "GPE" represents geopolitical entities (locations)
        if entity.label_ == "GPE":  
            locations.append(entity.text)

    return locations


# Location extraction using openai
# This function can take care of typos
def extract_location_mentions_llm(query: str) -> List[str]:

    # prompt should be passed in as a parameter to this function
    prompt = (
        "You are a language model that can extract location mentions from queries. Please provide the list of locations mentioned in the following queries. Take care of typos\n\n" 
        "Examples:\n"
        "1. Query: \"Find me 3 candidates in New York City and Los Angles who are Software Engineers\"\n"
        "   Locations: [\"New York City\", \"Los Angeles\"]\n\n"
        "2. Query: \"I'm looking for candidates from London with programming skills\"\n"
        "   Locations: [\"London\"]\n\n"
        "3. Query: \"Search for profiles in San Francsco with marketing experience\"\n"
        "   Locations: [\"San Francisco\"]\n\n"
        f"Query: \"{query}\""
    )
    
    # Use the appropriate LLM model - the cheapest
    # Set the desired max tokens
    # Don't set any stop sequence
    response = openai.Completion.create(
        temperature=0,
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=100,  
        stop=None  
    )

    # Extract the list of locations mentioned from the model's response
    output_lines = response.choices[0].text.strip().split("\n")
    extracted_locations = []
    for line in output_lines:
        if line.startswith("Locations: ["):
            locations_str = line.split(":")[1].strip()
            locations_list = [loc.strip('" ') for loc in locations_str.strip("[]").split(",")]
            extracted_locations.extend(locations_list)
    return [word.lower() for word in extracted_locations]