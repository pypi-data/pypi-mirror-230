from caddy.base import BaseAPI


class Tools(BaseAPI):
    def __init__(self, app_id, local=False, token=None):
        super().__init__(local=local, token=token)
        self.app_id = app_id
        self.route = "/apps"

    def request(self, tool_id: str, body: object = None) -> object:
        path = f"{self.route}/{self.app_id}/tool/{tool_id}/use"
        response = self._request(
            method="POST",
            path=path,
            body=body
        )
        return response

    def search_tools(self, query):
        path = f'{self.route}/{self.app_id}/search'
        body = dict()
        body['query'] = query
        response = self._request(
            method='POST',
            path=path,
            body=body
        )
        return response['items']

    def create_app_tool(self, route_id):
        path = f'{self.route}/{self.app_id}/tool'
        body = dict()
        body['route_id'] = route_id
        response = self._request(
            method='POST',
            path=path,
            body=body
        )
        return response

    def update_app_tool(self):
        path = f'{self.route}/{self.app_id}/tool'
        response = self._request(
            method='PUT',
            path=path
        )
        return response

    def delete_app_tool(self, tool_id):
        path = f'{self.route}/{self.app_id}/tool/{tool_id}'
        response = self._request(
            method='DELETE',
            path=path
        )
        return response

    def activate_app_tool(self, tool_id):
        path = f'{self.route}/{self.app_id}/tool/{tool_id}/activate'
        response = self._request(
            method='PUT',
            path=path
        )
        return response

    def deactivate_app_tool(self, tool_id):
        path = f'{self.route}/{self.app_id}/tool/{tool_id}/deactivate'
        response = self._request(
            method='PUT',
            path=path
        )
        return response

    def update_app_tool_parameter(self, tool_id, tool_param_id, value):
        path = f'{self.route}/{self.app_id}/tool/{tool_id}/params/{tool_param_id}'
        response = self._request(
            method='PUT',
            path=path,
            body={
                'value': value
            }
        )
        return response

    def get_app_tool(self, tool_id):
        path = f'{self.route}/{self.app_id}/tool/{tool_id}'
        response = self._request(
            method='GET',
            path=path
        )
        return response

    def get_app(self):
        path = f'{self.route}/{self.app_id}'
        response = self._request(
            method='GET',
            path=path
        )
        return response

    def update_app(self, data):
        path = f'{self.route}/{self.app_id}'
        response = self._request(
            method='PUT',
            path=path,
            body=data
        )
        return response

    def delete_app(self):
        path = f'{self.route}/{self.app_id}'
        response = self._request(
            method='DELETE',
            path=path
        )
        return response
