// create a global empty dictionary variable named eventsinfo 
let eventsinfo = {};
let jsontree = null;
let eventstsv = "";
let eventstable = null;
// create a function to populate the field-select with the fields from the json file
function populateFields() {
    // clear the jsontree
    if (jsontree) {
    jsonview.destroy(jsontree);
    }

    // get the file input
    const fileInput = document.getElementById('file');
    // get the file
    const file = fileInput.files[0];

    // create a new FileReader
    const reader = new FileReader();

    reader.onload = function(event) {
    const fileContent = event.target.result;
    try {
        const jsonData = JSON.parse(fileContent);
        eventsinfo = jsonData;
        // display the content of the json file
        eventsinfoJson = JSON.stringify(eventsinfo, null, 2);
        jsontree = jsonview.renderJSON(eventsinfoJson, document.querySelector('#json-display'));
        jsonview.expand(jsontree);

        fields = getKeysFromEventsJson(eventsinfo);
        // get the field-select
        const fieldSelect = document.getElementById('field-select');
        // clear the field-select
        fieldSelect.innerHTML = '';
        // populate the field-select
        fields.forEach(field => {
        const option = document.createElement('option');
        option.value = field;
        option.text = field;
        fieldSelect.appendChild(option);
        });

        // populate the value-select with the values of the first field
        console.log('jere')
        populateFieldValues(fields[0]);
    } catch (error) {
        console.error('Error parsing JSON:', error);
        alert('Error parsing JSON file.');
    }
    };

    reader.readAsText(file);
}

function populateFieldValues(field) {
    fieldDict = eventsinfo[field];
    console.log(fieldDict)
    // check if key 'Levels' or 'HED' exists in the valuesDict
    if ('HED' in fieldDict) {
        valuesDict = fieldDict['HED'];
    } else if ('Levels' in fieldDict) {
        valuesDict = fieldDict['Levels'];
    } else {
        alert('Key "Levels" or "HED" not found in valuesDict');
        return;
    }
    values = Object.keys(valuesDict);
    // populate the value-select with the values
    const valueSelect = document.getElementById('value-select');
    valueSelect.innerHTML = '';
    values.forEach(value => {
    const option = document.createElement('option');
    option.value = value;
    option.text = value;
    valueSelect.appendChild(option);
    });
}

function getKeysFromEventsJson(data) {
    // parse the data dictionary and get the keys
    const keys = Object.keys(data);
    return keys
}

function downloadEventsJson() {
    // get the eventsjson content
    const eventsjson = JSON.stringify(eventsinfo, null, 2);
    // create a new Blob
    const blob = new Blob([eventsjson], { type: 'application/json' });
    // create a new URL
    const url = URL.createObjectURL(blob);
    // create a new anchor element
    const a = document.createElement('a');
    // set the href attribute of the anchor element
    a.href = url;
    // set the download attribute of the anchor element
    a.download = 'events.json';
    // click the anchor element
    a.click();
    // revoke the URL
    URL.revokeObjectURL(url);
}

// add an event listener to the hedAnnotation textarea
document.getElementById('hedAnnotation').addEventListener('input', updateEventsJson);
function showSchema() {
    window.open('https://www.hedtags.org/display_hed.html', 'HED Schema browser', 'popup=true');
}
/**
 * When user select new value, display the associating HED from eventsinfo dictionary in the eventsjson textarea
 */
function getHedAnnotation() {
    // get the selected field
    const field = document.getElementById('field-select').value;
    // get the selected value
    const value = document.getElementById('value-select').value;
    // get the HED annotation
    const hedAnnotation = eventsinfo[field]['HED'][value];
    // update the hedAnnotation textarea
    const view_indentation = $("#view_indentation").data("state")
    if (view_indentation) {
    document.getElementById('hedAnnotation').value = indent_hed(hedAnnotation);
    } else {
    document.getElementById('hedAnnotation').value = hedAnnotation;
    }
}

function updateEventsJson() {
    // get the selected field
    const field = document.getElementById('field-select').value;
    // get the selected value
    const value = document.getElementById('value-select').value;
    // get the HED annotation
    let hedAnnotation = document.getElementById('hedAnnotation').value;
    // update the eventsinfo dictionary
    if ($("#view_indentation").data('state')) {
    hedAnnotation = unindent_hed(hedAnnotation);
    }
    eventsinfo[field]['HED'][value] = hedAnnotation;
    // update the eventsjson textarea
    eventsinfoJson = JSON.stringify(eventsinfo, null, 2);

    // render json data as dom without creating tree
    if (jsontree) {
    jsonview.destroy(jsontree);
    }
    jsontree = jsonview.renderJSON(eventsinfoJson, document.querySelector('#json-display'));
    jsonview.expand(jsontree);
}

function setIndentationMode() {
    const view_indentation = $("#view_indentation").data("state")
    if (view_indentation) {
    $("#view_indentation").removeClass('checked')
    $("#view_indentation").data('state', false)
    } else {
    $("#view_indentation").addClass('checked')
    $("#view_indentation").data('state', true)
    }
    getHedAnnotation()
}

