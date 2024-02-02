import os
from configparser import ConfigParser
from flask import Flask, stream_template
from flask_swagger_ui import get_swaggerui_blueprint

from algorithm import get_algorithm_blueprint

SWAGGER_URL = '/api/docs'
API_URL = 'http://127.0.0.1:5001/static/swagger.yaml'

config = ConfigParser()
config.read(os.path.abspath(os.path.join("rap.ini")))

app = Flask(__name__)
app.config["MONGO_URI"] = config['DEV']['DB_URI']

# Swagger blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "RAP application"
    }
)
app.register_blueprint(swaggerui_blueprint)

# Algorithm blueprint
algorithm_blueprint = get_algorithm_blueprint()
app.register_blueprint(algorithm_blueprint)


@app.route("/client-demo", methods=['GET'])
def client_demo():
    return stream_template('client-demo.html', title='Client Demo')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
