from database.data_access import DataAccess
from utils import get_logger
logger = get_logger('server', 'logs/server.log')

class Service():
    data_access = None

    def __init__(self, data_access: DataAccess):
        self.data_access = data_access
    
    def set_clienthandler(self, clienthandler):
        self.clienthandler = clienthandler
    
    def add_question(self, **kwargs):
        self.data_access.add_question(**kwargs)
    
    def add_account(self, **kwargs):
        self.data_access.add_account(**kwargs)
    
    def get_question(self, username, levelup_id):
        question = self.data_access.get_question(username, levelup_id)
        if question:
            if levelup_id:
                return question
            self.update_question(id=question['id'], respondent=username, status=0)
            return question
        return "NO AVAILABLE QUESTION!"
    
    def get_unanswered_question(self, respondent):
        unanswered_question = self.data_access.get_unanswered_question(respondent)
        if unanswered_question:
            return unanswered_question
        return "NO UNANSWERED QUESTION!"
    
    def get_question_for_selection_count(self, author):
        count = self.data_access.get_question_for_selection_count(author=author)
        if count:
            return count
        return "NO RECORDED QUESTION"

    def select_question(self, username):
        question = self.data_access.get_question(username=username)
        if question:
            return question
        return "NO QUESTION AVAILABLE FOR ANSWER SELECTION!"
    
    def get_account(self, username=''):
        account = self.data_access.get_account(username)
        if account:
            self.update_account(username=account['username'], status=1)
            return account
        return "NO AVAILABLE ACCOUNT!"
    
    def get_account_interactions(self, username):
        interactions = self.data_access.get_account_interactions(username)
        if interactions:
            return interactions
        return "NO ACCOUNT INTERACTIONS!"
    
    def update_question(self, **kwargs):
        self.data_access.update_question(**kwargs)

    def update_account(self, **kwargs):
        self.data_access.update_account(**kwargs)
    
    def update_account_interactions(self, target, username):
        interacted_accounts = self.get_account_interactions(username=target)
        if type(interacted_accounts) == dict:
            if interacted_accounts['interacted_accounts']:
                interacted_accounts = interacted_accounts['interacted_accounts'].split(',')
                interacted_accounts.append(username)
                interacted_accounts = ",".join(interacted_accounts)
                self.data_access.update_account_interactions(target, interacted_accounts)
            else:
                self.data_access.update_account_interactions(target, interacted_accounts)
    
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
            username = request['data']['username']
            response = self.get_account(username)
        elif request['message'] == 'GET_QUESTION':
            respondent = request['data']['username']
            levelup_id = request['data']['levelup_id']
            response = self.get_question(respondent, levelup_id)
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
            author = request['data']['author']
            status = request['data']['status']
            self.update_question(id=id, respondent=respondent, author=author, status=status)
            if status == 1:
                response = f"UPDATED {id} TO ANSWERED BY RESPONDENT"
            elif status == 2:
                response = f"UPDATED {id} TO ANSWERED BY LEVELUP ID"
            elif status == 3:
                response = f"{id} HAS ANSWER SELECTED"
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
        elif request['message'] == "GET_ACCOUNT_INTERACTIONS":
            username = request['data']['username']
            response = self.get_account_interactions(username)
        elif request['message'] == "ADD_INTERACTED_ACCOUNT":
            target = request['data']['target']
            username = request['data']['username']
            self.update_account_interactions(target=target, username=username)
            self.update_account_interactions(target=username, username=target)
            response = f"ADDED {username} TO INTERACTED ACCOUNTS OF {target}"
        elif request['message'] == 'GET_QUESTION_FOR_SELECTION_COUNT':
            author = request['data']['author']
            response = self.get_question_for_selection_count(author=author)
        elif request['message'] == 'GET_UNANSWERED_QUESTION':
            respondent = request['data']['respondent']
            response = self.get_unanswered_question(respondent)
        return response
