import json
from preprocessing_agent import preprocessing_agent

with open("config.json") as f:
    config = json.load(f)

output = preprocessing_agent(config)
print(json.dumps(output, indent=4))
