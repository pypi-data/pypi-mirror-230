from caddy.base import BaseAPI


class Tools(BaseAPI):
    def __init__(self, local=False, token=None):
        super().__init__(local=local, token=token)
        self.route = "/apps"

    def request(self, app_id: str, tool_id: str, body: object = None) -> object:
        path = f"{self.route}/{app_id}/tool/{tool_id}/use"
        response = self._post(
            path=path,
            body=body
        )
        self.request_id = None
        return response

    def search_tools(self, app_id, query):
        path = f'{self.route}/{app_id}/search'
        body = dict()
        body['query'] = query
        response = self._post(
            detailed=True,
            path=path,
            body=body
        )

        if response.get('correlation_id'):
            self.request_id = response['correlation_id']

        return response['payload']['items']

    def create_app(self, data):
        path = f'{self.route}'
        response = self._request(
            method='POST',
            path=path,
            body=data
        )
        return response

    def get_app(self, app_id):
        path = f'{self.route}/{app_id}'
        response = self._request(
            method='GET',
            path=path
        )
        return response

    def update_app(self, app_id, data):
        path = f'{self.route}/{app_id}'
        response = self._request(
            method='PUT',
            path=path,
            body=data
        )
        return response

    def delete_app(self, app_id):
        path = f'{self.route}/{app_id}'
        response = self._request(
            method='DELETE',
            path=path
        )
        return response

    def create_app_tool(self, app_id, route_id):
        path = f'{self.route}/{app_id}/tool'
        body = dict()
        body['route_id'] = route_id
        response = self._request(
            method='POST',
            path=path,
            body=body
        )
        return response

    def update_app_tool(self, app_id):
        path = f'{self.route}/{app_id}/tool'
        response = self._request(
            method='PUT',
            path=path
        )
        return response

    def delete_app_tool(self, app_id, tool_id):
        path = f'{self.route}/{app_id}/tool/{tool_id}'
        response = self._request(
            method='DELETE',
            path=path
        )
        return response

    def activate_app_tool(self, app_id, tool_id):
        path = f'{self.route}/{app_id}/tool/{tool_id}/activate'
        response = self._request(
            method='PUT',
            path=path
        )
        return response

    def deactivate_app_tool(self, app_id, tool_id):
        path = f'{self.route}/{app_id}/tool/{tool_id}/deactivate'
        response = self._request(
            method='PUT',
            path=path
        )
        return response

    def update_app_tool_parameter(self, app_id, tool_id, tool_param_id, value):
        path = f'{self.route}/{app_id}/tool/{tool_id}/params/{tool_param_id}'
        response = self._request(
            method='PUT',
            path=path,
            body={
                'value': value
            }
        )
        return response

    def get_app_tool(self, app_id, tool_id):
        path = f'{self.route}/{app_id}/tool/{tool_id}'
        response = self._request(
            method='GET',
            path=path
        )
        return response
