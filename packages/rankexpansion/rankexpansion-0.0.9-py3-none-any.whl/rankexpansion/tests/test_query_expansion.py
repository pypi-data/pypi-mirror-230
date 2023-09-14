import os
import sys
sys.path.append(os.getcwd())
from query_expansion import *
import unittest
from mongomock import MongoClient
import pymongo
import pprint
from searchdatamodels import *
from fastapi.encoders import jsonable_encoder
from unittest.mock import patch

INSTITUTION='Institution'
SPECIALIZATION="Specialization"

class QueryTest(unittest.TestCase):
    def test_generate_expanded_queries(self):
        user_query="fashion designer in paris"
        expanded_queries=generate_expanded_queries(user_query,5)
        print(expanded_queries)
        self.assertEqual(6, len(expanded_queries))

    def test_generate_expanded_queries_original(self):
        user_query = "data scientist in london"
        expanded_queries = generate_expanded_queries(user_query, 3)
        self.assertIn(user_query, expanded_queries)

    def test_generate_expanded_queries_unique(self):
        user_query = "civil engineer in berlin"
        expanded_queries = generate_expanded_queries(user_query, 4)
        self.assertEqual(len(expanded_queries), len(set(expanded_queries)))

class GenerateMongoQLTest(unittest.TestCase):
    def setUp(self):
        good_company_0="New York Times"
        good_company_1="washington post"
        good_role_0="editor"
        good_role_1="journalist"
        good_name="clark kent"
        good_school_0="kansas state university"
        good_school_1="university of kansas"
        good_major_0='english'
        good_major_1='history'
        good_location_0="manhattan"
        good_location_1="topeka"
        good_skill_0='photography'
        good_skill_1="interviewing"
        self.skill_list=[good_skill_0, good_skill_1]
        self.employment_dict={INSTITUTION:[good_company_0, good_company_1], SPECIALIZATION: [good_role_0, good_role_1]}
        self.education_dict={INSTITUTION: [good_school_0, good_school_1], SPECIALIZATION: [good_major_0, good_major_1]}
        self.location_list=[good_location_0, good_location_1]
        self.good_candidate=Candidate(Name=good_name, 
                                      WorkExperienceList=[WorkExperience(Institution=good_company_0, Specialization=good_role_0)],
                                      EducationExperienceList=[EducationExperience(Institution=good_school_0, Specialization=good_major_0)],
                                      Skills=self.skill_list, Location=good_location_0)
        self.collection=MongoClient().db.collection
        self.good_candidate_id=self.collection.insert_one(jsonable_encoder(self.good_candidate)).inserted_id
        self.query_str=f"{good_role_1} at {good_company_0} with a degree in {good_major_0} from {good_school_0} skilled in {good_skill_0}"


    def test_generate_mongo_ql_document_employment(self):
        mongo_document=generate_mongo_ql_document(self.employment_dict,{},[],[])
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    def test_generate_mongo_ql_document_employment_case_insensitive(self):
        mongo_document=generate_mongo_ql_document({INSTITUTION:['NEW YORK TIMES']},{},[],[])
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    def test_generate_mongo_ql_document_education(self):
        mongo_document=generate_mongo_ql_document({}, self.education_dict,[],[])
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    def test_generate_mongo_ql_document_education_case_insensitive(self):
        mongo_document=generate_mongo_ql_document({}, {INSTITUTION:["kansas state university".upper()] },[],[])
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    def test_generate_mongo_ql_document_skills(self):
        mongo_document=generate_mongo_ql_document({},{},self.skill_list,[])
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    def test_generate_mongo_ql_document_skills_case_insensitive(self):
        mongo_document=generate_mongo_ql_document({},{},["interviewing".upper()],[])
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    def test_generate_mongo_ql_document_locations(self):
        mongo_document=generate_mongo_ql_document({},{},[],self.location_list)
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    def test_generate_mongo_ql_document_locations_case_insensitive(self):
        mongo_document=generate_mongo_ql_document({},{},[],["manhattan".upper()])
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    def test_generate_mongo_ql_document(self):
        mongo_document=generate_mongo_ql_document(self.employment_dict, self.education_dict,self.skill_list, self.location_list)
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])

    @patch('query_expansion.infer_similar_job_title_kg')
    @patch('query_expansion.infer_similar_skill_kg')
    #@patch('query_expansion.extract_location_mentions_llm')
    def test_generate_mongo_ql_document_from_query_str(self, infer_similar_skill_kg_mock, 
                                                       infer_similar_job_title_kg_mock,
                                                       #extract_location_mentions_llm_mock
                                                       ):
        driver=None
        infer_similar_skill_kg_mock.return_value=self.skill_list
        infer_similar_job_title_kg_mock.return_value=["editor"]
        #extract_location_mentions_llm_mock.return_value=["metropolis"]
        mongo_document=generate_mongo_ql_document_from_query_str(self.query_str,driver)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(mongo_document)
        result=self.collection.find_one(mongo_document)
        self.assertEqual(self.good_candidate_id, result['_id'])


        


if __name__ =='__main__':
    unittest.main()
