# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


class TorchResponseData:
    def __init__(self, dic):
        self.__code = dic["code"]
        self.__data = dic["data"]
        self.__message= dic["message"]


    @property
    def code(self):
        return self.__code

    @property
    def data(self):
        return self.__data

    @property
    def message(self):
        return self.__message

    def __repr__(self):
        res = "code: {}, data: {}, message: {}".format( self.__code, self.__data, self.__message)
        return res
