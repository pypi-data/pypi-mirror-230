# Canvas Parent API
This is an async wrapper for the [Canvas API](https://canvas.instructure.com/doc/api/) from Instructure.  There are a few types of objects this will retrieve based on the assumption that you are a parent with students enrolled with Canvas.  

The types of objects that can be returned include:
 - Observees (Students)
 - Courses
 - Assignments
 - Submissions

This module is provided for use with the Home Assistant custom integration [Canvas](https://github.com/schwartzpub/canvas_hassio) however it could be useful as a standalone module for your own projects as well.

## Installing
To install the module use:
```python
python3 -m pip install canvas-parent-api
```

### Get API Token
If you are a parent, you will have a Canvas Parent account.  To get an API token, you must sign into the Canvas Parent application from a web browser.  This is typically using: https://<yourdistrict>.instructure.com/login/canvas

Once you have signed into your account, navigate to Account > Settings.

Under "Approved Integrations" click "+ New Access Token" to create a new API Token.

Enter a Purpose and Expiration date (blank for no expiration).

Be sure to save your API token, as you will have to generate a new token if this is lost.

### Usage
Example usage to get students, printing names:
```python
import asyncio
from canvas_parent_api import Canvas

base_url = "https://school.instructure.com"
api_token = "randomstringthatisntreallyatoken"

async def get_students():
	client = Canvas(f"{base_url}",f"{api_token}")
	return await client.observees()

students = asyncio.run(get_students())

for student in students:
	print(student.name)
```

### Patch Notes

 - 0.0.12:
    - Added pagination support to automatically paginate to end of available requests

 - 0.0.9:
	- Added Submissions