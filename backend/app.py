from flask import Flask
from flask_restful import Api
from src.api.resource.datasource import DataSource
from src.api.resource.search import Search
import logging

app = Flask(__name__)
api = Api(app)

logging.basicConfig(level=logging.DEBUG)


api.add_resource(DataSource, "/source/", "/source/<string:source_id>")
api.add_resource(Search, "/source/<string:source_id>/search")

if __name__ == "__main__":
    app.run(debug=True)
