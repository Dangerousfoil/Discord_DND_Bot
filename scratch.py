# from tinydb import TinyDB, Query

# reagent_db = TinyDB("assets/databases/reagent_database.json")
# reagent_db.default_table_name = "Reagent_Database"
# query = Query()

# effects = []
# single_effect = []

# for item in reagent_db:
#     for key, value in item.items():
#         if key == "Effect":
#             effects.append(value)

# for effect in effects:
#     if type(effect) is list:
#         for i in effect:
#             if i not in single_effect:
#                 single_effect.append(i)
#                 effect.remove(i)
#     else:
#         if effect not in single_effect:
#             single_effect.append(effect)
#             effects.remove(effect)

# for x, y in enumerate(single_effect, 1):
#     print(f"{x}: {y}")\69999999
