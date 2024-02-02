from db import get_db
from bson.json_util import dumps
from flask import Blueprint, request
from markupsafe import escape

import pandas as pd
import numpy as np

bp = Blueprint('algorithms', __name__, url_prefix='/api/algorithms')


def get_value_from_thresholds(value, item):
    thresholds = item['thresholds']
    for threshold in thresholds:
        lower_threshold = threshold['min']
        upper_threshold = threshold['max']
        if lower_threshold <= value < upper_threshold:
            return float(threshold['score'])
    if 'default' in item.keys():
        return float(item['default'])
    return None


def get_value_from_label(value, item):
    labels = item['labels']
    for label in labels:
        if value == label['name']:
            return float(label['score'])
    if 'default' in item.keys():
        return float(item['default'])
    return None


value_mappers = {
    "NUMBER": lambda x, item: float(x),
    "BOOL": lambda x, item: float(x.lower().startswith('t')),
    "THRESHOLDS": lambda x, item: get_value_from_thresholds(x, item),
    "LABELS": lambda x, item: get_value_from_label(x, item)
}


def elaborate_values(df_values, items):
    for item in items:
        name = item['name']
        if 'fillna' in item.keys():
            df_values[name] = df_values[name].fillna(item['fillna'])
        df_values[name] = df_values[name].apply(lambda v: value_mappers[item['type']](v, item))
    return df_values

@bp.route("/<name>", methods=['GET'])
def get(name):
    algorithm = get_db().algorithm.find_one({'name': escape(name)})
    return dumps(algorithm, indent=2)


@bp.route("/<name>/execute", methods=['POST'])
def post(name):
    f = request.files['samples']
    df = pd.read_csv(f)
    algorithm = get_db().algorithm.find_one({'name': escape(name)})
    all_names = []
    all_codes = []
    for scorecard in algorithm['scorecards']:
        scorecard_code = scorecard['name']
        all_codes.append(scorecard_code)
        items = scorecard['items']
        names = [item['name'] for item in items]
        all_names.extend(names)
        weights = [item['weight'] for item in items]
        df_names = elaborate_values(df.loc[:, names], items)
        df[scorecard_code] = np.dot(df_names.values, weights)
    return df[all_names + all_codes].to_json(indent=2)


def get_algorithm_blueprint():
    return bp
