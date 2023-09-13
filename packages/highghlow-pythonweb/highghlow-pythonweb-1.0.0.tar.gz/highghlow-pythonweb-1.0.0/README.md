# PythonWEB
A Flask wrapper for easy RESTful api development
## Quickstart
```python
import pythonweb

app = pythonweb.Server()

class ExampleException(Exception):
    codename = "ERR_EXAMPLE"
    verbose = "This is an example exception. The specified exception params would be here: {0} and here: {1}"
    code = 501

@app.api("/api/example", form=False) # form=true means that you can use this api route as a form handler
def example_endpoint(param1 : int, param2 : bool): # Type annotations are not used by the server
    if param2:
        raise ExampleException(param1, param2, "Param") # 501 {"error":"ERR_EXAMPLE", "message":[param1, param2, "Param"], "verbose":"This is an example..."}
    return {"some_json":param1+1}
```