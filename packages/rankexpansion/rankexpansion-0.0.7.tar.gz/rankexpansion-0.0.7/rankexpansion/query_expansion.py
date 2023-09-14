import os
import sys
sys.path.append(os.getcwd())
import openai
from typing import List
from extraction_utils import *
from ranking_system import *

if "OPENAI_API_KEY" in os.environ:
    openai.api_key = os.environ["OPENAI_API_KEY"]
    #for local testing, add the openai api_key to your env
    #otherwise make sure that you set your openai api_key before you use this library

# generate a set of queries similar to the original
def generate_expanded_queries(query: str, num_queries: int = 5) -> List[str]:
    '''The `generate_expanded_queries` function takes a user's search query and generates a list of similar
    queries that are relevant to the original context, such as similar job titles, nearby locations, and
    similar skills.
    
    Parameters
    ----------
    query : str
        The `query` parameter is a string that represents the user's search query. It is the original query
    for which we want to generate similar queries.
    num_queries : int, optional
        The `num_queries` parameter specifies the number of similar queries that should be generated. By
    default, it is set to 5, but you can change it to any positive integer value.
    
    Returns
    -------
        The function `generate_expanded_queries` returns a list of similar queries that are relevant to the
    original query context. The list includes `num_queries` similar queries, as well as the original
    query itself.
    
    '''
    prompt = (
        f"Given a user's search query, generate a list of {num_queries} similar queries that are relevant to the original context [similar job title, nearby location, similar skills].\n\n"
        "Examples:\n"
        "1. Input Query: \"Software engineer in New York\"\n"
        "   [\"Software Development Engineer in New York\", \"Software developer in New York\", \"SDE in Jersey City\" ]\n\n"
        "2. Input Query: \"Remote Data Scientist\"\n"
        "   [\"Remote Data Science Engineer\", \"Work from home Data Scientist\"]\n\n"
        "3. Input Query: \"Entry-level software developer\"\n"
        "   [\"Software engineering intern\", \"Junior software engineer\"]\n\n"
        "4. Input Query: \"Experienced software engineer\"\n"
        "   [\"Senior software engineer\", \"Software Architect\"]\n\n"
        "5. Input Query: \"Software development careers\"\n"
        "   [\"Software engineering job paths\", \"Career options in software development\"]\n\n"
        f"Input Query: \"{query}\"\n"
    )

    
    response = openai.Completion.create(
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=200,
        stop=None,
        temperature=0,
        n=num_queries,
        frequency_penalty=0.5,
        presence_penalty=0.5
    )

    expanded_text = response.choices[0]['text']
    print(expanded_text)

    # Find the start index of the list
    result_list_start = expanded_text.index("[")  

    # Find the end index of the list
    result_list_end = expanded_text.index("]")  

    # extract the result
    result_list_str = expanded_text[result_list_start:result_list_end+1] 
    result_list = eval(result_list_str) 

    # add original query as well
    result_list.append(query)

    return result_list

def generate_mongo_ql_document(employment_dict: dict, education_dict:dict, skill_list:list[str], location_list:list[str]) -> dict:
    '''The function generates a MongoDB query document based on employment, education, skills, and location.
    criteria. The query is an AND query of all the OR queries of possible degrees/job titles/skills etc;
    Example: if candidate_employment_dict ={
        "Institution": ["google","facebook"],
        "Specialization":["engineer", "developer"]
    }
    and candidate_skills_list=["java","python","html"]

    then (in pseudocode) the mongo_ql_document will be generated that finds:

    (WorkExperienceList contains "google" OR "facebook") AND (WorkExperienceList contains "engineer" OR "developer") AND (Skills contains "java" OR "python" OR "html")
    
    Parameters
    ----------
    employment_dict : dict
        The `employment_dict` parameter is a dictionary that contains the fields and values for filtering
    employment experience. Each key in the dictionary represents a field (Institution and/or Specialization) in the employment experience,
    and the corresponding value is a list of values to match for that field.
    education_dict : dict
        The `education_dict` parameter is a dictionary that contains the education criteria for the query.
    Each key in the dictionary represents a field (Institution and/or Specialization and/or Degree) in the education experience, and the corresponding
    value is a list of values to match for that field. 
    skill_list : list[str]
        A list of skills that the candidate should have.
    location_list : list[str]
        A list of locations to filter the candidates by.
    
    Returns
    -------
        a MongoDB query document that can be used to filter documents in a collection based on the provided
    employment, education, skill, and location criteria. calling collection.find(x) where x is the return
    value of this function should work
    
    '''
    and_condition_list=[]
    for field,value_list in employment_dict.items():
        or_condition_list=[]
        for value in value_list:
            or_condition_list.append({'WorkExperienceList.'+field:value.lower()})
        and_condition_list.append({"$or":or_condition_list})
    for field,value_list in education_dict.items():
        or_condition_list=[]
        for value in value_list:
            or_condition_list.append({'EducationExperienceList.'+field:value.lower()})
        and_condition_list.append({"$or":or_condition_list})
    if len(skill_list)>0:
        skill_or_condition_list=[]
        for skill in skill_list:
            skill_or_condition_list.append({"Skills":skill.lower()})
        and_condition_list.append({"$or":skill_or_condition_list})
    if len(location_list)>0:
        location_or_condition_list=[]
        for location in location_list:
            location_or_condition_list.append({"Location":location.lower()})
        and_condition_list.append({"$or":location_or_condition_list})
    return {"$and":and_condition_list}

