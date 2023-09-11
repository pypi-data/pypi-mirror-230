# -*- coding: utf-8 -*-
import logging
import json

from flask import g, request, url_for
from flask_restful import Api
from http import HTTPStatus
from sqlalchemy import desc

from vantage6.common.globals import STRING_ENCODING
from vantage6.common.task_status import TaskStatus, has_task_finished
from vantage6.server import db
from vantage6.server.permission import (
    Scope as S,
    PermissionManager,
    Operation as P
)
from vantage6.server.resource import only_for, ServicesResources, with_user
from vantage6.server.resource.common._schema import (
    TaskSchema,
    TaskIncludedSchema,
    TaskResultSchema
)
from vantage6.server.resource.pagination import Pagination
from vantage6.server.resource.event import kill_task


module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


def setup(api: Api, api_base: str, services: dict) -> None:
    """
    Setup the task resource.

    Parameters
    ----------
    api : Api
        Flask restful api instance
    api_base : str
        Base url of the api
    services : dict
        Dictionary with services required for the resource endpoints
    """
    path = "/".join([api_base, module_name])
    log.info(f'Setting up "{path}" and subdirectories')

    api.add_resource(
        Tasks,
        path,
        endpoint='task_without_id',
        methods=('GET', 'POST'),
        resource_class_kwargs=services
    )
    api.add_resource(
        Task,
        path + '/<int:id>',
        endpoint='task_with_id',
        methods=('GET', 'DELETE'),
        resource_class_kwargs=services
    )
    api.add_resource(
        TaskResult,
        path + '/<int:id>/result',
        endpoint='task_result',
        methods=('GET',),
        resource_class_kwargs=services
    )


# -----------------------------------------------------------------------------
# Permissions
# -----------------------------------------------------------------------------
def permissions(permissions: PermissionManager) -> None:
    """
    Define the permissions for this resource.

    Parameters
    ----------
    permissions : PermissionManager
        Permission manager instance to which permissions are added
    """
    add = permissions.appender(module_name)

    add(scope=S.GLOBAL, operation=P.VIEW,
        description="view any task")
    add(scope=S.ORGANIZATION, operation=P.VIEW, assign_to_container=True,
        assign_to_node=True, description="view tasks of your organization")

    add(scope=S.GLOBAL, operation=P.CREATE, description="create a new task")
    add(scope=S.ORGANIZATION, operation=P.CREATE,
        description=(
            "create a new task for collaborations in which your organization "
            "participates with"
        ))

    add(scope=S.GLOBAL, operation=P.DELETE,
        description="delete a task")
    add(scope=S.ORGANIZATION, operation=P.DELETE,
        description=(
            "delete a task from a collaboration in which your organization "
            "participates with"
        ))


# ------------------------------------------------------------------------------
# Resources / API's
# ------------------------------------------------------------------------------
task_schema = TaskSchema()
task_result_schema = TaskIncludedSchema()
task_result_schema2 = TaskResultSchema()


class TaskBase(ServicesResources):

    def __init__(self, socketio, mail, api, permissions, config):
        super().__init__(socketio, mail, api, permissions, config)
        self.r = getattr(self.permissions, module_name)


