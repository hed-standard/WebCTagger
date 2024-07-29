import os
import io
from io import StringIO
from flask import Blueprint, render_template, request
from flask_cors import CORS
import json
from hed import HedString, Sidecar, load_schema_version, TabularInput
from hed.errors import ErrorHandler, get_printable_issue_string
from hed.tools.analysis.annotation_util import strs_to_sidecar, to_strlist
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.hed_tag_manager import HedTagManager
from hed.tools.analysis.tabular_summary import TabularSummary
from hed.validator import HedValidator
import pandas as pd
from .openai_api import prompt_engineer
from .create_hed_prompts import get_hed_vocab
from autogen.agentchat import ConversableAgent

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

@bp.route("/validate_string", methods=["GET", "POST"])
def validateString(hedStr):
    check_for_warnings = False
    schema = load_schema_version('8.3.0')
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

def validate_hed_string_agent(hed_string: str) -> str:
    schema = load_schema_version('8.3.0')
    check_for_warnings = True
    data = hed_string
    hedObj = HedString(data, schema)
    short_string = hedObj.get_as_form('short_tag')

    # Validate the string
    error_handler = ErrorHandler(check_for_warnings=check_for_warnings)
    # validator = HedValidator(schema, def_dict)
    validator = HedValidator(schema)
    issues = validator.validate(hedObj, allow_placeholders=False, error_handler=error_handler)
    if issues:
        issues = get_printable_issue_string(issues, 'Validation issues').strip('\n')
        return issues
    else:
        return 'TERMINATE'

@bp.route("/generate_sidecar", methods=["GET", "POST"])
def generate_sidecar_template():
    event_file = request.form['event_file']
    skip_columns = ["onset", "duration", "sample"]
    value_summary = TabularSummary(skip_cols=skip_columns)
    StringData = StringIO(event_file)
    df = pd.read_csv(StringData, sep ="\t")
    value_summary.update(df)
    sidecar_template = value_summary.extract_sidecar_template()

    return json.dumps(sidecar_template, indent=4)

@bp.route("/assemble", methods=["GET", "POST"])
def assemble():
    schema = load_schema_version('8.3.0')
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

@bp.route("/generate_agent", methods=["GET", "POST"])
def generate_tags_agent():
    description = request.form['description']
    config_list = [{"model": "gpt-4", "api_key": os.getenv("OPENAI_API_KEY")}]
    hed_vocab = ",".join(get_hed_vocab())

    assistant = ConversableAgent(
        name="CodeWriter",
        system_message="You are an annotator.\n"
        f"You use the vocabulary given to you to create appropriate annotations: {hed_vocab}.\n"
        "Here are some examples\n"
        "Text description: 'The foreground view consists of a large number of ingestible objects, indicating a high quantity. The background view includes an adult human body, outdoors in a setting that includes furnishings, natural features such as the sky, and man-made objects in an urban environment.'\n"
        "Annotation: '(Foreground-view, ((Item-count, High), Ingestible-object)), (Background-view, ((Human, Body, Agent-trait/Adult), Outdoors, Furnishing, Natural-feature/Sky, Urban, Man-made-object))'\n"
        "Text description: In the foreground view, there is an adult human body, an adult male face turned away from the viewer, and a high number of furnishings. In the background view, there are ingestible objects, furnishings, a room indoors, man-made objects, and an assistive device.\n"
        "Annotation: '(Foreground-view, ((Item-count/1, (Human, Body, Agent-trait/Adult)), (Item-count/1, (Human, Body, (Face, Away-from), Male, Agent-trait/Adult)), ((Item-count, High), Furnishing))), (Background-view, (Ingestible-object, Furnishing, Room, Indoors, Man-made-object, Assistive-device))'\n"
        "Once there is no error returned by the validator, the task is done. Returns 'TERMINATE'.",
        llm_config={"config_list": config_list},
        is_termination_msg=lambda msg: "TERMINATE" in msg['content'].strip().upper(),
        human_input_mode="NEVER",
    )

    user_proxy = ConversableAgent(
        name="User",
        llm_config=False,
    )

    # # Register the tool signature with the assistant agent.
    assistant.register_for_llm(name="validate_hed_string", description="An effective translator")(validate_hed_string_agent)

    # Register the tool function with the user proxy agent.
    user_proxy.register_for_execution(name="validate_hed_string")(validate_hed_string_agent)

    chat_result = user_proxy.initiate_chat(assistant, message=f"Translate this sentence into HED annotations:\n{description}")
    # print(json.loads(chat_result.chat_history))
    chat_print, tags = print_chat_result(chat_result)
    return {"tags": tags, "chat": chat_print}

def print_chat_result(chat_result):
    result_str = ""
    before_last = ""
    for message in chat_result.chat_history:
        if not "tool_calls" in message:
            if message['content'] == "TERMINATE":
                result_str += "Finish suggesting\n"
                break
            else:
                result_str += f"{message['content']}\n"
            if message['role'] == "user":
                before_last = message['content']
            result_str += "\n"
    print(before_last)
    # tags = before_last[before_last.find("'")+1:before_last.rfind("'")]
    # extract the string in the '' of the last message from the right
    # tags = tags[:tags.rfind("'")]
    tags = before_last[before_last[:before_last.rfind("'")].rfind("'")+1:before_last.rfind("'")]
    schema = load_schema_version('8.3.0')
    hedObj = HedString(tags, schema)
    short_string = hedObj.get_as_form('short_tag')
    result_str += f"\nConvert to short form: \n{short_string}\n"
    return result_str, short_string