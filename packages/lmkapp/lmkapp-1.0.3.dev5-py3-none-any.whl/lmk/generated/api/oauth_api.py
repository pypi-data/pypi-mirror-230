# coding: utf-8

"""
    LMK API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import re  # noqa: F401

from pydantic import validate_arguments, ValidationError
from typing_extensions import Annotated

from pydantic import StrictStr, constr, validator

from typing import Optional

from lmk.generated.models.access_token_request import AccessTokenRequest
from lmk.generated.models.access_token_response import AccessTokenResponse

from lmk.generated.api_client import ApiClient
from lmk.generated.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)


class OauthApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client

    @validate_arguments
    def authorize(self, client_id : StrictStr, response_type : StrictStr, redirect_uri : StrictStr, scope : constr(strict=True), state : StrictStr, token : StrictStr, csrf_token : StrictStr, notification_channels : Optional[StrictStr] = None, **kwargs) -> None:  # noqa: E501
        """authorize  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.authorize(client_id, response_type, redirect_uri, scope, state, token, csrf_token, notification_channels, async_req=True)
        >>> result = thread.get()

        :param client_id: (required)
        :type client_id: str
        :param response_type: (required)
        :type response_type: str
        :param redirect_uri: (required)
        :type redirect_uri: str
        :param scope: (required)
        :type scope: str
        :param state: (required)
        :type state: str
        :param token: (required)
        :type token: str
        :param csrf_token: (required)
        :type csrf_token: str
        :param notification_channels:
        :type notification_channels: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: None
        """
        kwargs['_return_http_data_only'] = True
        return self.authorize_with_http_info(client_id, response_type, redirect_uri, scope, state, token, csrf_token, notification_channels, **kwargs)  # noqa: E501

    @validate_arguments
    def authorize_with_http_info(self, client_id : StrictStr, response_type : StrictStr, redirect_uri : StrictStr, scope : constr(strict=True), state : StrictStr, token : StrictStr, csrf_token : StrictStr, notification_channels : Optional[StrictStr] = None, **kwargs):  # noqa: E501
        """authorize  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.authorize_with_http_info(client_id, response_type, redirect_uri, scope, state, token, csrf_token, notification_channels, async_req=True)
        >>> result = thread.get()

        :param client_id: (required)
        :type client_id: str
        :param response_type: (required)
        :type response_type: str
        :param redirect_uri: (required)
        :type redirect_uri: str
        :param scope: (required)
        :type scope: str
        :param state: (required)
        :type state: str
        :param token: (required)
        :type token: str
        :param csrf_token: (required)
        :type csrf_token: str
        :param notification_channels:
        :type notification_channels: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: None
        """

        _params = locals()

        _all_params = [
            'client_id',
            'response_type',
            'redirect_uri',
            'scope',
            'state',
            'token',
            'csrf_token',
            'notification_channels'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method authorize" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))

        # process the form parameters
        _form_params = []
        _files = {}
        if _params['client_id']:
            _form_params.append(('client_id', _params['client_id']))
        if _params['response_type']:
            _form_params.append(('response_type', _params['response_type']))
        if _params['redirect_uri']:
            _form_params.append(('redirect_uri', _params['redirect_uri']))
        if _params['scope']:
            _form_params.append(('scope', _params['scope']))
        if _params['state']:
            _form_params.append(('state', _params['state']))
        if _params['notification_channels']:
            _form_params.append(('notification_channels', _params['notification_channels']))
        if _params['token']:
            _form_params.append(('token', _params['token']))
        if _params['csrf_token']:
            _form_params.append(('csrf_token', _params['csrf_token']))

        # process the body parameter
        _body_params = None

        # set the HTTP header `Content-Type`
        _content_types_list = _params.get('_content_type',
            self.api_client.select_header_content_type(
                ['application/x-www-form-urlencoded']))
        if _content_types_list:
                _header_params['Content-Type'] = _content_types_list

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {}

        return self.api_client.call_api(
            '/oauth/authorize', 'POST',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @validate_arguments
    def token(self, authorization : StrictStr, access_token_request : AccessTokenRequest, **kwargs) -> AccessTokenResponse:  # noqa: E501
        """token  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.token(authorization, access_token_request, async_req=True)
        >>> result = thread.get()

        :param authorization: (required)
        :type authorization: str
        :param access_token_request: (required)
        :type access_token_request: AccessTokenRequest
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: AccessTokenResponse
        """
        kwargs['_return_http_data_only'] = True
        return self.token_with_http_info(authorization, access_token_request, **kwargs)  # noqa: E501

    @validate_arguments
    def token_with_http_info(self, authorization : StrictStr, access_token_request : AccessTokenRequest, **kwargs):  # noqa: E501
        """token  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.token_with_http_info(authorization, access_token_request, async_req=True)
        >>> result = thread.get()

        :param authorization: (required)
        :type authorization: str
        :param access_token_request: (required)
        :type access_token_request: AccessTokenRequest
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(AccessTokenResponse, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'authorization',
            'access_token_request'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method token" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        if _params['authorization']:
            _header_params['authorization'] = _params['authorization']

        # process the form parameters
        _form_params = []
        _files = {}

        # process the body parameter
        _body_params = None
        if _params['access_token_request']:
            _body_params = _params['access_token_request']

        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # set the HTTP header `Content-Type`
        _content_types_list = _params.get('_content_type',
            self.api_client.select_header_content_type(
                ['application/json']))
        if _content_types_list:
                _header_params['Content-Type'] = _content_types_list

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {
            '201': "AccessTokenResponse",
        }

        return self.api_client.call_api(
            '/oauth/token', 'POST',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))
