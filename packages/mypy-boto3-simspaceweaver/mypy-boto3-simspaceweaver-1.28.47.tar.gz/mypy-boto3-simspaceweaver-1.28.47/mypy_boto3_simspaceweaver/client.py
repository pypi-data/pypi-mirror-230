"""
Type annotations for simspaceweaver service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_simspaceweaver.client import SimSpaceWeaverClient

    session = Session()
    client: SimSpaceWeaverClient = session.client("simspaceweaver")
    ```
"""
from typing import Any, Dict, Mapping, Sequence, Type

from botocore.client import BaseClient, ClientMeta

from .type_defs import (
    DescribeAppOutputTypeDef,
    DescribeSimulationOutputTypeDef,
    LaunchOverridesTypeDef,
    ListAppsOutputTypeDef,
    ListSimulationsOutputTypeDef,
    ListTagsForResourceOutputTypeDef,
    S3DestinationTypeDef,
    S3LocationTypeDef,
    StartAppOutputTypeDef,
    StartSimulationOutputTypeDef,
)

__all__ = ("SimSpaceWeaverClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    TooManyTagsException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class SimSpaceWeaverClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        SimSpaceWeaverClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#can_paginate)
        """

    def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.close)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#close)
        """

    def create_snapshot(
        self, *, Destination: S3DestinationTypeDef, Simulation: str
    ) -> Dict[str, Any]:
        """
        Creates a snapshot of the specified simulation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.create_snapshot)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#create_snapshot)
        """

    def delete_app(self, *, App: str, Domain: str, Simulation: str) -> Dict[str, Any]:
        """
        Deletes the instance of the given custom app.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.delete_app)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#delete_app)
        """

    def delete_simulation(self, *, Simulation: str) -> Dict[str, Any]:
        """
        Deletes all SimSpace Weaver resources assigned to the given simulation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.delete_simulation)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#delete_simulation)
        """

    def describe_app(self, *, App: str, Domain: str, Simulation: str) -> DescribeAppOutputTypeDef:
        """
        Returns the state of the given custom app.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.describe_app)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#describe_app)
        """

    def describe_simulation(self, *, Simulation: str) -> DescribeSimulationOutputTypeDef:
        """
        Returns the current state of the given simulation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.describe_simulation)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#describe_simulation)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#generate_presigned_url)
        """

    def list_apps(
        self, *, Simulation: str, Domain: str = ..., MaxResults: int = ..., NextToken: str = ...
    ) -> ListAppsOutputTypeDef:
        """
        Lists all custom apps or service apps for the given simulation and domain.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.list_apps)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#list_apps)
        """

    def list_simulations(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListSimulationsOutputTypeDef:
        """
        Lists the SimSpace Weaver simulations in the Amazon Web Services account used
        to make the API
        call.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.list_simulations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#list_simulations)
        """

    def list_tags_for_resource(self, *, ResourceArn: str) -> ListTagsForResourceOutputTypeDef:
        """
        Lists all tags on a SimSpace Weaver resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#list_tags_for_resource)
        """

    def start_app(
        self,
        *,
        Domain: str,
        Name: str,
        Simulation: str,
        ClientToken: str = ...,
        Description: str = ...,
        LaunchOverrides: LaunchOverridesTypeDef = ...
    ) -> StartAppOutputTypeDef:
        """
        Starts a custom app with the configuration specified in the simulation schema.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.start_app)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#start_app)
        """

    def start_clock(self, *, Simulation: str) -> Dict[str, Any]:
        """
        Starts the simulation clock.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.start_clock)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#start_clock)
        """

    def start_simulation(
        self,
        *,
        Name: str,
        RoleArn: str,
        ClientToken: str = ...,
        Description: str = ...,
        MaximumDuration: str = ...,
        SchemaS3Location: S3LocationTypeDef = ...,
        SnapshotS3Location: S3LocationTypeDef = ...,
        Tags: Mapping[str, str] = ...
    ) -> StartSimulationOutputTypeDef:
        """
        Starts a simulation with the given name.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.start_simulation)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#start_simulation)
        """

    def stop_app(self, *, App: str, Domain: str, Simulation: str) -> Dict[str, Any]:
        """
        Stops the given custom app and shuts down all of its allocated compute
        resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.stop_app)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#stop_app)
        """

    def stop_clock(self, *, Simulation: str) -> Dict[str, Any]:
        """
        Stops the simulation clock.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.stop_clock)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#stop_clock)
        """

    def stop_simulation(self, *, Simulation: str) -> Dict[str, Any]:
        """
        Stops the given simulation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.stop_simulation)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#stop_simulation)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        Adds tags to a SimSpace Weaver resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes tags from a SimSpace Weaver resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/simspaceweaver.html#SimSpaceWeaver.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_simspaceweaver/client/#untag_resource)
        """
