from dotenv import load_dotenv
import pymongo
import os
#load env
load_dotenv(override=True)
MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_PORT = os.getenv('MONGODB_PORT')
#mongo uri
mongo_uri = f'mongodb://{MONGODB_HOST}:{MONGODB_PORT}'
connetion = pymongo.MongoClient(mongo_uri)
db = connetion["iir"]
collection = db["pubmed_doc"]