#!/usr/bin/env python3
# Description: This file takes in a html file from extract-regexes.pl, finds all the script 
# tags, and combine the JS in them into a temporary js file. It then sends the path of the
# temporary js file back to extract-regexes.pl to let it pipeline the js file to the javascript
# extractor. After extract-regexes.pl finishes extracting, The temporary JS file will be 
# deleted by extract-regexes.pl. 

from bs4 import BeautifulSoup
import sys
import subprocess
import json
import tempfile
import os

def extract_js(file_path):
    with open(file_path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    js_from_html = ''
    for script in soup.find_all('script'):
        js_from_html += script.string

    return js_from_html

def extract_regexes(json_tempfile):
    output = subprocess.run([os.path.join(os.getcwd(), 'extract-regexes.pl'), json_tempfile.name], 
        capture_output=True, text=True)
    return json.loads(output.stdout)

file_path = sys.argv[1]
js_from_html = extract_js(file_path)

# create temp-js-content.js based on the location of extract-regexes.pl
js_tempfile = tempfile.NamedTemporaryFile(suffix='.js', mode='w+t')
js_tempfile.writelines(js_from_html)
js_tempfile.seek(0)

# create temp json file to pass to the meta-program
json_tempfile = tempfile.NamedTemporaryFile(suffix='.json', mode='w+t')
json_tempfile.writelines(json.dumps({"file": js_tempfile.name, "language": "javascript"}))
json_tempfile.seek(0)

# call the meta-program 
output_json = extract_regexes(json_tempfile)
output_json['file'] = file_path
return_string = json.dumps(output_json)
print(return_string, end = '')

# delete the temp js and json file
js_tempfile.close()
json_tempfile.close()
