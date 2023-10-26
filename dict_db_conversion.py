from tinydb import TinyDB

# change database path to desired database
db = TinyDB('databases/recipe_database.json')
# change database name to desired database
db.default_table_name = 'Recipe_Database'


class DatabaseSetup:
    def __init__(self):
        self.db = db
        # copy the dictionary into the square brackets
        self.dict = [{'Name': 'metal_weapon', 'metal': 1, 'wood': 0.5, 'hide': 0.125, 'tools': "Woodcarver's Tools and Smith's Tool's"},
                      {'Name': 'metal_armor', 'metal': 1, 'wood': 0, 'hide': 0.125, 'tools': "Woodcarver's Tools and Smith's Tool's"},
                      {'Name': 'wood_weapon', 'metal': 0.5, 'wood': 1, 'hide': 0.125, 'tools': "Woodcarver's Tools"},
                      {'Name': 'hide_armor', 'metal': 0.125, 'wood': 0, 'hide': 1, 'tools': "Woodcarver's Tools and Smith's Tool's"},
                      {'Name': 'metal_ammo', 'metal': 1, 'wood': 0, 'hide': 0, 'tools': "Smith's Tool's"},
                      {'Name': 'wood_ammo', 'metal': 1, 'wood': 1, 'hide': 1, 'tools': "Woodcarver's Tools and Smith's Tool's"}]

    def new_db_info(self):
        for i in self.dict:
            self.db.insert(i)
            print('Adding Item...')
        x = len(self.dict)
        print(f'Complete.\n{x} Items Added To Database.')


# Run the program it will copy the items from the dictionary to your database
database = DatabaseSetup()
database.new_db_info()
