#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python Template for Cisco Sample Code.

Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""


__author__ = "Timothy E Miller, PhD <timmil@cisco.com>"
__contributors__ = [
]
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import requests
import json

from nxapi import payloads


class nxapiException(Exception):
    pass


class nxapi(object):
    def __init__(self, protocol='http',
                 host='localhost', port='80',
                 username='admin', password='admin',
                 message_format='json-rpc',
                 command_type='cli',
                 ):

        # Core connection information
        self.__set_protocol(protocol)
        self.__host = host
        self.__port = port
        self.__user = username
        self.__password = password
        self.__set_message(message_format)
        self.__set_command(command_type)

        # Test the connection
        self._test_connection()

    def __set_protocol(self, protocol):
        if protocol not in ['http', 'https']:
            raise nxapiException(
                        'Unsupported protocol {0}'.format(protocol)
                        )

        self.__protocol = protocol

    def __get_protocol(self):
        return self.__protocol

    protocol = property(__get_protocol, __set_protocol)

    def __set_message(self, message_format):
        if message_format not in payloads.supported_messages:
            raise nxapiException(
                        'Unsupported message {0}'.format(message_format)
            )

        self.__message = message_format

    def __get_message(self):
        return self.__message

    message_format = property(__get_message, __set_message)

    def __set_command(self, command_type):
        commands = payloads.supported_command_types[self.message_format]
        if command_type not in commands:
            raise nxapiException(
                        'Unsupported command {0}'.format(command_type)
                        )

        self.__command = command_type

    def __get_command(self):
        return self.__command

    command_type = property(__get_command, __set_command)

    def __url(self):
        return '{0}://{1}:{2}/ins'.format(
                   self.protocol, self.__host, self.__port
                   )

    def __credentials(self):
        return (self.__user, self.__password)

    def post(self, request=None, status=None):
        response_raw = requests.post(
                            self.__url(),
                            data=json.dumps(request.post_input()),
                            headers=request.post_header(),
                            auth=self.__credentials()
                            )

        # Convert response to return status if requested
        if status:
            return response_raw.status_code

        return response_raw.json()

    def payload(self, payload_commands=None):
        if self.message_format == 'json-rpc':
            return payloads.json_rpc(
                        method=self.command_type,
                        cmd=payload_commands
                        )

        raise nxapiException(
                'Unsupported message format {0}'.format(self.message_format)
                )

    def _test_connection(self):
        payload = self.payload('show version')
        status = self.post(payload, status=True)
        if status >= 400:
            raise nxapiException('Status code: {0}'.format(status))
