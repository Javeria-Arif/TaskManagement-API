
import unittest
from app import app 

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()  

    def test_sign_up(self):
        
        request_data = {
        "email": "testuser@gmail.com",
        "password": "12345"
        }

        response = self.app.post('/signup', json=request_data)

       
        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        self.assertEqual(response_data['success'], True )
        
        
def test_login(self):
        
        request_data = {
        "email": "testuser@gmail.com",
        "password": "12345"
        }

        response = self.app.post('/login', json=request_data)

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.bearer_token = response_data['access_token'] 

def test_create_teask(self):
   
        request_data = {
        "title" : "TestTask",
        "description" : "Learning Python",
        "due_date": "2023-09-22",
        "status"  : "COMPLETED"
    } 
        bearer_token = self.bearer_token

        headers = {
            'Authorization': f'Bearer {bearer_token}'
        }

        response = self.app.post('/', json=request_data, headers = headers)

        
        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        

        

if __name__ == '__main__':
    unittest.main()
