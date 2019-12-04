Script to replace all instances of M-Write LTI tool in Canvas
Requires canvasapi package

To run
* Get your API token for a user that is admin and can update all sites
  * In Canvas Account -> Settings -> New Access Token
  * It's fine if it expires today
* Get the XML and JSON files for the LTI and put them in this directory
* Copy config_sample.json to config.json and fill out the config.json with the values including the sites to update
* Run the script with Python 3