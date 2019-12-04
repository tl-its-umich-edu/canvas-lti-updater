# Updating MWrite LTI links courses and assignments in sites
import json
from canvasapi import Canvas
from collections import OrderedDict

#sites_to_update = [109190]

with open("config.json") as config_file:
    CONFIG = json.load(config_file)

CANVAS = Canvas(CONFIG.get("API_URL"), CONFIG.get("API_KEY"))

with open(CONFIG.get("LTI_JSON_FILE")) as json_file:
    data = json.load(json_file)
    LTI_KEY, LTI_SECRET = list(data.items())[0]

with open(CONFIG.get("LTI_XML_FILE")) as xml_file:
    LTI_XML = xml_file.read()

for site in CONFIG.get("SITES_TO_UPDATE"):
    # Get the course
    course = CANVAS.get_course(site)
    # Find and delete the existing LTI tool
    print ("Searching for M-Write tool")
    tools = course.get_external_tools()
    for tool in tools:
        if "M-Write" in tool.name:
            print (f"Found tool named {tool.name}, deleting")
            tool.delete()
    # Re-add the new tool
    course.create_external_tool("M-Write Peer Review", "anonymous",
        LTI_KEY, LTI_SECRET, config_xml=LTI_XML, config_type="by_xml")
    # Get all the assignments and relink lti onesthem
    assignments = course.get_assignments()
    for assignment in assignments:
        if hasattr(assignment, 'external_tool_tag_attributes'):
            print (f"Found LTI Assignment {assignment.name}, updating external URL")
            assignment.edit(assignment={'external_tool_tag_attributes': 
                {'url': CONFIG.get("LTI_NEW_LAUNCH")}})