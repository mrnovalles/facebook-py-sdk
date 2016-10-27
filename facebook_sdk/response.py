try:
    import simplejson as json
except ImportError:
    import json

from facebook_sdk.exceptions import FacebookResponseException
from facebook_sdk.request import FacebookRequest, FacebookBatchRequest


class FacebookResponse(object):
    """ A Facebook Response

    """

    def __init__(self, request, http_status_code, body, headers=None):
        """
        :type headers: dict
        :type body: str
        :type http_status_code: int
        :type request: FacebookRequest
        """
        super(FacebookResponse, self).__init__()

        self.request = request
        self.body = body
        self.http_status_code = http_status_code
        self.headers = headers

        self._parse_body()

        if self.is_error:
            self._build_exception()

    @property
    def is_error(self):
        """ Check if the response is an error-

        """
        return 'error' in self.json_body

    def _parse_body(self):
        """ Parse the raw response to json.

        """
        try:
            self.json_body = json.loads(self.body)
        except:
            self.json_body = {}

    def raiseException(self):
        """ Raise the FacebookSDKException

        """
        raise self.exception

    def _build_exception(self):
        """

        :return:
        """
        self.exception = FacebookResponseException.create(response=self)


class FacebookBatchResponse(FacebookResponse):
    """ A Facebook Batch Response

    """

    def __init__(self, batch_request, batch_response):
        """

        :type batch_request: FacebookBatchRequest
        :type batch_response: FacebookResponse
        """
        super(FacebookBatchResponse, self).__init__(
            request=batch_request,
            body=batch_response.body,
            http_status_code=batch_response.http_status_code,
            headers=batch_response.headers
        )
        self.responses = self.build_responses(self.json_body)

    def build_responses(self, json_body):
        """ Parse the json_body to a set of FacebookResponse.

        :param json_body: parsed batch response
        """
        responses = []
        for index, response in enumerate(json_body):
            request_name = self.request.requests[index]['name']
            request = self.request.requests[index]['request']

            body = response.get('body')
            code = response.get('code')
            headers = response.get('headers')

            responses.insert(
                index,
                {
                    'name': request_name,
                    'response': FacebookResponse(
                        request=request,
                        body=body,
                        headers=headers,
                        http_status_code=code,
                    ),
                }
            )

        return responses

    def __iter__(self):
        return iter(self.responses)
