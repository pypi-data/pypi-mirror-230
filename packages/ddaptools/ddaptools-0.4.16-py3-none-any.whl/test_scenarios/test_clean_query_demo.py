import json
from typing import List

def cleanQueryArgument(queryArgument):
        # If the queryArg is a list or dict, format it into a way that is query insertable
        if isinstance(queryArgument, (dict)):
            # If the is List and the first element is a dict, then it is a list of objects
            return json.dumps(queryArgument)
        if isinstance(queryArgument, List) and len(queryArgument) >0 and isinstance(queryArgument[0], dict):
            # return an array of strings of the json
            for(i, item) in enumerate(queryArgument):
                queryArgument[i] = cleanQueryArgument(item)
        
        return queryArgument


examples = [
     {"simple-dict": "hello"},
     [{"nested-dict": 1}, {"nested-dict-2": 2}],
     [
      {
        "name": "iamge-.jpg",
        "size": 17292,
        "type": "image/jpeg",
        "lastModified": 1683577149679,
        "lastModifiedDate": "2023-05-08T20:19:09.679Z",
        "webkitRelativePath": ""
      }
    ]
]

for item in examples:
     print(cleanQueryArgument(item))


