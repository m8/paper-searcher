import os
import json
import time

def read_json_file(filename):
    with open(filename, "r") as f:
        return json.load(f)

class dump_database:
    def __init__(self, db_path):
        self.db_entries = []
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
    
    def create_db(self):
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        
        # create metadata file, idk why maybe for future use
        with open(self.db_path + "/metadata.json", "w") as f:
            f.write(json.dumps({"date": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}))
        
    def is_conference_in_db(self, conference):
        return os.path.exists(self.db_path + "/" + conference + ".json")

    def load_conference_from_db(self, conference):
        if self.is_conference_in_db(conference):
            return read_json_file(self.db_path + "/" + conference + ".json")
        else:
            return None

    def add_to_database(self, json, venue=""):
        json_entries = json['result']['hits']['hit']
        for json_entry in json_entries:
            entry = self.convert_json_entry(json_entry, venue)
            self.db_entries.append(entry)
        self.sort_entries()

    def sort_entries(self):
        self.db_entries.sort(key=lambda x: x.year, reverse=True)

    def parse_query(self,query):
        keywords = []
        venues = []

        special_keywords = ["in", "and", "or", "not"]

        current_group = "keywords"
        for token in query.split():
            if token.lower() in special_keywords:
                if token.lower() == "in":
                    current_group = "venues"
                continue
            if current_group == "keywords":
                keywords.append(token)
            else:
                venues.append(token)

        return keywords, venues  
    
    def check(self, entry, keywords, venues):
        if len(venues) > 0:
            if entry.u_venue not in venues:
                return False
        for keyword in keywords:
            if keyword.lower() not in entry.title.lower():
                return False
        return True

    def search(self, query):
        keywords, venues = self.parse_query(query)
        print("Searching for " + str(keywords) + " in " + str(venues))
        results = []
        for entry in self.db_entries:
            if self.check(entry, keywords, venues):
                results.append(entry)
        return results

    def convert_json_entry(self, json_entry, venue=""):
        entry = _entry()
        entry.title = json_entry['info']['title']
        entry.authors = json_entry['info']['authors'] if 'authors' in json_entry['info'] else []
        entry.venue = json_entry['info']['venue'] if type(json_entry['info']['venue']) is str else ""
        entry.year = json_entry['info']['year']
        entry.doi = json_entry['info']['doi'] if 'doi' in json_entry['info'] else ""
        entry.ee = json_entry['info']['ee'] if 'ee' in json_entry['info'] else ""
        entry.u_venue = venue
        return entry

class _entry:    
    def __init__(self):
        self.title = ""
        self.authors = []
        self.u_venue = ""
        self.venue = ""
        self.year = 0
        self.doi = ""     
        self.ee = ""