def infer_similar_job_title_kg(driver, title, max_num=5):
    """
    This function takes a given job title, and return a list of titles that based on the number of matched skills.
    driver: a neo4j python driver for connecting to the graph instance.
    title: the seed job title you want to infer.
    max_num: the max number of similar title you want ot generate.
    """
    query_string = '''MATCH (p:Title {{name: "{title}"}}) -[:Require]->(skills)
                    MATCH (similar) -[r:Require]-> (skills)
                    WHERE p <> similar
                    WITH DISTINCT similar,r
                    RETURN similar.name, COUNT(r)
                    ORDER BY COUNT(r) DESC
                    LIMIT {num}'''.format(title=title,num=max_num)
    records, summary, keys = driver.execute_query(query_string)
    res = [title['similar.name'] for title in records]
    return res


def infer_similar_skill_kg(driver, skill, max_num=5):
    """
    This function takes a given job title, and return a list of titles that based on the number of matched skills.
    driver: a neo4j python driver for connecting to the graph instance.
    skill: the seed skill you want to infer.
    max_num: the max number of similar title you want ot generate.
    """
    query_string = '''MATCH (p:Title) -[:Require]->(skills {name:"{skill}"})
                        MATCH (p) -[r:Require]-> (similar)
                        WHERE skills <> similar
                        WITH DISTINCT similar,r
                        RETURN similar.name, COUNT(r)
                        ORDER BY COUNT(r) DESC
                        LIMIT {num}'''.format(skill=skill, num=max_num)
    records, summary, keys = driver.execute_query(query_string)
    res = [skill['similar.name'] for skill in records]
    return res

def generate_mongo_ql_document_from_query_str(query:str,driver)->dict:
    #given query, we use llm to get similar queries
    #from each of those similar queries, we extract jobs/skills/education
    #for each of the jobs/skills/education we use things like kg or llm to find similar answers
    #then we have the dicts so we just use generate
    expanded_query_list=generate_expanded_queries(query)
    main_employment_dict={}
    main_education_dict={}
    main_location_list=[]
    main_skill_list=[]
    for expanded_query in expanded_query_list:
        print('expanded query', expanded_query)
        employment_dict=extract_employment(expanded_query)
        print("\t", employment_dict)
        education_dict=extract_education(expanded_query)
        print("\t", education_dict)
        location_list=extract_location_mentions_llm(expanded_query)
        print("\t", location_list)
        skill_list=extract_skills(expanded_query)
        print("\t", skill_list)
        for key,value in employment_dict.items():
            if key not in main_employment_dict:
                main_employment_dict[key]=[]
            main_employment_dict[key].extend(x for x in value if x not in main_employment_dict[key])
        for key,value in education_dict.items():
            if key not in main_education_dict:
                main_education_dict[key]=[]
            main_education_dict[key].extend(x for x in value if x not in main_education_dict[key])
        main_location_list.extend(x for x in location_list if x not in main_location_list)
        main_skill_list.extend(x for x in skill_list if x not in main_skill_list)
    
    expanded_location_list=get_expanded_locations_llm(query_locations=main_location_list, max_limit=5)
    main_location_list+=expanded_location_list
    main_location_list=list(set(main_location_list))
    print('main_location_list len',len(main_location_list))
    
    similar_skill_list=[]
    for skill in main_skill_list:
        similar_skill_list+=infer_similar_skill_kg(driver,skill)
    main_skill_list+=similar_skill_list
    main_skill_list=list(set(main_skill_list))
    print('main_skill_list len',len(main_skill_list))
    
    similar_title_list=[]
    for title in main_employment_dict["Specialization"]:
        similar_title_list+=infer_similar_job_title_kg(driver,title)
    main_employment_dict["Specialization"]+=similar_title_list
    #main_employment_dict["Specialization"].extend(t for t in similar_title_list if t not in main_employment_dict["Specialization"])
    main_employment_dict["Specialization"]=list(set(main_employment_dict["Specialization"]))
    print('main_employment_dict', len(main_employment_dict["Specialization"]))
    return generate_mongo_ql_document(main_employment_dict, main_education_dict, main_skill_list, main_location_list)