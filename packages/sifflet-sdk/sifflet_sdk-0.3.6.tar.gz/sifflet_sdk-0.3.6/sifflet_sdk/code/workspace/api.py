import json
from enum import Enum
from typing import List, Optional
from uuid import UUID

from sifflet_sdk.client.api import workspace_api
from sifflet_sdk.client.exceptions import ApiException
from sifflet_sdk.client.model.as_code_object_dto import AsCodeObjectDto
from sifflet_sdk.client.model.as_code_workspace_dto import AsCodeWorkspaceDto
from sifflet_sdk.client.model.workspace_apply_request_dto import WorkspaceApplyRequestDto
from sifflet_sdk.client.model.workspace_apply_response_dto import WorkspaceApplyResponseDto
from sifflet_sdk.apis.base import BaseApi
from sifflet_sdk.logger import logger


class ObjectUntrackAction(Enum):
    DELETE = "DELETE"
    IGNORE = "IGNORE"
    ERROR = "ERROR"
    UNTRACK = "UNTRACK"


class ObjectMoveAction(Enum):
    MOVE = "MOVE"
    IGNORE = "IGNORE"
    ERROR = "ERROR"


class ObjectTrackAction(Enum):
    TRACK = "TRACK"
    IGNORE = "IGNORE"
    ERROR = "ERROR"


class WorkspaceApi(BaseApi):
    def __init__(self, sifflet_config):
        super().__init__(sifflet_config)
        self.api_instance = workspace_api.WorkspaceApi(self.api)

    def list_workspaces(self) -> List[AsCodeWorkspaceDto]:
        response = self.api_instance.list_workspaces()
        logger.debug(f"Response: {response}")
        return response

    def delete_workspace(self, id: UUID, dry_run: bool) -> WorkspaceApplyResponseDto:
        logger.debug(f"Request: id={id}, dry_run={dry_run}")
        response = self.api_instance.delete_workspace(str(id), dry_run=dry_run)
        logger.debug(f"Response: {response}")
        return response

    def apply_workspace(
        self,
        id: UUID,
        changes: List[AsCodeObjectDto],
        dry_run: bool,
        object_untrack_action: Optional[ObjectUntrackAction] = None,
        object_move_action: Optional[ObjectMoveAction] = None,
        object_track_action: Optional[ObjectTrackAction] = None,
    ) -> WorkspaceApplyResponseDto:
        # We do not check the type to allow the use of new monitor parameters DTO
        # Without updating the CLI
        request = WorkspaceApplyRequestDto(_check_type=False)
        request.changes = changes
        logger.debug(
            f"Request: id={id}, dry_run={dry_run}, object_untrack_action={object_untrack_action}, object_move_action={object_move_action}, object_track_action={object_track_action}, body="
        )
        logger.debug(request)
        kwargs = {}
        if object_untrack_action is not None:
            kwargs["object_untrack_action"] = object_untrack_action.value
        if object_move_action is not None:
            kwargs["object_move_action"] = object_move_action.value
        if object_track_action is not None:
            kwargs["object_track_action"] = object_track_action.value
        try:
            response = self.api_instance.deploy_workspace(
                str(id),
                request,
                dry_run=dry_run,
                _check_return_type=False,
                **kwargs,
            )
            logger.debug("Response: body=")
            logger.debug(response)
        except ApiException as err:
            logger.debug(err)
            if err.body:
                error_body = json.loads(err.body)
                if error_body.get("type") == "sifflet:errors:workspace:apply":
                    response = error_body["response"]
                    return WorkspaceApplyResponseDto(**response)
            raise err
        return response
