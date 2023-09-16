from flask import current_app
import traceback


def handle_client_exception(status=500, error_data={}, ex=None):
    """Exception handler for endpoints. This wraps error message
    in a common format and allows the user-specified return code.
    Use this in except block to return relvent error message to the
    client. For example:
    ```
    try:
        ...
    except orm_exception.NoResultFound:
        handle_exception(404, {'message': 'Object with uid={} not found.'.format(pid)})
    ```

    :param int status: HTTP status code to send back. Default 500
    :param error_data: Error data to send back
    """
    # NOTE: adjusted to output json format
    # print traceback to logger if the exception is passed in
    # we don't need to log every case that comes through here since
    # some exception are expected and handle properly outside this function
    if ex is not None:
        current_app.logger.error(traceback.format_exc())
    payload = {}
    payload['status'] = status

    if status == 500 and error_data is None:
        payload['message'] = 'Something went wrong while processing this.'
    return payload


def test_print_helper(*args):
    pos = 1
    failed = False
    msg = []
    for arg in args:
        if not arg:
            failed = True
            msg.append(f"Test failed, with condition v{pos} is {arg}")
        pos += 1
    return (not failed, msg)


class CSGServerError(Exception):
    def __init__(self, error_message, response_code, response_body):

        Exception.__init__(self, error_message)
        self.response_code = response_code  # Http status code
        self.response_body = response_body  # Full http response

        # Parsed error message from server
        try:
            # if we receive str/bytes we try to convert to unicode/str to have
            # consistent message types (see #616)
            if (isinstance(error_message, bytes)):
                self.error_message = error_message.decode()
            else:
                self.error_message = error_message
        except Exception:
            self.error_message = error_message

    def __str__(self):
        if self.response_code is not None:
            return f"{self.response_code}: {self.error_message}"
        else:
            return f"{self.error_message}"


def on_http_error(error):
    """Manage GitlabHttpError exceptions.
    This decorator function can be used to catch GitlabHttpError exceptions
    raise specialized exceptions instead.
    Args:
        The exception type to raise -- must inherit from GitlabError
    """

    def wrap(f: __F) -> __F:
        @functools.wraps(f)
        def wrapped_f(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except GitlabHttpError as e:
                raise error(e.error_message, e.response_code, e.response_body) from e

        return cast(__F, wrapped_f)

    return wrap
