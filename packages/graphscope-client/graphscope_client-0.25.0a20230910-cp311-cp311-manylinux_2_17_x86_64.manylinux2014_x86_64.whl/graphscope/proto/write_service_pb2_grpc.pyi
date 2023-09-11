"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
Copyright 2020 Alibaba Group Holding Limited. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import abc
import collections.abc
import grpc
import grpc.aio
import typing
import write_service_pb2

_T = typing.TypeVar('_T')

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta):
    ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore
    ...

class ClientWriteStub:
    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    getClientId: grpc.UnaryUnaryMultiCallable[
        write_service_pb2.GetClientIdRequest,
        write_service_pb2.GetClientIdResponse,
    ]
    batchWrite: grpc.UnaryUnaryMultiCallable[
        write_service_pb2.BatchWriteRequest,
        write_service_pb2.BatchWriteResponse,
    ]
    remoteFlush: grpc.UnaryUnaryMultiCallable[
        write_service_pb2.RemoteFlushRequest,
        write_service_pb2.RemoteFlushResponse,
    ]

class ClientWriteAsyncStub:
    getClientId: grpc.aio.UnaryUnaryMultiCallable[
        write_service_pb2.GetClientIdRequest,
        write_service_pb2.GetClientIdResponse,
    ]
    batchWrite: grpc.aio.UnaryUnaryMultiCallable[
        write_service_pb2.BatchWriteRequest,
        write_service_pb2.BatchWriteResponse,
    ]
    remoteFlush: grpc.aio.UnaryUnaryMultiCallable[
        write_service_pb2.RemoteFlushRequest,
        write_service_pb2.RemoteFlushResponse,
    ]

class ClientWriteServicer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getClientId(
        self,
        request: write_service_pb2.GetClientIdRequest,
        context: _ServicerContext,
    ) -> typing.Union[write_service_pb2.GetClientIdResponse, collections.abc.Awaitable[write_service_pb2.GetClientIdResponse]]: ...
    @abc.abstractmethod
    def batchWrite(
        self,
        request: write_service_pb2.BatchWriteRequest,
        context: _ServicerContext,
    ) -> typing.Union[write_service_pb2.BatchWriteResponse, collections.abc.Awaitable[write_service_pb2.BatchWriteResponse]]: ...
    @abc.abstractmethod
    def remoteFlush(
        self,
        request: write_service_pb2.RemoteFlushRequest,
        context: _ServicerContext,
    ) -> typing.Union[write_service_pb2.RemoteFlushResponse, collections.abc.Awaitable[write_service_pb2.RemoteFlushResponse]]: ...

def add_ClientWriteServicer_to_server(servicer: ClientWriteServicer, server: typing.Union[grpc.Server, grpc.aio.Server]) -> None: ...
