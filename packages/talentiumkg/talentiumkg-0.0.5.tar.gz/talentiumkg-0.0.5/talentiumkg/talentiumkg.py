from neo4j import GraphDatabase
import pandas as pd
import os

'''
Authentication information, right now the instance is on zeyu's personal account.
To create your own instance and test it out, pleas follow the instruction on https://neo4j.com/docs/aura/auradb/.
And use the data from the KG directory to create your own graph.
'''
NEO4J_URI = "neo4j+s://bc2ca9c6.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "h5ROEfuHjUgEA_ucQnJ3vXUD9ASO7XpMgsQVTczhl2M"
AURA_INSTANCEID = "bc2ca9c6"
AURA_INSTANCENAME = "Instance01"
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)


class KnowledgeGraph():
    def __init__(self, uri=None, username=None, password=None):
        if username is None:
            self.neo4j_username = NEO4J_USERNAME
        else:
            self.neo4j_username = username
        if password is None:
            self.neo4j_password = NEO4J_PASSWORD
        else:
            self.neo4j_password = password
        if uri is None:
            self.neo4j_uri = NEO4J_URI
        else:
            self.neo4j_uri = uri
        with GraphDatabase.driver(NEO4J_URI, auth=(self.neo4j_username, self.neo4j_password)) as driver:
            self.driver = driver
        this_dir, this_filename = os.path.split(__file__)
        self.skills = set()
        self.titles = set()
        self.load_data(this_dir)

    def check_connectivity(self):
        self.driver.verify_connectivity()

    def load_data(self, path):
        skills = pd.read_csv(os.path.join(path, "data", "skills.csv"))
        self.skills = set(skills['name'].values.tolist())
        titles = pd.read_csv(os.path.join(path, "data", "titles.csv"))
        self.titles = set(titles['name'].values.tolist())

    def infer_similar_job_title(self, title, max_num=5):
        """
        This function takes a given job title, and return a list of titles that based on the number of matched skills.
        driver: a neo4j python driver for connecting to the graph instance.
        title: the seed job title you want to infer.
        max_num: the max number of similar title you want ot generate.
        """
        query_string = '''MATCH (p:Title {{name: "{title}"}}) -[:Require]->(skills)
                        MATCH (similar) -[r:Require]-> (skills)
                        WHERE p <> similar
                        WITH DISTINCT similar,r
                        RETURN similar.name, COUNT(r)
                        ORDER BY COUNT(r) DESC
                        LIMIT {num}'''.format(title=title,num=max_num)
        records, summary, keys = self.driver.execute_query(query_string)
        res = [title['similar.name'] for title in records]
        return res

    def infer_similar_skill(self, skill, max_num=5):
        """
        This function takes a given job title, and return a list of titles that based on the number of matched skills.
        driver: a neo4j python driver for connecting to the graph instance.
        skill: the seed skill you want to infer.
        max_num: the max number of similar title you want ot generate.
        """
        query_string = '''MATCH (p:Title) -[:Require]->(skills {name:"{skill}"})
                            MATCH (p) -[r:Require]-> (similar)
                            WHERE skills <> similar
                            WITH DISTINCT similar,r
                            RETURN similar.name, COUNT(r)
                            ORDER BY COUNT(r) DESC
                            LIMIT {num}'''.format(skill=skill, num=max_num)
        records, summary, keys = self.driver.execute_query(query_string)
        res = [skill['similar.name'] for skill in records]
        return res

    def generate_query_candidate(self, raw_query, ngram=3):
        tokens = raw_query.split(' ')
        res = []
        for i in range(len(tokens)):
            for span in range(ngram, 0, -1):
                if i + span < len(tokens):
                    if ' '.join(tokens[i:i + span]).lower() in self.titles:
                        candidates = self.infer_similar_job_title(' '.join(tokens[i:i + span]).lower())
                        for candidate_title in candidates:
                            # (start_pos, end_pos, candidate string, relevant socre)
                            res.append([i, i + span - 1, candidate_title, 1])
        return res
