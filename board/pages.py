import io
from flask import Blueprint, render_template, request
from flask_cors import CORS
import json
from hed import HedString, Sidecar, load_schema_version, TabularInput
from hed.errors import ErrorHandler, get_printable_issue_string
from hed.tools.analysis.annotation_util import strs_to_sidecar, to_strlist
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.hed_tag_manager import HedTagManager
from hed.validator import HedValidator
import pandas as pd
from .openai_api import prompt_engineer
from .create_hed_prompts import get_hed_vocab

bp = Blueprint("pages", __name__)
CORS(bp)
@bp.route("/")
def home():
    hed_tags = get_hed_vocab()
    return render_template("pages/home.html", hed_tags=hed_tags)

@bp.route("/about")
def about():
    return "Hello, About!"


@bp.route("/validate", methods=["GET", "POST"])
def validate():
    validation_type = request.form['type']
    check_for_warnings = False
    schema = load_schema_version('8.2.0')
    data = request.form['hed']
    if validation_type == "sidecar":
        data_json = json.loads(data)
        data_json = json.dumps(data_json)
        sidecar = strs_to_sidecar(data_json) 
        error_handler = ErrorHandler(check_for_warnings=check_for_warnings)
        issues = sidecar.validate(schema, name=sidecar.name, error_handler=error_handler)
    else:
        hedObj = HedString(data, schema)
        short_string = hedObj.get_as_form('short_tag')

        # Validate the string
        error_handler = ErrorHandler(check_for_warnings=check_for_warnings)
        validator = HedValidator(schema)
        issues = validator.validate(hedObj, allow_placeholders=False, error_handler=error_handler)

    if issues:
        data = get_printable_issue_string(issues, f"Validation issues")
        response = data
    else:
        response = "No issues found"
    return response #you have to return json here as explained in the js file

def validateString(hedStr):
    check_for_warnings = False
    schema = load_schema_version('8.2.0')
    hedObj = HedString(hedStr, schema)
    short_string = hedObj.get_as_form('short_tag')

    # Validate the string
    error_handler = ErrorHandler(check_for_warnings=check_for_warnings)
    validator = HedValidator(schema)
    issues = validator.validate(hedObj, allow_placeholders=False, error_handler=error_handler)

    if issues:
        data = get_printable_issue_string(issues, f"Validation issues")
        response = data
    else:
        response = "No issues found"
    return response

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

@bp.route("/generate", methods=["GET", "POST"])
def generate_tags():
    description = request.form['description']
    hed_vocab = ",".join(get_hed_vocab())
    messages=[
        {"role": "system", "content": "You are a precise translator."},
        {"role": "system", "content": f"Translate these sentences into tags using only tags from the provided list: {hed_vocab}."},
        {"role": "user", "content": "The foreground view consists of a large number of ingestible objects, indicating a high quantity. The background view includes an adult human body, outdoors in a setting that includes furnishings, natural features such as the sky, and man-made objects in an urban environment."},
        {"role": "assistant", "content": "(Foreground-view, ((Item-count, High), Ingestible-object)), (Background-view, ((Human, Body, Agent-trait/Adult), Outdoors, Furnishing, Natural-feature/Sky, Urban, Man-made-object))"},
        {"role": "user", "content": "In the foreground view, there is an adult human body, an adult male face turned away from the viewer, and a high number of furnishings. In the background view, there are ingestible objects, furnishings, a room indoors, man-made objects, and an assistive device."},
        {"role": "assistant", "content": "(Foreground-view, ((Item-count/1, (Human, Body, Agent-trait/Adult)), (Item-count/1, (Human, Body, (Face, Away-from), Male, Agent-trait/Adult)), ((Item-count, High), Furnishing))), (Background-view, (Ingestible-object, Furnishing, Room, Indoors, Man-made-object, Assistive-device))"},
        {"role": "user", "content": description},
    ]
    output = prompt_engineer(messages,"gpt-3.5-turbo")
    validation_result = validateString(output)

    ## TODO: try few shots
    result = {
        "tags": output,
        "validation_issues": validation_result
    }
    return result