import os
import sys
sys.path.append(os.getcwd())
import unittest

class BehaviorTest(unittest.TestCase):
    def test_database_complete(self):
        '''
        GIVEN a user_query, and a mongoDB query_document, and a mongo db collection n_queries=10, and 10 candidates that match the mongodb query
        WHEN the 10 candidates are put into the collection, and we call candidate_search_flow
        THEN we should return the 10 candidates
        '''
        return
    
    def test_database_incomplete(self):
        '''
        GIVEN an user_query, and a mongoDB query_document, and a collection, n_queries=10, and 9 candidates that match the mongodb query
            and we have set a mock so basilsearchsweeper.external_web_sweep returns [candidate X]
        WHEN the 9 candidates are put into the database, and we call candidate_search_flow
        THEN we should return the 9 candidates + candidate X, and candidate X should be inserted into the collection
        ''' 
        return
    
    def test_database_empty(self):
        '''
        GIVEN an user_query, and a mongoDB query_document, and a collection, n_queries=10, and 10 candidates
            and we have set a mock so basilsearchsweeper.external_web_sweep returns the 10 candidates
        WHEN we call candidate_search_flow
        THEN we should return the 10 candidates, and they should be inserted into the collection
        ''' 
        return
    
    def test_database_incomplete_with_redundancy(self):
        '''
        GIVEN an user_query, and a mongoDB query_document, and a collection, n_queries=10, and 5 candidates
            and we have set a mock so basilsearchsweeper.external_web_sweep returns the 5 candidates
            and the 5 candidates have been put into the collection
        WHEN we call candidate_search_flow
        THEN we should return the 5 candidates (redundant ones should have been removed)
        '''
        return