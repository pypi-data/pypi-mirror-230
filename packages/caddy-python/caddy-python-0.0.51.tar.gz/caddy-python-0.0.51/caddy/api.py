from caddy.base import BaseAPI


class API(BaseAPI):
    def __init__(self, local=False, token=None):
        super().__init__(local=local, token=token)
        self.route = "/apis"

    def create_api(self, data: object) -> object:
        path = f"{self.route}/create"
        response = self._request(
            method="POST",
            path=path,
            body=data
        )
        return response

    def update_api(self, api_id: str, data: object) -> object:
        path = f"{self.route}/{api_id}/update"
        response = self._request(
            method="PUT",
            path=path,
            body=data
        )
        return response

    def delete_api(self, api_id: str) -> object:
        path = f"{self.route}/{api_id}/delete"
        response = self._request(
            method="DELETE",
            path=path
        )
        return response

    def get_api(self, api_id: str) -> object:
        path = f"{self.route}/{api_id}"
        response = self._request(
            method="GET",
            path=path
        )
        return response

    def create_api_route(self, api_id: str, data: object) -> object:
        path = f"{self.route}/{api_id}/route"
        response = self._request(
            method="POST",
            path=path,
            body=data
        )
        return response

    def update_api_route(self, api_id: str, route_id: str, data: object) -> object:
        path = f"{self.route}/{api_id}/route/{route_id}"
        response = self._request(
            method="PUT",
            path=path,
            body=data
        )
        return response

    def delete_api_route(self, api_id: str, route_id: str) -> object:
        path = f"{self.route}/{api_id}/route/{route_id}"
        response = self._request(
            method="DELETE",
            path=path
        )
        return response

    def get_api_route(self, api_id: str, route_id: str) -> object:
        path = f"{self.route}/{api_id}/route/{route_id}"
        response = self._request(
            method="GET",
            path=path
        )
        return response

    def create_api_route_parameter(self, api_id: str, route_id: str, data: object) -> object:
        path = f"{self.route}/{api_id}/route/{route_id}/parameter"
        response = self._request(
            method="POST",
            path=path,
            body=data
        )
        return response

    def update_api_route_parameter(self, api_id: str, route_id: str, parameter_id: str, data: object) -> object:
        path = f"{self.route}/{api_id}/route/{route_id}/parameter/{parameter_id}"
        response = self._request(
            method="PUT",
            path=path,
            body=data
        )
        return response

    def delete_api_route_parameter(self, api_id: str, route_id: str, parameter_id: str) -> object:
        path = f"{self.route}/{api_id}/route/{route_id}/parameter/{parameter_id}"
        response = self._request(
            method="DELETE",
            path=path
        )
        return response

    def get_api_route_parameter(self, api_id: str, route_id: str, parameter_id: str) -> object:
        path = f"{self.route}/{api_id}/route/{route_id}/parameter/{parameter_id}"
        response = self._request(
            method="GET",
            path=path
        )
        return response
