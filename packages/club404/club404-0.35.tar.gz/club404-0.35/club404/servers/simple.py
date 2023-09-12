import json

from urllib import parse
from functools import partial

from http.server import HTTPServer, SimpleHTTPRequestHandler

from club404.router import WebRequest, WebResponse
from club404.servers.abstract import AbstractServer


class Request(WebRequest):
    # Wrap your request object into serializable object
    def __init__(self, ctx): super().__init__(
        verb=ctx.command,
        path=ctx.path,
        head=ctx.headers,
        body=self.body(ctx, ctx.headers),
        params=self.query(ctx),
    )

    def query(self, ctx):
        path_parts = ctx.path.split('?')
        if len(path_parts) > 1:
            return parse.parse_qs(path_parts[1])
        return {}    

    def body(self, ctx, headers):
        # Only try and parse the body for known methods (eg: POST, PUT)
        if not ctx.command in ["POST", "PUT", "PATCH"]:
            return None 
        
        # Parse the body according to the content type
        ctype = headers['content-type'] if 'content-type' in headers else ''
        length = int(ctx.headers.get('content-length'))
        match ctype:
            case 'application/json':
                input = ctx.rfile.read(length).decode('utf8')
                data = json.loads(input)
            case 'application/x-www-form-urlencoded':
                input = ctx.rfile.read(length).decode('utf8')
                form = parse.parse_qs(input, keep_blank_values=1)
                data = {}
                for key in form:
                    if len(form[key]) > 1:
                        data[key] = form[key]
                    elif len(form[key]) == 1:
                        data[key] = form[key][0]
            case _:
                message = 'Content type "%s" cannot be parsed into a body.' % ctype
                raise Exception(message)

        return data


class Response(WebResponse):
    __sent = False

    # Wrap your response object into serializable object
    def __init__(self, ctx, req): super().__init__(
        verb=ctx.command,
        path=ctx.path,
        head={},
        body=None
    )

    def redirect(self, ctx, location):
        self.reply(ctx, 302, head={'Location': location})

    def respond(self, ctx, status=200, headers={}, message=""):
        if self.__sent:
            raise Exception('Status already sent')
        ctx.send_response(status, message)
        self.__sent = True

        # Finilize the headers
        for key in headers:  # Append headers
            self.head[key] = headers[key]

    def reply(self, ctx, body=None, head={}):
        for key in head:  # Append headers
            self.head[key] = head[key]

        # Send status code (if not sent)
        if not self.__sent:
            self.respond(ctx, self.status)

        # Reply with headers (if not already sent)
        for key in self.head:
            ctx.send_header(key, self.head[key])
        ctx.end_headers()

        # Send the response UTF encoded (if defined)
        if body:
            ctx.wfile.write(body.encode('utf8'))


class Handler(SimpleHTTPRequestHandler):
    # Bind your route handlers into our router's path resolvers
    def __init__(self, server, *extra_args, **kwargs):
        self.reply = server.reply
        self.config = server.config
        super().__init__(directory=server.config.static, *extra_args, **kwargs)

    def do_DEFAULT(self, verb):
        # If no custom routes were triggered, this function will be called..
        # We will check for default actions in this order:
        #  1) config.static - (PATH) Serve static content
        #  2) Fallback: Send "Not found"
        if verb == "GET" and self.config.static:
            # Serve contents from the specified static folder
            return self.do_STATIC()
        else:
            # The default action is to reply: "Not found"
            self.send_response(404, "Not Found")
            self.end_headers()

    def do_REPLY(self, verb): self.reply(verb, self.path, self)
    def do_STATIC(self): super().do_GET()
    def do_HEAD(self): self.do_GET()
    def do_GET(self): self.do_REPLY("GET")
    def do_POST(self): self.do_REPLY("POST")
    def do_PUT(self): self.do_REPLY("PUT")
    def do_PATCH(self): self.do_REPLY("PATCH")
    def do_DELETE(self): self.do_REPLY("DELETE")


class SimpleServer(AbstractServer):

    def __init__(self, prefix='', config=None, app=None):
        # Initialise the base server instance
        super().__init__(prefix, config=config, app=app)

    def start(self):
        # Create a new server instance that will be serving our routes
        self.host = (self.config.host, self.config.port)
        self.app = HTTPServer(self.host, partial(Handler, self))

        # Start the server using the target (request handler) type
        self.onStart()
        self.app.serve_forever()

    def static(self, path):
        # Set the static folder (will be set when server starts)
        self.config.static = path

    def route(self, verb, route):
        print(' + [ %-5s ] %s' % (verb, route))

        def decorator(action):
            # Register this rout, to be searched and resolved in SimpleServer.reply(verb, path, ctx)
            http = self.routes
            http[verb] = {} if not verb in http else http[verb]
            http[verb][route] = action
            return action

        return decorator

    def reply(self, verb, path, ctx):
        # This method is called from the `Handler` interface, each time a route is intercepted
        # See if we can match a route to the current verb
        action = self.find_route(verb, path)
        if not action:
            # Not found: delegate to the default route handler
            return ctx.do_DEFAULT(verb)

        # Service the incomming request with the specified handler
        req = Request(ctx)
        resp = Response(ctx, req)
        data = self.render(action)(req, resp)

        # Write the headers of the response
        ctx.send_response(resp.status)
        for key in resp.head:
            ctx.send_header(key, resp.head[key])
        ctx.end_headers()

        # Send the response UTF encoded (if defined)
        if type(data) == str:
            ctx.wfile.write(data.encode('utf8'))
        elif data:
            raise Exception('Response could not be encoded to text: %s' % data)
