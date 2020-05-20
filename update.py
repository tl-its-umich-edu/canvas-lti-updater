# Update MPR LTI courses and their assignments
import json
import logging

from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

with open("config.json") as config_file:
    CONFIG = json.load(config_file)

dryRun = (CONFIG.get('DRY_RUN', False) == True)

if (dryRun):
    logger.info('Dry run mode enabled ("DRY_RUN" is "true" in "config.json")')
    dryRunText = '(dry run) not '
else:
    dryRunText = ''

CANVAS = Canvas(CONFIG.get("API_URL"), CONFIG.get("API_TOKEN"))

with open(CONFIG.get("LTI_JSON_FILE")) as json_file:
    data = json.load(json_file)
    LTI_KEY, LTI_SECRET = list(data.items())[0]

with open(CONFIG.get("LTI_XML_FILE")) as xml_file:
    LTI_XML = xml_file.read()

for courseId in CONFIG.get('COURSE_IDS_TO_UPDATE'):
    logger.info(f"Searching for course by ID ({courseId})")
    # Get the course
    try:
        course = CANVAS.get_course(courseId)
        logger.info(f'Found course "{course.name}" ({course.id})')
    except ResourceDoesNotExist:
        logger.warning(f'Problem retrieving course by ID ({courseId}), skipping...', exc_info=True)
        continue

    # Find and delete the old LTI tool by launch URL
    # Although unlikely, it's possible that a course may have multiple tools defined with the
    # same launch URL.  This code removes ALL tools with that URL and replaces them with a
    # single instance of the new tool.  It probably will not cause us trouble, but it's
    # important to be aware of this possibility.
    logger.info("Searching for old tool(s) by launch URL...")

    tools = course.get_external_tools()
    tool_found = False

    for tool in tools:
        if tool.url == CONFIG.get('LTI_OLD_LAUNCH'):
            tool_found = True
            logger.info(f'Found old tool named "{tool.name}" ({tool.id}), {dryRunText}deleting')
            if (not dryRun):
                tool.delete()

    if not tool_found:
        logger.warning(f'No old tool found in course '
                       f'"{course.name}" ({course.id}), skipping...')
        continue

    # Old LTI tool(s) were found and deleted, so add new tool
    logger.info(f'{dryRunText}Creating new tool...')
    if (not dryRun):
        # TODO: get tool name from XML
        privacyLevel = "anonymous"
        newTool = course.create_external_tool(
            "M-Write Peer Review", privacyLevel,
            LTI_KEY, LTI_SECRET, config_xml=LTI_XML,
            config_type="by_xml")
        logger.info(f'Created new tool "{newTool.name}" ({newTool.id}) '
                    f'in course "{course.name}" ({course.id})')

    logger.info("Searching for assignments with old tool by launch URL...")

    # Get assignments and re-configure those with old LTI
    assignments = course.get_assignments()
    for assignment in assignments:
        if (
                hasattr(assignment, 'external_tool_tag_attributes') and
                (assignment.external_tool_tag_attributes.get('url') == CONFIG.get(
                    'LTI_OLD_LAUNCH'))
        ):
            logger.info(
                f'Found external tool for Assignment "{assignment.name}" ({assignment.id}), '
                f'{dryRunText}updating tool URL')
            if (not dryRun):
                # TODO: get tool launch URL from XML
                assignment.edit(assignment={'external_tool_tag_attributes':
                                                {'url': CONFIG.get("LTI_NEW_LAUNCH")}})
