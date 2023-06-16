from flask import Flask
from collections import defaultdict
from re import split
import psycopg2

'''
Helper functions
''' 
# create_app() creates the flask application.
def create_app():
    app = Flask(__name__)
    return app

# Helper function to extract data from csv files.
def extractData():
    # users[id] = userInfo
    # userExperiments[id] = List of experiments' [id, compound_ids, run_time]
    # compounds[id] = compoundInfo
    users, userExperiments, compounds = defaultdict(list), defaultdict(list), defaultdict(list)
    try:
        with open("data/users.csv") as f:
            # Skip header to start extracting user data
            for line in f.readlines()[2:]:
                l = split(",\t", line)
                users[l[0]] = l[1:]
                users[l[0]][-1] = users[l[0]][-1].strip('\n')
        with open("data/user_experiments.csv") as f:
            for line in f.readlines()[1:]:
                l = split(",\t", line)
                userExperiments[l[1]].append(l[:1] + l[2:])
                userExperiments[l[1]][-1][-1] = userExperiments[l[1]][-1][-1].strip('\n')
        with open("data/compounds.csv") as f:
            for line in f.readlines()[1:]:
                l = split(",\t", line)
                compounds[l[0]] = l[1:]
                compounds[l[0]][-1] = compounds[l[0]][-1].strip('\n')
    except:
        print("Encountered error while extracting csv data.")
    return users, userExperiments, compounds

# Helper function to extract features given data from csv files.
def deriveFeatures(users, userExperiments):
    # features[id] = user features
    features = defaultdict(list)
    for id in users:
        tot = len(userExperiments[id])
        avgTime = sum([int(e[-1]) for e in userExperiments[id]]) / tot
        count, mostIds = defaultdict(int), []
        for experiment in userExperiments[id]:
            for c in experiment[1].split(';'):
                count[c] += 1
        for k, v in count.items():
            if v == max(count.values()):
                mostIds.append(k)
        features[id] = [tot, avgTime, mostIds]
    return features

# Helper function to upload the derived features to a postgres table.
def uploadData(features):
    # Connect to the postgres database.
    try:
        conn = psycopg2.connect(database="postgresdb", user="postgres", password="backendtakehome", port="5432", host="postgresdb")
        conn.autocommit = True
        cursor = conn.cursor()
        queryStr = ""
        for k, v in features.items():
            queryStr += "('%s', '%d', '%s', '{%s}')," % (k, v[0], v[1], ','.join(v[2]))
        cursor.execute("INSERT INTO features(user_id, total_experiments, average_experiment_time, most_commonly_used_compounds) VALUES %s ON CONFLICT (user_id) DO UPDATE SET total_experiments=EXCLUDED.total_experiments, average_experiment_time=EXCLUDED.average_experiment_time, most_commonly_used_compounds=EXCLUDED.most_commonly_used_compounds" % queryStr[:-1])
        cursor.close()
    except:
        return "encountered error while uploading features to the postgres table."
    else:
        return "successfully uploaded features to the postgres table."
        
def etl():
    # Load CSV files
    users, userExperiments, compounds = extractData()
    # Process files to derive features
    features = deriveFeatures(users, userExperiments)
    # Upload processed data into a database
    s = uploadData(features)
    return s

'''
Exposed API endpoints 
'''
app = create_app()

# Your API that can be called to trigger your ETL process
@app.route('/etl')
def trigger_etl():
    # Trigger your ETL process here
    response = etl()
    return {"message": "ETL process started and process %s" % response}, 200
    
# Use to query database for derived features.
@app.route('/query')
def queryDB():
    try:
        conn = psycopg2.connect(database="postgresdb", user="postgres", password="backendtakehome", port="5432", host="postgresdb")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM features")
        query = cursor.fetchall()
        cursor.close()
    except:
        return "Encountered an error", 400
    else:
        return str(query), 200
    
if __name__ == "__main__":
    app.run(host ='0.0.0.0')