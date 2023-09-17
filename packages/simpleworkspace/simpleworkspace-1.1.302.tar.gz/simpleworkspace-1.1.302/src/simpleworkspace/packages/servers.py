from base64 import b64encode
from http import HTTPStatus
from logging import Logger
import http.server
import socketserver
from socketserver import BaseRequestHandler
from urllib.parse import urlparse, parse_qs
from simpleworkspace.logproviders import DummyLogger, StdoutLogger
import ssl
import subprocess


class BasicRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Class should always be derived

    Methods that may be overridden:
    - GetPage_Index()       , a placeholder/boilerplate function runs on entry path 'localhost/' and query empty
    - OnRequest_Action()    , a placeholder/boilerplate function runs on entry path 'localhost/' and query with 'action=xxx' specified
    - do_GET()              , for more complex servers this one should be fully overriden to desired specs, you may copy & paste it and edit that for a premade snippet
    """

    # just to update intellisense
    server = None  # type: BasicServer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Exceptions:
        class StopRequest(Exception):
            pass

    # override, original writes to standard outputs, which fails if app is pyw
    def log_message(self, format, *args):
        self.server.logger.debug(f"{self.address_string()} - {format % args}")

    def SendResponse_Raw(self, data: str, statusCode=HTTPStatus.OK, contentType="text/html", customHeaders: dict[str, str] = {}):
        self.send_response(statusCode.value)
        customHeaders["Content-type"] = contentType  # incase of duplicate, contentType param is preffered
        for key, value in customHeaders.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data.encode())
        return

    def _Routine_BasicAuth(self):
        if self.server._config_auth_basicKey is None:
            # no auth configured
            return

        if self.headers.get("Authorization") == self.server._config_auth_basicKey:
            return

        self.SendResponse_Raw("Authorization required.", HTTPStatus.UNAUTHORIZED, customHeaders={"WWW-Authenticate": 'Basic realm="Login Required"'})
        raise self.Exceptions.StopRequest()

    def GetPage_Index(self):
        pass

    def OnRequest_Action(self, action: str, data: str):
        pass

    def do_GET(self):
        parsedUrl = urlparse(self.path)
        query_components = parse_qs(parsedUrl.query)
        if parsedUrl.path == "/":
            if parsedUrl.query == "":
                self.GetPage_Index()
            elif "action" in query_components:
                action = query_components["action"][0]
                data = query_components["data"][0] if "data" in query_components else None
                self.OnRequest_Action(action, data)
            return
        return self.SendResponse_Raw("Not Found", HTTPStatus.NOT_FOUND)

    def _BeforeHTTPCommand(self):
        # when basic auth is enabled, checks if current client is authorized
        self._Routine_BasicAuth()  # throws a stoprequest exception if not passed

    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            try:
                self.raw_requestline = self.rfile.readline(65537)
                if len(self.raw_requestline) > 65536:
                    self.requestline = ""
                    self.request_version = ""
                    self.command = ""
                    self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                    return
                if not self.raw_requestline:
                    self.close_connection = True
                    return
                if not self.parse_request():
                    # An error code has been sent, just exit
                    return
                mname = "do_" + self.command
                if not hasattr(self, mname):
                    self.send_error(HTTPStatus.NOT_IMPLEMENTED, "Unsupported method (%r)" % self.command)
                    return
                method = getattr(self, mname)
                self._BeforeHTTPCommand()
                method()
            except self.Exceptions.StopRequest:
                pass  # a graceful request cancellation

            self.wfile.flush()  # actually send the response if not already done.
        except TimeoutError as e:
            # a read or a write timed out.  Discard this connection
            self.server.logger.exception("Request timed out")
            self.close_connection = True
            return


class BasicServer(socketserver.ThreadingTCPServer):
    def __init__(self, port: int, requestHandler: BaseRequestHandler):
        self._config_auth_basicKey = None
        self._config_ssl_file_cert = None
        self._config_ssl_file_key = None

        self.logger = DummyLogger.GetLogger()

        super().__init__(("", port), requestHandler, bind_and_activate=False)

    def UseLogger(self, logger: Logger):
        self.logger = logger

    def UseAuthorization_Basic(self, username: str, password: str):
        """Uses http basic auth before any request is accepted, one of username or password can be left empty"""
        self._config_auth_basicKey = "Basic " + b64encode(f"{username}:{password}".encode()).decode()

    def GenerateSelfSignedSSLCertificates(self, certificateOutPath = 'cert.crt', PrivateKeyOutPath = 'cert.key'):
        if(not certificateOutPath.endswith(".crt")) or (not PrivateKeyOutPath.endswith('.key')):
            raise Exception("wrong file extensions used for certs")
        result = subprocess.run(
            ["openssl", 
                "req", "-x509", ""
                "-newkey", "rsa:4096", 
                "-keyout", PrivateKeyOutPath, "-out", certificateOutPath, 
                "-days", str(365), 
                "-nodes",
                "-subj", "/C=US/CN=*"
            ],text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:  # something went bad
            raise Exception(result.stderr, result.stdout)

    def UseSSL(self, certificatePath: str, PrivateKeyPath: str):
        self._config_ssl_file_cert = certificatePath
        self._config_ssl_file_key = PrivateKeyPath

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        if self._config_ssl_file_cert is not None:
            self.socket = ssl.wrap_socket(self.socket, keyfile=self._config_ssl_file_key, certfile=self._config_ssl_file_cert, server_side=True)
        try:
            self.server_bind()
            self.server_activate()
        except:
            self.server_close()
            raise

        self.logger.info(f"Server started at port {self.server_address[1]}")
        return super().serve_forever(poll_interval)


# BasicRequestHandler would be overriden for implementer
# server = BasicServer(8082, BasicRequestHandler)
# server.UseLogger(StdoutLogger.GetLogger())
# server.UseAuthorization_Basic("admin", "123")
# server.serve_forever()
