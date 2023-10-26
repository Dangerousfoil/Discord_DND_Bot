from tinydb import TinyDB


db = TinyDB("databases/recipe_database.json") # <- change database path to desired database
db.default_table_name = "Recipe_Database" # <- change database name to desired database


class DatabaseSetup:
    def __init__(self):
        self.db = db
        self.dict = []
        # ^ copy the dictionary into the square brackets

    def new_db_info(self):
        # Loops through items in the list and copies them into your database
        for i in self.dict:
            self.db.insert(i)
            print("Adding Item...")
        x = len(self.dict)
        print(f"Complete.\n{x} Items Added To Database.")


# Run the program it will copy the items from the dictionary to your database
database = DatabaseSetup()
database.new_db_info()