class Tasks(TaskBase):

    @only_for(("user", "node", "container"))
    def get(self):
        """List tasks
        ---
        description: >-
          Returns a list of tasks.\n

          ### Permission Table\n
          |Rule name|Scope|Operation|Assigned to node|Assigned to container|
          Description|\n
          |--|--|--|--|--|--|\n
          |Task|Global|View|❌|❌|View any task|\n
          |Task|Organization|View|✅|✅|View any task in your organization|
          \n

          Accessible to users.

        parameters:
          - in: query
            name: initiator_id
            schema:
              type: int
            description: The organization id of the origin of the request
          - in: query
            name: init_user_id
            schema:
              type: int
            description: The user id of the user that started the task
          - in: query
            name: collaboration_id
            schema:
              type: int
            description: The collaboration id to which the task belongs
          - in: query
            name: image
            schema:
              type: str
            description: >-
              (Docker) image name which is used in the task. Name to match
              with a LIKE operator. \n
              * The percent sign (%) represents zero, one, or multiple
              characters\n
              * underscore sign (_) represents one, single character
          - in: query
            name: parent_id
            schema:
              type: int
            description: The id of the parent task
          - in: query
            name: run_id
            schema:
              type: int
            description: The run id that belongs to the task
          - in: query
            name: name
            schema:
              type: str
            description: >-
              Name to match with a LIKE operator. \n
              * The percent sign (%) represents zero, one, or multiple
              characters\n
              * underscore sign (_) represents one, single character
          - in: query
            name: description
            schema:
              type: string
            description: >-
              Description to match with a LIKE operator. \n
              * The percent sign (%) represents zero, one, or multiple
              characters\n
              * underscore sign (_) represents one, single character
          - in: query
            name: database
            schema:
              type: string
            description: >-
              Database description to match with a LIKE operator. \n
              * The percent sign (%) represents zero, one, or multiple
              characters\n
              * underscore sign (_) represents one, single character
          - in: query
            name: result_id
            schema:
              type: int
            description: A result id that belongs to the task
          - in: query
            name: include
            schema:
              type: array
              items:
                type: string
            description: Include 'results' to get task results. Include
              'metadata' to get pagination metadata. Note that this will
              put the actual data in an envelope.
          - in: query
            name: status
            schema:
              type: string
            description: Filter by task status, e.g. 'active' for active
              tasks, 'completed' for finished or 'crashed' for failed tasks.
          - in: query
            name: page
            schema:
              type: integer
            description: Page number for pagination
          - in: query
            name: per_page
            schema:
              type: integer
            description: Number of items per page

        responses:
          200:
            description: Ok
          400:
            description: Non-allowed parameter values
          401:
            description: Unauthorized

        security:
            - bearerAuth: []

        tags: ["Task"]
        """
        q = g.session.query(db.Task)
        args = request.args

        # obtain organization id
        auth_org_id = self.obtain_organization_id()

        # check permissions and apply filter if neccassary
        if not self.r.v_glo.can():
            if self.r.v_org.can():
                q = q.join(db.Collaboration).join(db.Organization)\
                    .filter(db.Collaboration.organizations.any(id=auth_org_id))
            else:
                return {'msg': 'You lack the permission to do that!'}, \
                    HTTPStatus.UNAUTHORIZED

        # filter based on arguments
        for param in ['initiator_id', 'init_user_id', 'collaboration_id',
                      'parent_id', 'run_id']:
            if param in args:
                q = q.filter(getattr(db.Task, param) == args[param])
        for param in ['name', 'image', 'description', 'database', 'status']:
            if param in args:
                q = q.filter(getattr(db.Task, param).like(args[param]))
        if 'result_id' in args:
            q = q.join(db.Result).filter(db.Result.id == args['result_id'])

        q = q.order_by(desc(db.Task.id))
        # paginate tasks
        page = Pagination.from_query(q, request)

        # serialization schema
        schema = task_result_schema if self.is_included('results') else\
            task_schema

        return self.response(page, schema)

    @only_for(("user", "container"))
    def post(self):
        """Adds new computation task
        ---
        description: >-
          Creates a new task within a collaboration. If no `organization_ids`
          are given the task is send to all organizations within the
          collaboration. The endpoint can be accessed by both a `User` and
          `Container`.\n

          ### Permission Table\n
          |Rule name|Scope|Operation|Assigned to node|Assigned to container|
          Description|\n
          |--|--|--|--|--|--|\n
          |Task|Global|Create|❌|❌|Create a new task|\n
          |Task|Organization|Create|❌|✅|Create a new task for a specific
          collaboration in which your organization participates|\n

          ## Accessed as `User`\n
          This endpoint is accessible to users. A new `run_id` is
          created when a user creates a task. The user needs to be within an
          organization that is part of the collaboration to which the task is
          posted.\n

          ## Accessed as `Container`\n
          When this endpoint is accessed by an algorithm container, it is
          considered to be a child-task of the container, and will get the
          `run_id` from the initial task. Containers have limited permissions
          to create tasks: they are only allowed to create tasks in the same
          collaboration using the same image.\n

        requestBody:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'

        responses:
          200:
            description: Ok
          400:
            description: Supplied organizations are not in the supplied
              collaboration, or not all required nodes are registered, or you
              are not in the collaboration yourself
          401:
            description: Unauthorized
          404:
            description: Collaboration with `collaboration_id` not found

        security:
          - bearerAuth: []

        tags: ["Task"]
        """
        data = request.get_json()
        collaboration_id = data.get('collaboration_id')
        collaboration = db.Collaboration.get(collaboration_id)

        if not collaboration:
            return {"msg": f"Collaboration id={collaboration_id} not found!"},\
                   HTTPStatus.NOT_FOUND

        organizations_json_list = data.get('organizations')
        org_ids = [org.get("id") for org in organizations_json_list]
        db_ids = collaboration.get_organization_ids()

        # Check that all organization ids are within the collaboration, this
        # also ensures us that the organizations exist
        if not set(org_ids).issubset(db_ids):
            return {"msg": (
                "At least one of the supplied organizations in not within "
                "the collaboration."
            )}, HTTPStatus.BAD_REQUEST

        # check if all the organizations have a registered node
        nodes = g.session.query(db.Node)\
            .filter(db.Node.organization_id.in_(org_ids))\
            .filter(db.Node.collaboration_id == collaboration_id)\
            .all()
        if len(nodes) < len(org_ids):
            present_nodes = [node.organization_id for node in nodes]
            missing = [str(id) for id in org_ids if id not in present_nodes]
            return {"msg": (
                "Cannot create this task because there are no nodes registered"
                f" for the following organization(s): {', '.join(missing)}."
            )}, HTTPStatus.BAD_REQUEST
        # check if any of the nodes that are offline shared their configuration
        # info and if this prevents this user from creating this task
        if g.user:
            for node in nodes:
                if self._node_doesnt_allow_user_task(node.config):
                    return {"msg": (
                        "Cannot create this task because one of the nodes that"
                        " you are trying to send this task to does not allow "
                        "you to create tasks."
                    )}, HTTPStatus.BAD_REQUEST

        # figure out the initiating organization of the task
        if g.user:
            init_org = g.user.organization
        else:  # g.container:
            init_org = db.Node.get(g.container["node_id"]).organization

        # check if the initiating organization is part of the collaboration
        if init_org not in collaboration.organizations:
            return {
                "msg": "You can only create tasks for collaborations "
                       "you are participating in!"
            }, HTTPStatus.UNAUTHORIZED

        # Create the new task in the database
        image = data.get('image', '')

        # verify permissions
        if g.user:
            if not self.r.c_glo.can():
                c_orgs = collaboration.organizations
                if not (self.r.c_org.can() and g.user.organization in c_orgs):
                    return {'msg': 'You lack the permission to do that!'}, \
                        HTTPStatus.UNAUTHORIZED

        elif g.container:
            # verify that the container has permissions to create the task
            if not self.__verify_container_permissions(g.container, image,
                                                       collaboration_id):
                return {"msg": "Container-token is not valid"}, \
                    HTTPStatus.UNAUTHORIZED

        # permissions ok, create record
        task = db.Task(collaboration=collaboration, name=data.get('name', ''),
                       description=data.get('description', ''), image=image,
                       database=data.get('database', ''),
                       initiator=init_org)

        # create run_id. Users can only create top-level -tasks (they will not
        # have sub-tasks). Therefore, always create a new run_id. Tasks created
        # by containers are always sub-tasks
        if g.user:
            task.run_id = task.next_run_id()
            task.init_user_id = g.user.id
            log.debug(f"New run_id {task.run_id}")
        elif g.container:
            task.parent_id = g.container["task_id"]
            parent = db.Task.get(g.container["task_id"])
            task.run_id = parent.run_id
            task.init_user_id = parent.init_user_id
            log.debug(f"Sub task from parent_id={task.parent_id}")

        # ok commit session...
        task.save()

        # send socket event that task has been created
        self.socketio.emit(
            "task_created", {
                "task_id": task.id,
                "run_id": task.run_id,
                "collaboration_id": collaboration_id,
                "init_org_id": init_org.id,
            }, room=f"collaboration_{collaboration_id}", namespace='/tasks'
        )

        # now we need to create results for the nodes to fill. Each node
        # receives their instructions from a result, not from the task itself
        log.debug(f"Assigning task to {len(organizations_json_list)} nodes.")
        for org in organizations_json_list:
            organization = db.Organization.get(org['id'])
            log.debug(f"Assigning task to '{organization.name}'.")
            input_ = org.get('input')
            # FIXME: legacy input from the client, could be removed at some
            # point
            if isinstance(input_, dict):
                input_ = json.dumps(input_).encode(STRING_ENCODING)
            # Create result
            result = db.Result(
                task=task,
                organization=organization,
                input=input_,
                status=TaskStatus.PENDING
            )
            result.save()

        # notify nodes a new task available (only to online nodes), nodes that
        # are offline will receive this task on sign in.
        self.socketio.emit('new_task', task.id, namespace='/tasks',
                           room=f'collaboration_{task.collaboration_id}')

        # add some logging
        log.info(f"New task for collaboration '{task.collaboration.name}'")
        if g.user:
            log.debug(f" created by: '{g.user.username}'")
        else:
            log.debug(f" created by container on node_id="
                      f"{g.container['node_id']}"
                      f" for (master) task_id={g.container['task_id']}")

        log.debug(f" url: '{url_for('task_with_id', id=task.id)}'")
        log.debug(f" name: '{task.name}'")
        log.debug(f" image: '{task.image}'")

        return task_schema.dump(task, many=False).data, HTTPStatus.CREATED

    @staticmethod
    def __verify_container_permissions(container, image, collaboration_id):
        """Validates that the container is allowed to create the task."""

        # check that the image is allowed: algorithm containers can only
        # create tasks with the same image
        if not image.endswith(container["image"]):
            log.warning((f"Container from node={container['node_id']} "
                        f"attempts to post a task using illegal image!?"))
            log.warning(f"  task image: {image}")
            log.warning(f"  container image: {container['image']}")
            return False

        # check master task is not completed yet
        if db.Task.get(container["task_id"]).complete:
            log.warning(
                f"Container from node={container['node_id']} "
                f"attempts to start sub-task for a completed "
                f"task={container['task_id']}"
            )
            return False

        # check that node id is indeed part of the collaboration
        if not container["collaboration_id"] == collaboration_id:
            log.warning(
                f"Container attempts to create a task outside "
                f"collaboration_id={container['collaboration_id']} in "
                f"collaboration_id={collaboration_id}!"
            )
            return False

        return True

    @staticmethod
    def _node_doesnt_allow_user_task(
        node_configs: list[db.NodeConfig]
    ) -> bool:
        """
        Checks if the node allows user to create task.

        Parameters
        ----------
        node_configs : list[db.NodeConfig]
            List of node configurations.

        Returns
        -------
        bool
            True if the node doesn't allow the user to create task.
        """
        has_limitations = False
        for config_option in node_configs:
            if config_option.key == "allowed_users":
                has_limitations = True
                # TODO expand when we allow also usernames, like orgs below
                if g.user.id == int(config_option.value):
                    return False
            elif config_option.key == "allowed_orgs":
                has_limitations = True
                if config_option.value.isdigit():
                    if g.user.organization_id == int(config_option.value):
                        return False
                else:
                    org = db.Organization.get_by_name(config_option.value)
                    if org and g.user.organization_id == org.id:
                        return False
        return has_limitations


