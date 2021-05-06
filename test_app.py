import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = f"postgres://localhost:5432/{self.database_name}"#.format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_q = {
            'question':'What is layered like an Ogre, according to Shrek?',
            'answer':'Onions',
            'category':5,
            'difficulty':1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        pass #Question.query.filter(Question.id>23).delete()
    

    def test_questions_search(self):

        res = self.client().post('/questions/search?page=2',json={"searchTerm":" "},
            headers={"Content-Type": "application/json"})
        data = json.loads(res.data.decode('utf-8'))
        # print('-'*80)
        # print(data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 20) # because we added a question
        self.assertEqual(res.status_code, 200)

    def test_searchterm(self):

        res = self.client().post('/questions/search',json={"searchTerm":"Cassius"},
            headers={"Content-Type": "application/json"})
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['questions'][0].get('answer'), 'Muhammad Ali')
        self.assertEqual(res.status_code, 200)

    def test_pagination(self):
        """ See that questions are returned based on page number query parameter """
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['num_records'], 10)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(data['categories'],{
                                            "1": "Science", 
                                            "2": "Art", 
                                            "3": "Geography", 
                                            "4": "History", 
                                            "5": "Entertainment", 
                                            "6": "Sports"
                                        })


    def test_404_get_questions_invalid_page(self):
        # Test invalid page number
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])
        self.assertEqual(data['error'], 404)

    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(data['categories'],{
                                            "1": "Science", 
                                            "2": "Art", 
                                            "3": "Geography", 
                                            "4": "History", 
                                            "5": "Entertainment", 
                                            "6": "Sports"
                                        })
    def test_invalid_delete(self):
        res = self.client().delete('/questions/100')
        self.assertEqual(res.status_code, 422)
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)




    def test_post_question(self):
        # delete new records posted in the process of testing other endpoints

        res = self.client().post('/questions',json=self.new_q)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
    
    def test_valid_delete(self):
        max_id = Question.query.order_by(Question.id)[-1].id
        res = self.client().delete(f'/questions/{max_id}')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)

        q = Question.query.filter(Question.id==max_id).one_or_none()
        self.assertEqual(q, None)

    def test_questions_by_Cat(self):

        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data.decode('utf-8'))
        #print(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['num_records'], 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(int(data['current_category']), 1)
        self.assertEqual(res.status_code, 200)



    def test_quiz(self):

        res = self.client().post('/quizzes', 
            json={'previous_questions': [12, 5, 9], 
                    'quiz_category': {'type': 'History', 'id': 4}})
            #json={'quiz_category': {'type': 'History', 'id': 4},'previous_questions': [12, 5, 9]})
        
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(data['question']['id'],23)
        self.assertEqual(res.status_code, 200)

                
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

