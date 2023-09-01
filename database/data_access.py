from database.connect_database import connect_database

class DataAccess():
    db_conn = None
    db_cursor = None

    def __init__(self):
        self.db_conn, self.db_cursor = connect_database()

    def get_account(self):
        if self.db_cursor:
            query = "SELECT username, passwd FROM naverkin_user WHERE account_status = 0 LIMIT 1;"
            self.db_cursor.execute(query)
            result = self.db_cursor.fetchone()
            return result

    def add_account(self, username, password, account_name, date_of_birth, gender, mobile_no, account_status=0):
        if self.db_cursor and self.db_conn:
            query = "INSERT INTO naverkin_user(username, passwd, account_name, date_of_birth, gender, mobile_no, account_status) VALUES(%s, %s, %s, %s, %s, %s, %s)"
            params = (username, password, account_name, date_of_birth, gender, mobile_no, str(account_status))
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
    
    def update_account(self, username, status):
        if self.db_cursor and self.db_conn:
            query = "UPDATE naverkin_user SET account_status = %s WHERE username = %s;"
            params = (str(status), username)
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
    
    def get_question(self):
        if self.db_cursor:
            query = "SELECT question_id FROM naverkin_question WHERE respondent_user = '' LIMIT 1;"
            self.db_cursor.execute(query)
            result = self.db_cursor.fetchone()
            return result
    
    def add_question(self, id, title, author, status=0, respondent=''):
        if self.db_cursor and self.db_conn:
            query = "INSERT INTO naverkin_question(question_id, question_title, question_status, author, respondent_user) VALUES(%s, %s, %s, %s, %s);"
            params = (id, title, str(status), author, respondent)
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
        
    def update_question(self, id, respondent, status=1):
        if self.db_cursor and self.db_conn:
            query = "UPDATE naverkin_question SET question_status = %s, respondent_user = %s WHERE question_id = %s;"
            params = (str(status), respondent, id)
            self.db_cursor.execute(query, params)
            self.db_conn.commit()
