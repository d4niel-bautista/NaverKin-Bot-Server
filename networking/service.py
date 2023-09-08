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

    def select_question(self, username):
        question = self.data_access.get_question(username=username)
        if question:
            return question
        return "NO QUESTION WAITING FOR SELECTION!"
    
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
    
    def get_cookies(self, **kwargs):
        cookies = self.data_access.fetch_session(**kwargs)
        if cookies:
            if cookies['cookies'] and cookies['cookies'] != '[]':
                return cookies
        return f"USER {kwargs['username']} HAS NO COOKIES SAVED!"

    def save_cookies(self, **kwargs):
        self.data_access.save_session(**kwargs)
    
    def get_useragent(self, **kwargs):
        useragent = self.data_access.fetch_session(**kwargs)
        if useragent:
            if useragent['useragent']:
                return useragent
        return f"USER {kwargs['username']} HAS NO USER AGENT SAVED!"
    
    def save_useragent(self, **kwargs):
        self.data_access.save_session(**kwargs)
    
    def get_configs(self, config_id):
        configs = self.data_access.get_configs(config_id)
        if configs:
            return configs
        return f"NO CONFIGS FOUND!"
    
    def process_request(self, request):
        if request['message'] == 'GET_ACCOUNT':
            response = self.get_account()
        elif request['message'] == 'GET_QUESTION':
            respondent = request['data']['username']
            response = self.get_question(respondent)
        elif request['message'] == 'SELECT_QUESTION':
            author = request['data']['username']
            response = self.select_question(author)
        elif request['message'] == 'UPDATE_ACCOUNT':
            username = request['data']['username']
            status = request['data']['status']
            self.update_account(username=username, status=status)
            if status == 0:
                response = f"UPDATED {username} TO AVAILABLE"
            elif status == 1:
                response = f"UPDATED {username} TO ACTIVE"
            elif status == 2:
                response = f"UPDATED {username} TO REACHED ID LIMIT"
            elif status == 3:
                response = f"UPDATED {username} TO TERMINATED"
        elif request['message'] == 'UPDATE_QUESTION':
            id = request['data']['id']
            respondent = request['data']['respondent']
            status = request['data']['status']
            self.update_question(id=id, respondent=respondent, status=status)
            response = f"UPDATED {id} TO ANSWERED"
        elif request['message'] == 'GET_COOKIES':
            username = request['data']['username']
            response = self.get_cookies(column='cookies', username=username)
        elif request['message'] == 'SAVE_COOKIES':
            username = request['data']['username']
            cookies = request['data']['cookies']
            self.save_cookies(column='cookies', value=cookies, username=username)
            response = f"SAVED {username} COOKIES"
        elif request['message'] == 'GET_USERAGENT':
            username = request['data']['username']
            response = self.get_useragent(column='user_agent `useragent`', username=username)
        elif request['message'] == 'SAVE_USERAGENT':
            username = request['data']['username']
            useragent = request['data']['useragent']
            self.save_useragent(column='user_agent', value=useragent, username=username)
            response = f"SAVED {username} USER AGENT"
        elif request['message'] == 'GET_CONFIGS':
            config_id = request['data']['config_id']
            response = self.get_configs(config_id)
        elif request['message'] == 'SAVE_QUESTION':
            id = request['data']['question_id'] 
            title = request['data']['question_title'] 
            author = request['data']['author']
            self.add_question(id=id, title=title, author=author)
            response = f"SAVED QUESTION {id}"
        return response
