from database.data_access import DataAccess
from utils import get_logger
logger = get_logger('server', 'logs/server.log')

class Service():
    data_access = None

    def __init__(self, data_access: DataAccess):
        self.data_access = data_access
    
    def add_question(self, **kwargs):
        self.data_access.add_question(**kwargs)
    
    def add_account(self, **kwargs):
        self.data_access.add_account(**kwargs)
    
    def get_question(self, username):
        question = self.data_access.get_question()
        if question:
            self.update_question(id=question['id'], respondent=username, status=0)
            return question
        return "NO AVAILABLE QUESTION!"
    
    def get_account(self):
        account = self.data_access.get_account()
        if account:
            self.update_account(username=account['username'], status=1)
            return account
        return "NO AVAILABLE ACCOUNT!"
    
    def update_question(self, **kwargs):
        self.data_access.update_question(**kwargs)

    def update_account(self, **kwargs):
        self.data_access.update_account(**kwargs)
    
    def process_request(self, request):
        if request['message'] == 'GET_ACCOUNT':
            response = self.get_account()
        elif request['message'] == 'GET_QUESTION':
            respondent = request['data']['username']
            response = self.get_question(respondent)
        return response
