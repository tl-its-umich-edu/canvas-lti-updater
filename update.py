# Updating MWrite LTI links courses and assignments in sites
import json
from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist
from collections import OrderedDict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info(f"Processing course {site}")
    # Get the course
    try:
        course = CANVAS.get_course(site)
    except ResourceDoesNotExist as e:
        logger.warning("Problem retrieving course, skipping", e)
        continue
    # Find and delete the existing LTI tool
    logger.info ("Searching for M-Write tool")
    tools = course.get_external_tools()
    tool_found = False
    for tool in tools:
        if "M-Write" in tool.name:
            logger.info(f"Found tool named {tool.name}, deleting")
            tool.delete()
            logger.info("Creating new M-Write Tool")
            # Re-add the new tool
            tool_found = True
    # If we found an LTI tool    
    if tool_found:
        course.create_external_tool("M-Write Peer Review", "anonymous",
            LTI_KEY, LTI_SECRET, config_xml=LTI_XML, config_type="by_xml")
        # Get all the assignments and relink lti onesthem
        assignments = course.get_assignments()
        for assignment in assignments:
            if hasattr(assignment, 'external_tool_tag_attributes') and \
                'mwrite' in assignment.external_tool_tag_attributes.get('url'):
                logger.info(f"Found LTI Assignment {assignment.name}, updating external URL")
                # TODO: This could be pulled out of the XML
                assignment.edit(assignment={'external_tool_tag_attributes': 
                    {'url': CONFIG.get("LTI_NEW_LAUNCH")}})