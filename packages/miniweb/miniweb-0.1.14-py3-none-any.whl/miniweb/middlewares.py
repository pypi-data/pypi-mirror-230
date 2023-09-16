



from .core import Middleware
from .request import HttpRequest
from .response import HttpResponse


class OptionsHandlerMiddleware(Middleware):
    """Handle OPTIONS request globally.
    """

    def __call__(self, http_request:HttpRequest, http_response:HttpResponse) -> None:
        """If request.method equals OPTIONS, then do options handler and stop the real bussiness process.

        So that the OptionsHandlerMiddleware must be put before other bussiness middlewares.
        """
        if http_request.method == "OPTIONS":
            return self.options_handler(http_request, http_response)
        else:
            return self.get_response(http_request, http_response)

    def options_handler(self, http_request, http_response):
        if http_request.path == "*": # returns globally permitted methods
            permitted_methods = http_request.application.global_allowed_methods
        else: # find the handler of the given path
            handler = http_request.application.router.dispatch(http_request.path)
            if not handler:
                return http_response.not_found()
            else:
                permitted_methods = getattr(handler, "allowed_methods", http_request.application.global_allowed_methods)
        if not "OPTIONS" in permitted_methods:
            permitted_methods = ["OPTIONS"] + permitted_methods
        http_response.set_header("Allow", ", ".join(permitted_methods))
        return http_response.response_text(content=None)
