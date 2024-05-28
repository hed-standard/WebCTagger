let schemaNodes = [];
let allSchemaNodes = [];
let inLibraryNodes = [];
let suggestedTagsDict = {};
let useNewFormat = true;
let github_endpoint = "https://api.github.com/repos/hed-standard/hed-schemas/contents";
let github_raw_endpoint = "https://raw.githubusercontent.com/hed-standard/hed-schemas/main";

function getSchemaNodes() {
    /**
     * Set autocomplete behavior
     */
    allowDeprecated = $("#searchDeprecatedTags")[0].checked;
    // clear array
    schemaNodes.length = 0;
    allSchemaNodes.length = 0;

    // clear dictionary
    suggestedTagsDict = {};
    /* Initialize schema nodes list and set behavior of search box */
    $("a[name='schemaNode']").each(function() {
        attributes = getAttributesOfNode($(this));
        if (!allowDeprecated && attributes.includes('deprecatedFrom')) {
            return;
        }
        
        var nodeName = $(this).attr("tag");
        allSchemaNodes.push(nodeName);

        // build the suggestedtags dictionary
        $(this).nextAll(`.attribute[name='${nodeName}']`).each(function(index) {
            var parsed = $(this).text();
            if (parsed.includes("suggestedTag")) {
                var suggestedTags = parsed.split(":")[1].trim();
                suggestedTags = suggestedTags.split(",");
                clean_suggestedTags = [];
                suggestedTags.forEach(element => {
                    // for non empty string, remove whitespace and newline characters and tab characters and push to clean_suggestedTags
                    if (element.trim().length > 0) {
                        cleaned = element.trim();
                        cleaned.replace((/[\t\n\r]/gm),"");
                        cleaned = cleaned.toLowerCase();
                        clean_suggestedTags.push(cleaned);
                    }
                });
                // for each clean_suggestedTags, add its mapping with nodeName to the suggestedTagsDict
                clean_suggestedTags.forEach(element => {
                    if (!(element in suggestedTagsDict)) {
                        suggestedTagsDict[element] = [nodeName];
                    }
                    else {
                        suggestedTagsDict[element].push(nodeName);
                    }
                });
            }
        });
    });    
    
    /* add autocomplete and search */
    console.log(allSchemaNodes.length);
    autocomplete(document.getElementById("searchTags"), allSchemaNodes, suggestedTagsDict);

    /* go to tag on enter key press */
    $("#searchTags").on('keyup', function (e) {
        if (e.key === 'Enter' || e.keyCode === 13) {
        var searchText = $("#searchTags").val();
        searchText = searchText.toLowerCase();
        searchText = capitalizeFirstLetter(searchText);
        if (allSchemaNodes.includes(searchText))
            toNode(searchText);
        }
    });
}