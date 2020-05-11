import json
#import os

class Database:
    
    def __init__(self, name, dir_path, parse_db = False):
        #this_dir_path = os.path.abspath(os.path.dirname(__file__))
        self.db = json.load(open('%s/%s.json' % (dir_path,name)))
        self.db = self.db['database']
        self.index = {}
        if parse_db:
            for partner in self.db:
                for feature in partner:
                    if feature not in self.index:
                        self.index[feature] = set()
                    if feature=="name":
                        for name in partner[feature]:
                            self.index[feature].add(name)
                    else:
                        self.index[feature].add(partner[feature])