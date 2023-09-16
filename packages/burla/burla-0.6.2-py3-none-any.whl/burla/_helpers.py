import asyncio
import nest_asyncio
from aiohttp import ClientSession

nest_asyncio.apply()


class StatusMessage:
    function_name = None
    total_cpus = None
    total_gpus = None
    n_inputs = None

    uploading_inputs = "Uploading Inputs ..."
    uploading_function = "Uploading Function ..."
    downloading = "Downloading Outputs ..."

    @classmethod
    def preparing(cls):
        msg = f"Preparing to run {cls.n_inputs} inputs through `{cls.function_name}` with "
        if cls.total_gpus > 0:
            msg += f"{cls.total_cpus} CPUs, and {cls.total_gpus} GPUs."
            msg += " This may take several minutes."
        else:
            msg += f"{cls.total_cpus} CPUs."
            msg += " This may take a few minutes."
        return msg

    @classmethod
    def running(cls):
        msg = f"Running {cls.n_inputs} inputs through `{cls.function_name}` with {cls.total_cpus} "
        msg += f"CPUs, and {cls.total_gpus} GPUs." if cls.total_gpus > 0 else "CPUs."
        return msg


class JobTimeoutError(Exception):
    def __init__(self, job_id, timeout):
        super().__init__(f"Burla job with id: '{job_id}' timed out after {timeout} seconds.")


class InstallError(Exception):
    def __init__(self, stdout: str):
        super().__init__(
            f"The following error occurred attempting to pip install packages:\n{stdout}"
        )


class ServerError(Exception):
    def __init__(self):
        super().__init__(
            (
                "An unknown error occurred in Burla's cloud, this is not an error with your code. "
                "Someone has been notified, please try again later."
            )
        )


def nopath_warning(message, category, filename, lineno, line=None):
    return f"{category.__name__}: {message}\n"


def make_async_requests(requests_kwargs: list[dict]):
    async def _make_request(session, request_kwargs):  # <- cant have more than two args, idk why
        async with session.request(**request_kwargs) as response:
            response.raise_for_status()
            if request_kwargs["method"] == "get":
                return await response.read()

    async def _make_requests(requests_kwargs):
        async with ClientSession() as session:
            tasks = [_make_request(session, request_kwargs) for request_kwargs in requests_kwargs]
            return await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_make_requests(requests_kwargs))
