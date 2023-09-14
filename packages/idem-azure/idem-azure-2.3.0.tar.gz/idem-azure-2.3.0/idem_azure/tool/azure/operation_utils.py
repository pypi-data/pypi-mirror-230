import asyncio
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Optional

OPERATION_TRACKERS = {}


@dataclass
class OperationResult:
    finished: bool
    succeeded: bool
    error_message: str = None
    status: int = None
    operation_url: str = None
    resource: Dict[str, Any] = None


# result is True only if operation finished successfully
# if it is still running -> result is False and there is rerun_data containing information passed on input
# it long-running operation finished with an error -> result is False and there is rerun_data == {"has_error": True}
# if get_resource is True and operation has succeeded, get the resource by the resource_url in rerun_data
# resource is returned in result["resource"]
async def handle_operation(
    hub, ctx, rerun_data, get_resource: bool = True
) -> Dict[str, Any]:
    """
    Processes the rerun_data of a long-running asynchronous operation
    Fetches the current operation state and does error handling if needed
    Returns either the end result or the rerun_data for subsequent iterations
    :param ctx: Context to be used for Azure API calls
    :param rerun_data: Object containing any information needed for processing
        Should include the following keys:
        - operation_id - unique identifier for operation within the idem process
        - operation_headers - headers returned by Azure API needed for fetching the operation information
        - resource_url - only required if get_resource is true - URL of the targeted resource to be fetched upon operation success
        Any other keys get ignored and passed through transparently in resulting rerun_data if operation is still running
    :param get_resource: True if caller wants the method to fetch the targeted resource upon success. Resource returned in result["resource]
    """
    result = {
        "comment": [],
        "result": True,
        "rerun_data": None,
        "resource": None,
    }

    operation_id = rerun_data.get("operation_id")

    if operation_id is None:
        result["result"] = False
        result["comment"].append("Operation ID is not supplied")
        result["rerun_data"] = {"has_error": True}
        return result

    try:
        operation_result: OperationResult = (
            await hub.tool.azure.operation_utils.check_operation_result(
                ctx,
                operation_id=operation_id,
                operation_headers=rerun_data.get("operation_headers"),
            )
        )
    except Exception as e:
        result["result"] = False
        result["comment"].append(
            "An error occurred while processing the long-running operation"
        )
        result["comment"].append(str(e))
        result["rerun_data"] = {"has_error": True}
        return result

    if not operation_result.finished:
        # Operation still hasn't finished -> reconcile.
        result["rerun_data"] = rerun_data
        result["result"] = False
        return result

    if not operation_result.succeeded:
        result["rerun_data"] = {"has_error": True}
        result["comment"].append(
            f"Long running operation {operation_result.operation_url} failed"
        )
        if operation_result.status:
            result["comment"].append(f"Status code: {operation_result.status}")
        if operation_result.error_message:
            result["comment"].append(operation_result.error_message)
        result["result"] = False
        return result

    if not get_resource:
        # no further processing needed
        return result

    resource_url = rerun_data.get("resource_url")
    if not resource_url:
        raise RuntimeError("Resource URL not provided!")

    get_result = await hub.exec.request.json.get(
        ctx,
        url=resource_url,
        success_codes=[200],
    )

    if get_result.get("result"):
        result["resource"] = get_result.get("ret") or None
    elif get_result.get("status") == 404:
        result["resource"] = None
    else:
        result["result"] = False
        result["rerun_data"] = {"has_error": True}
        result["comment"].append(
            f"Long running operation {operation_result.operation_url} succeeded, but get request for {resource_url} failed"
        )
        if get_result.get("status"):
            result["comment"].append(f"Status code: {operation_result.status}")
        if get_result.get("comment"):
            result["comment"].append(get_result["comment"])
        if get_result.get("ret") and "error" in get_result.get("ret"):
            result["comment"].append(str(get_result["ret"]["error"]))

    return result


async def await_operation(hub, ctx, operation_headers, resource_url) -> Dict[str, Any]:
    """
    Awaits a long-running asynchronous Azure operation to complete. Performs an additional GET request when operation completes to fetch the resulting Azure resource.
    :param operation_headers: Headers from initial HTTP response from Azure API call which initiated the operation
    :param resource_url: Azure API URL, used to GET the resource produced by the operation
    """
    poller = OperationPoller(hub, ctx, operation_headers, resource_url)
    return await poller.await_operation()


