import sqlite3

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.connection.commit()
            self.connection.close()

    def create_table(self, table_name, columns):
        self.connect()
        column_str = ', '.join(columns)
        create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({column_str})'
        self.cursor.execute(create_table_query)

    def insert_data(self, table_name, values):
        self.connect()
        value_placeholders = ', '.join(['?'] * len(values))
        insert_query = f'INSERT INTO {table_name} VALUES ({value_placeholders})'
        self.cursor.execute(insert_query, values)
        self.disconnect()  # อาจจะเพิ่มการ disconnect หลังจาก insert

    def select_all_data(self, table_name):
        self.connect()
        select_query = f'SELECT * FROM {table_name}'
        self.cursor.execute(select_query)
        rows = self.cursor.fetchall()
        self.disconnect()  # อาจจะเพิ่มการ disconnect หลังจาก select
        return rows

    def select_data(self, data_names, table_name):
        self.connect()
        data_names_str = ', '.join(data_names)
        select_query = f'SELECT {data_names_str} FROM {table_name}'
        self.cursor.execute(select_query)
        selected_data = self.cursor.fetchall()
        self.disconnect()  # อาจจะเพิ่มการ disconnect หลังจาก select
        return selected_data

    def update_data(self, table_name, set_values, where_clause):
        self.connect()
        set_clause = ', '.join([f'{key} = ?' for key in set_values.keys()])
        update_query = f'UPDATE {table_name} SET {set_clause} WHERE {where_clause}'
        self.cursor.execute(update_query, list(set_values.values()))
        self.disconnect()  # อาจจะเพิ่มการ disconnect หลังจาก update

    def delete_data(self, table_name, where_clause):
        self.connect()
        delete_query = f'DELETE FROM {table_name} WHERE {where_clause}'
        self.cursor.execute(delete_query)
        self.disconnect()  # อาจจะเพิ่มการ disconnect หลังจาก delete