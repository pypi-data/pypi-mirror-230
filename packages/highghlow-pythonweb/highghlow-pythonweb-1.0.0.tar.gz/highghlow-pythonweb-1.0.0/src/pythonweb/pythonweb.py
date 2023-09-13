import flask as _flask
import json as _json

class code:
    def __init__(self, code : int):
        self.code = code
    def __int__(self):
        return self.code
    def __repr__(self):
        return f"code({self.code})"

class MissingArguments(Exception):
    codename = "MISSING_ARGUMENTS"
    verbose = "{0} is missing {1} argument"

class Server(_flask.Flask):
    def get_endpoints(self):
        try:
            return self._endpoints
        except AttributeError:
            return []
    
    def set_endpoints(self, val):
        self._endpoints = val
        
    endpoints = property(get_endpoints, set_endpoints)
    
    def api(self, url : str, form=False):
        def wrapper(f):
            self.endpoints += [("API", url, f)]
            def on_request(web=True, **kwargs):

                # EXTRACTING PARAMS
                if web == True:
                    if not form:
                        if _flask.request.args:
                            params = _flask.request.args.to_dict()
                        else:
                            params = _flask.request.get_json(force=True)
                    else:
                        params = dict(_flask.request.form)
                else:
                    params = web

                # EXECUTING
                try:

                    print("[PYWEB] Processing api call for", url, "on", f.__name__)
                    api_result = f(**params, **kwargs)
                    print("[PYWEB] Successful api call for", url)
                    if web == True:

                        if type(api_result) == _flask.Response:
                            return api_result
                        status_code = 200
                        if isinstance(api_result, dict):
                            status_code = api_result.get("status_code", 200)
                        elif isinstance(api_result, tuple):
                            if len(api_result) == 2:
                                if isinstance(api_result[1]):
                                    api_result, status_code = api_result
                        
                        return _flask.Response(_json.dumps(api_result), content_type="text/json", status=status_code)
                    else:
                        return api_result

                except (Exception, SyntaxError) as exception:
                    print(exception.args)
                    # EXCEPTION
                    ecls = exception.__class__
                    error = ecls.__name__

                    # PROCESSING CODENAME
                    codename = getattr(ecls, "codename", None)

                    if codename:
                        error = codename

                    if exception.args and not isinstance(exception.args[0], code):
                        message = exception.args
                    else:
                        message = None
                    status_code = getattr(ecls, "code", 500)

                    # PROCESSING CUSTOM CODE
                    if isinstance(exception.args[-1], code):
                        status_code = int(exception.args[-1])
                    
                    verbose = getattr(exception, "verbose", None)
                    if verbose:
                        verbose = verbose.format(*exception.args)

                    print("[PYWEB] Error when executing api call for", url, error+":", message)
                    return _flask.Response(_json.dumps({
                        "error":error, "message":message, "verbose":verbose
                    }), content_type="text/json", status=status_code)

            on_request.__name__ = f.__name__
            super(Server, self).route(url, methods=["POST"])(on_request)
            return on_request
        return wrapper
    def route(self, rule: str, **options):
        def wrapper(f):
            self.endpoints += [("WEB", rule, f)]
            return super(Server, self).route(rule, **options)(f)
        return wrapper

class _universal_script(str):
    @property
    def WRAPPED(self):
        return "<script>"+self+"</script>"

    @property
    def EMBEDED(self):
        return _flask.Markup("<script>"+self+"</script>")

CONNECTION_SCRIPT = _universal_script("""
const makeRequest = function (url, payload={}, method="POST") {
    console.log("[PYWEB(C_S)] Requesting api route "+url+" with params: "+JSON.stringify(payload))

    const Http = new XMLHttpRequest();
    Http.open(method, url);
    Http.setRequestHeader("Accept", "application/json");
    Http.setRequestHeader("Content-Type", "application/json");
    Http.timeout = 10000;
    Http.send(JSON.stringify(payload));

    return new Promise(function(resolve, reject) {
        Http.onload = (e) => {
            console.log("[PYWEB(C_S)] Result for api route "+url+" is: "+Http.responseText);
            resolve({
                "data": JSON.parse(Http.responseText),
                "status": Http.status,
                "statusText": Http.statusText
            });
        }
        Http.onerror = (e) => {
            console.log("[PYWEB(C_S)] !Error for api route "+url+" is: "+Http.responseText);
            reject();
        }
        Http.ontimeout = (e) => {
            console.log("[PYWEB(C_S)] !Timeout for api route "+url+" is: "+Http.responseText);
            reject();
        }
    })
}
""")

__all__ = ["with_code", "code", "Server", "CONNECTION_SCRIPT"]