async def check_operation_result(
    hub, ctx, operation_id, operation_headers
) -> OperationResult:
    """
    Returns the current status of a long-running asynchronous Azure operation.
    :param operation_id: Client-supplied unique operation ID
    :param operation_headers: Headers from initial HTTP response from Azure API call which initiated the operation
    """
    poller = OPERATION_TRACKERS.get(operation_id)
    if not poller:
        poller = OperationPoller(hub, ctx, operation_headers)
        OPERATION_TRACKERS[operation_id] = poller
    try:
        operation_result = await poller.check_operation()
        if operation_result.finished:
            del OPERATION_TRACKERS[operation_id]
        return operation_result
    except Exception as e:
        op_url = poller.get_operation_url()
        del OPERATION_TRACKERS[operation_id]
        return OperationResult(
            finished=True, succeeded=False, error_message=str(e), operation_url=op_url
        )


class OperationFailed(Exception):
    pass


class OperationStatus:
    """Operation status class.

    Operation status is used to indicate the status of an operation. It can be one of the following values: Succeeded, Failed, Canceled, Running.
    """

    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELED = "Canceled"
    RUNNING = "Running"

    FINISHED_STATES = {SUCCEEDED.lower(), FAILED.lower(), CANCELED.lower()}
    FAILED_STATES = {FAILED.lower(), CANCELED.lower()}
    SUCCEEDED_STATES = {SUCCEEDED.lower()}

    @staticmethod
    def finished(status):
        return str(status).lower() in OperationStatus.FINISHED_STATES

    @staticmethod
    def failed(status):
        return str(status).lower() in OperationStatus.FAILED_STATES

    @staticmethod
    def succeeded(status):
        return str(status).lower() in OperationStatus.SUCCEEDED_STATES


class OperationPoller:
    def __init__(self, hub, ctx, operation_headers, resource_url: str = None):
        self._hub = hub
        self._ctx = ctx
        self._operation_headers = operation_headers
        self._resource_url = resource_url
        self._status_url = self._get_status_url()
        self._status = None
        self._error = None

    async def await_operation(self) -> Dict[str, Any]:
        return await self._poll()

    def get_operation_url(self) -> str:
        return self._status_url

    async def check_operation(self) -> OperationResult:
        if not self.operation_finished():
            await self._update_status()
        return OperationResult(
            self.operation_finished(),
            self._operation_succeeded(),
            self._error,
            self._status,
            operation_url=self._status_url,
        )

    def _get_status_url(self) -> Optional[str]:
        headers: Dict[str, Any] = self._operation_headers

        if "Azure-AsyncOperation" in headers:
            return headers["Azure-AsyncOperation"]
        elif "Location" in headers:
            return headers["Location"]
        else:
            return None

    def _get_retry_after(self) -> int:
        headers = self._operation_headers

        retry_after = headers.get("Retry-After")
        try:
            delay = int(retry_after)
        except:
            delay = 1

        return delay if delay > 1 else 1

    def operation_finished(self) -> bool:
        return OperationStatus.finished(self._status)

    def _operation_succeeded(self) -> bool:
        return OperationStatus.succeeded(self._status)

    async def _update_status(self):
        get_response = await self._hub.exec.request.json.get(
            self._ctx,
            url=self._status_url,
            success_codes=[200],
        )
        if "status" in get_response["ret"]:
            self._status = get_response["ret"]["status"].lower()
        else:
            self._status = None
        if "error" in get_response["ret"]:
            self._error = get_response["ret"]["error"]
        else:
            self._error = None

    async def _delay(self):
        await asyncio.sleep(self._get_retry_after())

    async def _poll(self):
        if not self.operation_finished():
            await self._update_status()
        while not self.operation_finished():
            await self._delay()
            await self._update_status()

        if not self._operation_succeeded():
            raise OperationFailed(
                f"Operation failed or has been canceled: {self._error}"
            )
        else:
            get_response = await self._hub.exec.request.json.get(
                self._ctx,
                url=self._resource_url,
                success_codes=[200],
            )
            return get_response
