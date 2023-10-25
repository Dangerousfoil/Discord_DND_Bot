from tinydb import TinyDB

# change database path to desired database
db = TinyDB('databases/reagent_database.json')
# change database name to desired database
db.default_table_name = 'Reagent_Database'


class DatabaseSetup:
    def __init__(self):
        self.db = db
        # copy the dictionary into the square brackets
        self.dict = []
    def new_db_info(self):
        for i in self.dict:
            self.db.insert(i)
            print('Adding Item...')
        x = len(self.dict)
        print(f'Complete.\n{x} Items Added To Database.')


# Run the program it will copy the items from the dictionary to your database
database = DatabaseSetup()
database.new_db_info()
