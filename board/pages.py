import io
from flask import Blueprint, render_template, request
import json
from hed import Sidecar, load_schema_version, TabularInput
from hed.errors import ErrorHandler, get_printable_issue_string
from hed.tools.analysis.annotation_util import strs_to_sidecar, to_strlist
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.hed_tag_manager import HedTagManager
import pandas as pd

bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    return render_template("pages/home.html")

@bp.route("/about")
def about():
    return "Hello, About!"


@bp.route("/validate", methods=["GET", "POST"])
def validate():
    data = request.get_json(force=True)
    y = json.dumps(data)
    check_for_warnings = False
    schema = load_schema_version('8.2.0')
    sidecar = strs_to_sidecar(y) #Sidecar(y)
    error_handler = ErrorHandler(check_for_warnings=check_for_warnings)
    issues = sidecar.validate(schema, name=sidecar.name, error_handler=error_handler)
    if issues:
        data = get_printable_issue_string(issues, f"Validation issues")
        response = data
    else:
        response = "No issues found"
    return response #you have to return json here as explained in the js file

@bp.route("/assemble", methods=["GET", "POST"])
def assemble():
    schema = load_schema_version('8.2.0')
    eventsjson = request.form['eventsjson']
    sidecar = Sidecar(io.StringIO(eventsjson))
    eventstsv = request.form['eventstsv']
    events = TabularInput(file=io.StringIO(eventstsv), sidecar=sidecar, name="Test")
    include_context = True
    replace_defs = True
    remove_types = ['Condition-variable', 'Task']
    event_manager = EventManager(events, schema)
    tag_manager = HedTagManager(event_manager,  remove_types)
    hed_string_objs = tag_manager.get_hed_objs(include_context, replace_defs);
    hed_strings = to_strlist(hed_string_objs)
    df = pd.read_csv(io.StringIO(eventstsv), sep='\t')
    df['HED'] = hed_strings
    return {"header": df.columns.tolist(), "data": df.to_numpy().tolist()}
