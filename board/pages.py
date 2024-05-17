import io
from flask import Blueprint, render_template, request
import json
from hed import Sidecar, load_schema_version, TabularInput
from hed.errors import ErrorHandler, get_printable_issue_string
from hed.tools.analysis.annotation_util import strs_to_sidecar, to_strlist
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.hed_tag_manager import HedTagManager
import pandas as pd
from .openai_api import prompt_engineer
from .create_hed_prompts import get_hed_vocab

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

@bp.route("/generate", methods=["GET", "POST"])
def generate_tags():
    description = request.form['description']
    hed_vocab = get_hed_vocab()
    messages=[
        {"role": "system", "content": "You are a precise translator."},
        {"role": "system", "content": f"Translate these sentences into tags using only tags from the provided list: {hed_vocab}."},
        {"role": "user", "content": "The foreground view consists of a large number of ingestible objects, indicating a high quantity. The background view includes an adult human body, outdoors in a setting that includes furnishings, natural features such as the sky, and man-made objects in an urban environment."},
        {"role": "assistant", "content": "(Foreground-view, ((Item-count, High), Ingestible-object)), (Background-view, ((Human, Body, Agent-trait/Adult), Outdoors, Furnishing, Natural-feature/Sky, Urban, Man-made-object))"},
        {"role": "user", "content": "In the foreground view, there is an adult human body, an adult male face turned away from the viewer, and a high number of furnishings. In the background view, there are ingestible objects, furnishings, a room indoors, man-made objects, and an assistive device."},
        {"role": "assistant", "content": "(Foreground-view, ((Item-count/1, (Human, Body, Agent-trait/Adult)), (Item-count/1, (Human, Body, (Face, Away-from), Male, Agent-trait/Adult)), ((Item-count, High), Furnishing))), (Background-view, (Ingestible-object, Furnishing, Room, Indoors, Man-made-object, Assistive-device))"},
        {"role": "user", "content": "In the foreground view, we see a male adolescent human, characterized by his body and traits as an agent. He is interacting with a man-made object, possibly engaged in play or using it in some way. In the background view, the setting is outdoors, specifically showing a natural feature such as an ocean."},
        # {"role": "assistant", "content": "(Foreground-view, ((Item-count/1, (Human, Body, Agent-trait/Adult)), (Item-count/1, (Human, Body, (Face, Away-from), Male, Agent-trait/Adult)), ((Item-count, High), Furnishing))), (Background-view, (Ingestible-object, Furnishing, Room, Indoors, Man-made-object, Assistive-device))"},
    ]
    output = prompt_engineer(messages,"gpt-3.5-turbo")

    ## TODO: try few shots
    print('ground truth: (Foreground-view, ((Item-count/1, ((Human, Human-agent), Body, Male, Agent-trait/Adolescent)), (Play, (Item-count/1, Man-made-object)))), (Background-view, (Outdoors, Natural-feature/Ocean))')
    print(output)
    # messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": f"Given this list of tags: {hed_vocab}."},
    #         {"role": "user", "content": f"And given this annotation: {output}."},
    #         {"role": "user", "content": f"Highlight the tags that are from the list by captioning them with *"},
    # ]
    # opai.prompt_engineer(messages,"gpt-3.5-turbo")