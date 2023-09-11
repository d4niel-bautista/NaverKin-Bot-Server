from database.connect_database import connect_database

class DataAccess():
    db_conn = None
    db_cursor = None

    def __init__(self):
        self.db_conn, self.db_cursor = connect_database()

    def get_account(self):
        if self.db_cursor:
            query = "SELECT username, passwd `password`, account_status `status`, account_role `role` FROM naverkin_user WHERE account_status = 0 LIMIT 1;"
            self.db_cursor.execute(query)
            result = self.db_cursor.fetchone()
            return result

    def add_account(self, username, password, account_name, date_of_birth, gender, mobile_no, recovery_email='', account_status=0):
        if self.db_cursor and self.db_conn:
            query = "INSERT INTO naverkin_user(username, passwd, recovery_email, account_name, date_of_birth, gender, mobile_no, account_status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
            params = (username, password, recovery_email, account_name, date_of_birth, gender, mobile_no, str(account_status))
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
    
    def update_account(self, username, status):
        if self.db_cursor and self.db_conn:
            query = "UPDATE naverkin_user SET account_status = %s WHERE username = %s;"
            params = (str(status), username)
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
    
    def get_question(self, username=''):
        if self.db_cursor:
            if username:
                query = "SELECT question_id `id`, question_status `status`, respondent_user `respondent`, naverkin_user.account_url `respondent_url` FROM naverkin_question LEFT JOIN naverkin_user ON naverkin_question.respondent_user = naverkin_user.username WHERE author = %s AND respondent_user != '' AND question_status = 0 LIMIT 1;"
                params = (username,)
                self.db_cursor.execute(query, params)
            elif not username:
                query = "SELECT question_id `id`, question_status `status`, respondent_user `respondent` FROM naverkin_question WHERE respondent_user = '' AND question_status = 0 LIMIT 1;"
                self.db_cursor.execute(query)
            result = self.db_cursor.fetchone()
            return result
    
    def add_question(self, id, title, author, status=0, respondent=''):
        if self.db_cursor and self.db_conn:
            query = "INSERT INTO naverkin_question(question_id, question_title, question_status, author, respondent_user) VALUES(%s, %s, %s, %s, %s);"
            params = (id, title, str(status), author, respondent)
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
        
    def update_question(self, id, respondent='', author='', status=1):
        if self.db_cursor and self.db_conn:
            if respondent == '' and author != '':
                query = "UPDATE naverkin_question SET question_status = %s WHERE question_id = %s AND author = %s;"
                params = (str(status), id, author)
            elif author == '' and respondent != '':
                query = "UPDATE naverkin_question SET question_status = %s, respondent_user = %s WHERE question_id = %s;"
                params = (str(status), respondent, id)
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
    
    def fetch_session(self, column, username):
        if self.db_cursor:
            query = f"SELECT {column} FROM user_session WHERE username = %s LIMIT 1;"
            params = (username,)
            self.db_cursor.execute(query, params)
            result = self.db_cursor.fetchone()
            return result

    def save_session(self, column, value, username):
        if self.db_cursor and self.db_conn:
            query = f"UPDATE user_session SET {column} = %s WHERE username = %s;"
            params = (value, username)
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
    
    def get_configs(self, config_id):
        if self.db_cursor:
            query = f"SELECT submit_delay, page_refresh, cooldown, prohibited_words, prescript, prompt, postscript, openai_api_key FROM crawler_configs WHERE config_id = %s LIMIT 1;"
            params = (config_id,)
            self.db_cursor.execute(query, params)
            result = self.db_cursor.fetchone()
            return result