function validateEventsJson() {
    eventsinfoJson = JSON.stringify(eventsinfo, null, 2); 
    $.post( "http://127.0.0.1:8000/validate", eventsinfoJson, function( data ) {
    alert(data);
    });
}

function indent_hed(hed_string) {
            var level_open = []
            var level = 0
            var final = ""
            var prev = ''
            for (let i = 0; i < hed_string.length; i++) {
                c = hed_string[i];
                if (c == "(") {
                    level_open.push(level)
                    final += "\n" + "\t".repeat(level) + c
                    level += 1	
                }
                else if (c == ")") {
                    level = level_open.pop()
                    if (prev == ")") {
                        final += "\n" + "\t".repeat(level) + c
                    }
                    else {
                        final += c
                    }
                }
                else {
                    final += c
                }
                prev = c
            }
            return final
        }

function unindent_hed(hed_string) {
    // strip all tabs and newlines
    return hed_string.replace(/[\t\n]/g, '');
}

function addDescription() {
    // get the selected field
    const field = document.getElementById('field-select').value;
    // get the selected value
    const value = document.getElementById('value-select').value;
    // get the HED annotation
    let hedAnnotation = document.getElementById('hedAnnotation').value;
    // update the eventsinfo dictionary
    if ($("#view_indentation").data('state')) {
    hedAnnotation = unindent_hed(hedAnnotation);
    }
    eventsinfo[field]['HED'][value] = hedAnnotation;
}

function initTable(id, columnHeader, tabledata) {
    const table = $(id);
    // clear the table
    table.html(""); //empty();
    if (DataTable.isDataTable(id)) {
    // destroy datatable
    var datatable = new DataTable(id);
    datatable.clear();
    datatable.destroy();
    }
    
    // add header row using the columnHeader
    const thead = document.createElement('thead');
    const tr = document.createElement('tr');
    for (let i = 0; i < columnHeader.length; i++) {
    const th = document.createElement('th');
    th.textContent = columnHeader[i];
    tr.append(th);
    }
    thead.append(tr);
    table.append(thead);
    
    // add body rows using the tabledata
    const tbody = document.createElement('tbody');
    for (let i = 0; i < tabledata.length; i++) {
    const row = tabledata[i];
    const tr = document.createElement('tr');
    for (let j = 0; j < row.length; j++) {
        const td = document.createElement('td');
        td.textContent = row[j];
        tr.append(td);
    }
    tbody.append(tr);
    }
    table.append(tbody);

    // initialize the datatable
    // $(id).DataTable({
    //   retrieve: true,
    //   paging: false,
    //   scrollY: 600
    // });
}

function importEventsTSV() {
    // get the file input
    const fileInput = document.getElementById('eventstsv');
    // get the file
    const file = fileInput.files[0];
    // create a new FileReader
    const reader = new FileReader();

    const table = $('#tsv-display');
    reader.onload = function(event) {
    const fileContent = event.target.result;
    eventstsv = fileContent;
    try {
        const tsvdata = d3.tsvParse(fileContent);
        // for each object element of tsvdata strip the keys and only store values in an array
        tabledata = [];
        tsvdata.forEach(element => {
        tabledata.push(Object.values(element));
        });
        const columnHeader = Object.keys(tsvdata[0]);
        initTable('#tsv-display', columnHeader, tabledata);
    } catch (error) {
        console.error('Error parsing tsv:', error);
        alert('Error parsing tsv file.');
    }
    };

    reader.readAsText(file);
}

function assembleHED() {
    eventsinfoJson = JSON.stringify(eventsinfo, null, 2);
    columnHeader = [];
    tabledata = [];
    $.post( "http://127.0.0.1:8000/assemble", {"eventsjson": eventsinfoJson, "eventstsv": eventstsv} , function( hed ) {
    // if hed is not empty
    if (hed) {
        tabledata = hed['data'];
        columnHeader = hed['header'];
        initTable('#tsv-display', columnHeader, tabledata);
    }
    else {
        alert('Error assembling HED');
    }
    });
}

function getDescription() {
    document.getElementById('event-description').value = "";
    const field = document.getElementById('field-select').value;
    const value = document.getElementById('value-select').value;
    if ('Levels' in eventsinfo[field]) {
    if (value in eventsinfo[field]['Levels'])
        document.getElementById('event-description').value = eventsinfo[field]['Levels'][value];
    }
}

function saveDescription() {
    // get the selected field
    const field = document.getElementById('field-select').value;
    // get the selected value
    const value = document.getElementById('value-select').value;
    // get the description
    const description = document.getElementById('event-description').value;
    // update the eventsinfo dictionary
    if (!('Levels' in eventsinfo[field])) {
    eventsinfo[field]['Levels'] = {};
    }
    eventsinfo[field]['Levels'][value] = description;
    // update the eventsjson textarea
    eventsinfoJson = JSON.stringify(eventsinfo, null, 2);
    // render json data as dom without creating tree
    if (jsontree) {
    jsonview.destroy(jsontree);
    }
    jsontree = jsonview.renderJSON(eventsinfoJson, document.querySelector('#json-display'));
    jsonview.expand(jsontree);
    // close the modal event-description-modal
    $('#event-description-modal').modal('toggle');
}