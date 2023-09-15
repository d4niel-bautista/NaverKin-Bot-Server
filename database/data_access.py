from database.connect_database import connect_database

class DataAccess():
    def get_account(self, username=''):
        db_conn, db_cursor = connect_database()
        if db_cursor:
            if username:
                query = "SELECT username, passwd `password`, account_status `status`, levelup_id FROM naverkin_user WHERE account_status = 0 AND username != %s LIMIT 1;"
                params = (username,)
                db_cursor.execute(query, params)
            else:
                query = "SELECT username, passwd `password`, account_status `status`, levelup_id FROM naverkin_user WHERE account_status = 0 LIMIT 1;"
                db_cursor.execute(query)
            result = db_cursor.fetchone()
            db_cursor.close()
            db_conn.close()
            return result

    def add_account(self, username, password, account_name='', date_of_birth='2023-09-04', gender='', mobile_no='', recovery_email='', levelup_id=0, account_url='', account_status=0):
        db_conn, db_cursor = connect_database()
        if db_cursor and db_conn:
            query = "INSERT INTO naverkin_user(username, passwd, recovery_email, account_name, date_of_birth, gender, mobile_no, levelup_id, account_url, account_status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (username, password, recovery_email, account_name, date_of_birth, gender, mobile_no, levelup_id, account_url, account_status)
            db_cursor.execute(query, params)
            db_conn.commit()
            db_cursor.close()
            db_conn.close()
        self.add_account_interactions(username=username)
        self.add_user_session(username=username)
    
    def update_account(self, username, status):
        db_conn, db_cursor = connect_database()
        if db_cursor and db_conn:
            query = "UPDATE naverkin_user SET account_status = %s WHERE username = %s;"
            params = (str(status), username)
            db_cursor.execute(query, params)
            db_conn.commit()
            db_cursor.close()
            db_conn.close()
    
    def get_question(self, username='', levelup_id=''):
        db_conn, db_cursor = connect_database()
        if db_cursor:
            username = username.split('::')
            if len(username) == 2 and username[-1] == 'author':
                query = "SELECT question_id `id`, question_status `status`, respondent_user `respondent`, naverkin_user.account_url `respondent_url` FROM naverkin_question LEFT JOIN naverkin_user ON naverkin_question.respondent_user = naverkin_user.username WHERE author = %s AND respondent_user != '' AND question_status = 2 LIMIT 1;"
                params = (username[0],)
                db_cursor.execute(query, params)
            elif len(username) == 1:
                if levelup_id:
                    query = "SELECT question_id `id`, question_status `status`, respondent_user `respondent`, author FROM naverkin_question WHERE respondent_user != '' AND respondent_user != %s AND author != %s AND question_status = 1 LIMIT 1;"
                    params = (username[0], username[0])
                    db_cursor.execute(query, params)
                else:
                    query = "SELECT question_id `id`, question_status `status`, respondent_user `respondent`, author FROM naverkin_question WHERE respondent_user = '' AND author != %s AND question_status = 0 LIMIT 1;"
                    params = (username[0],)
                    db_cursor.execute(query, params)
            result = db_cursor.fetchone()
            db_cursor.close()
            db_conn.close()
            return result
    
    def get_unanswered_question(self, respondent):
        db_conn, db_cursor = connect_database()
        if db_cursor:
            query = "SELECT question_id `id`, question_status `status`, respondent_user `respondent`, author FROM naverkin_question WHERE respondent_user = %s AND author != %s AND question_status = 0 LIMIT 1;"
            params = (respondent, respondent)
            db_cursor.execute(query, params)
            result = db_cursor.fetchone()
            db_cursor.close()
            db_conn.close()
            return result
    
    def get_question_for_selection_count(self, author):
        db_conn, db_cursor = connect_database()
        if db_cursor:
            query = 'SELECT COUNT(question_id) `count` FROM naverkin_question WHERE author = %s AND question_status < 3;'
            params = (author,)
            db_cursor.execute(query, params)
            result = db_cursor.fetchone()
            db_cursor.close()
            db_conn.close()
            return result
    
    def add_question(self, id, title, author, status=0, respondent=''):
        db_conn, db_cursor = connect_database()
        if db_cursor and db_conn:
            query = "INSERT INTO naverkin_question(question_id, question_title, question_status, author, respondent_user) VALUES(%s, %s, %s, %s, %s);"
            params = (id, title, str(status), author, respondent)
            db_cursor.execute(query, params)
            db_conn.commit()
            db_cursor.close()
            db_conn.close()
        
    def update_question(self, id, respondent='', author='', status=1):
        db_conn, db_cursor = connect_database()
        if db_cursor and db_conn:
            if status == 3:
                query = "UPDATE naverkin_question SET question_status = %s WHERE question_id = %s AND author = %s;"
                params = (str(status), id, author)
            elif status == 2:
                query = "UPDATE naverkin_question SET question_status = %s WHERE question_id = %s;"
                params = (str(status), id)
            elif status == 1 or status == 0:
                query = "UPDATE naverkin_question SET question_status = %s, respondent_user = %s WHERE question_id = %s;"
                params = (str(status), respondent, id)
            db_cursor.execute(query, params)
            db_conn.commit()
            db_cursor.close()
            db_conn.close()
    
    def fetch_session(self, column, username):
        db_conn, db_cursor = connect_database()
        if db_cursor:
            query = f"SELECT {column} FROM user_session WHERE username = %s LIMIT 1;"
            params = (username,)
            db_cursor.execute(query, params)
            result = db_cursor.fetchone()
            db_cursor.close()
            db_conn.close()
            return result

    def save_session(self, column, value, username):
        db_conn, db_cursor = connect_database()
        if db_cursor and db_conn:
            query = f"UPDATE user_session SET {column} = %s WHERE username = %s;"
            params = (value, username)
            db_cursor.execute(query, params)
            db_conn.commit()
            db_cursor.close()
            db_conn.close()
    
    def add_user_session(self, username, cookies='', useragent=''):
        db_conn, db_cursor = connect_database()
        if db_cursor and db_conn:
            query = "INSERT INTO user_session(username, cookies, user_agent) VALUES (%s, %s, %s);"
            params = (username, cookies, useragent)
            db_cursor.execute(query, params)
            db_conn.commit()
            db_cursor.close()
            db_conn.close()
    
    def get_configs(self, config_id):
        db_conn, db_cursor = connect_database()
        if db_cursor:
            query = f"SELECT submit_delay, page_refresh, cooldown, prohibited_words, prescript, prompt, postscript, max_interactions, openai_api_key FROM crawler_configs WHERE config_id = %s LIMIT 1;"
            params = (config_id,)
            db_cursor.execute(query, params)
            result = db_cursor.fetchone()
            db_cursor.close()
            db_conn.close()
            return result
    
    def add_account_interactions(self, username, interactions=''):
        db_conn, db_cursor = connect_database()
        if db_cursor and db_conn:
            query = "INSERT INTO account_interactions(username, interacted_accounts) VALUES (%s, %s);"
            params = (username, interactions)
            db_cursor.execute(query, params)
            db_conn.commit()
            db_cursor.close()
            db_conn.close()
    
    def get_account_interactions(self, username):
        db_conn, db_cursor = connect_database()
        if db_cursor:
            query = "SELECT interacted_accounts FROM account_interactions WHERE username = %s LIMIT 1;"
            params = (username,)
            db_cursor.execute(query, params)
            result = db_cursor.fetchone()
            db_cursor.close()
            db_conn.close()
            return result
    
    def update_account_interactions(self, target, username):
        db_conn, db_cursor = connect_database()
        if db_cursor and db_conn:
            query = "UPDATE account_interactions SET interacted_accounts = %s WHERE username = %s;"
            params = (username, target)
            db_cursor.execute(query, params)
            db_conn.commit()
            db_cursor.close()
            db_conn.close()