class Task(TaskBase):
    """Resource for /api/task"""

    @only_for(("user", "node", "container"))
    def get(self, id):
        """Get task
        ---
        description: >-
          Returns the task specified by the id.

          ### Permission Table\n
          |Rule name|Scope|Operation|Assigned to node|Assigned to container|
          Description|\n
          |--|--|--|--|--|--|\n
          |Task|Global|View|❌|❌|View any task|\n
          |Task|Organization|View|✅|✅|View any task in your organization|

          Accessible to users.

        parameters:
          - in: path
            name: id
            schema:
              type: integer
            description: Task id
            required: true
          - in: query
            name: include
            schema:
              type: string
            description: Include 'results' to include the task's results.

        responses:
          200:
            description: Ok
          404:
            description: Task not found
          401:
            description: Unauthorized

        security:
          - bearerAuth: []

        tags: ["Task"]
        """
        task = db.Task.get(id)
        if not task:
            return {"msg": f"task id={id} is not found"}, HTTPStatus.NOT_FOUND

        # determine the organization to which the auth belongs
        auth_org = self.obtain_auth_organization()

        # obtain schema
        schema = task_result_schema if request.args.get('include') == \
            'results' else task_schema

        # check permissions
        if not self.r.v_glo.can():
            org_ids = [org.id for org in task.collaboration.organizations]
            if not (self.r.v_org.can() and auth_org.id in org_ids):
                return {'msg': 'You lack the permission to do that!'}, \
                    HTTPStatus.UNAUTHORIZED

        return schema.dump(task, many=False).data, HTTPStatus.OK

    @with_user
    def delete(self, id):
        """Remove task
        ---
        description: >-
          Remove tasks and their results.\n

          ### Permission Table\n
          |Rule name|Scope|Operation|Assigned to node|Assigned to container|
          Description|\n
          |--|--|--|--|--|--|\n
          |Task|Global|Delete|❌|❌|Delete a task|\n
          |Task|Organization|Delete|❌|❌|Delete a task from a collaboration
          in which your organization participates|\n

          Accessible to users.

        parameters:
          - in: path
            name: id
            schema:
              type: integer
            description: Task id
            required: true

        responses:
          200:
            description: Ok
          404:
            description: Task not found
          401:
            description: Unauthorized

        security:
          - bearerAuth: []

        tags: ["Task"]
        """

        task = db.Task.get(id)
        if not task:
            return {"msg": f"task id={id} not found"}, HTTPStatus.NOT_FOUND

        # validate permissions
        if not self.r.d_glo.can():
            orgs = task.collaboration.organizations
            if not (self.r.d_org.can() and g.user.organization in orgs):
                return {'msg': 'You lack the permission to do that!'}, \
                    HTTPStatus.UNAUTHORIZED

        # kill the task if it is still running
        if not has_task_finished(task.status):
            kill_task(task, self.socketio)

        # retrieve results that belong to this task
        log.info(f'Removing task id={task.id}')
        for result in task.results:
            log.info(f" Removing result id={result.id}")
            result.delete()

        # permissions ok, delete...
        task.delete()

        return {"msg": f"task id={id} and its result successfully deleted"}, \
            HTTPStatus.OK


class TaskResult(ServicesResources):
    """Resource for /api/task/<int:id>/result"""

    def __init__(self, socketio, mail, api, permissions, config):
        super().__init__(socketio, mail, api, permissions, config)
        self.r = getattr(self.permissions, "result")

    @only_for(['user', 'container'])
    def get(self, id):
        """Return the results for a specific task
        ---
        description: >-
          Returns the task's results specified by the task id.\n

          ### Permission Table\n
          |Rule name|Scope|Operation|Assigned to node|Assigned to container|
          Description|\n
          |--|--|--|--|--|--|\n
          |Result|Global|View|❌|❌|View any result|\n
          |Result|Organization|View|✅|✅|View results for the
          collaborations in which your organization participates with|\n

          Accessible to users.

        parameters:
          - in: path
            name: id
            schema:
              type: integer
            description: Task id
            required: true
          - in: query
            name: include
            schema:
              type: string
            description: Include 'metadata' to get pagination metadata. Note
              that this will put the actual data in an envelope.
          - in: query
            name: page
            schema:
              type: integer
            description: Page number for pagination
          - in: query
            name: per_page
            schema:
              type: integer
            description: Number of items per page

        responses:
          200:
            description: Ok
          404:
            description: Task not found
          401:
            description: Unauthorized

        security:
            - bearerAuth: []

        tags: ["Task"]
        """
        task = db.Task.get(id)
        if not task:
            return {"msg": f"Task id={id} not found"}, HTTPStatus.NOT_FOUND

        # obtain organization model
        org = self.obtain_auth_organization()

        if not self.r.v_glo.can():
            c_orgs = task.collaboration.organizations
            if not (self.r.v_org.can() and org in c_orgs):
                return {'msg': 'You lack the permission to do that!'}, \
                    HTTPStatus.UNAUTHORIZED

        # pagination
        page = Pagination.from_list(task.results, request)

        # model serialization
        return self.response(page, task_result_schema2)
