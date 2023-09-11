"""Canvas API Client."""
import json
import logging

from urllib.parse import urljoin

import aiohttp
from multidict import MultiDict

from canvas_parent_api.errors.canvas_error import CanvasError

from .models.base import ObserveeResponse, CourseResponse, AssignmentResponse, SubmissionResponse

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)


def _enable_debug_logging():
    _LOGGER.setLevel(logging.DEBUG)


class CanvasApiClient():
    """Canvas Parent API Client."""
    def __init__(
        self,
        base_url,
        api_key,
        path: str = None,
        debug=False,
    ):
        if debug:
            _enable_debug_logging()

        if path:
            self._base_url = f"{base_url}/api/v1/users/{path}"
        else:
            self._base_url = f"{base_url}/api/v1/"

        _LOGGER.debug(f"generated base url: {self._base_url}")

        self._api_key = api_key
        self._headers = {"accept": "application/json", "Authorization": f"Bearer {self._api_key}"}

    async def _get_request(self, end_url: str):
        """Perform GET request to API endpoint."""
        request_url = urljoin(self._base_url, end_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{request_url}", headers=self._headers) as resp:
                response = resp
                responsetext = await resp.text()
                if response.status >= 400:
                    raise CanvasError(response.status, responsetext)
                return response

    async def get_observees(self) -> list[ObserveeResponse]:
        """Get Canvas Observees (students)."""
        response = await self._get_request("users/self/observees")
        parsed_json = await response.json()
        next = MultiDict(response.links.get('next', ''))
        if next:
            nextpage = await self._get_request(str(next.get('url')).replace(self._base_url, ''))
            parsed_json.extend(await nextpage.json())
        if response:
            return [ObserveeResponse(**resp) for resp in parsed_json]
        return []

    async def get_courses(self, student_id: int) -> list[CourseResponse]:
        """Get Canvas Courses."""
        response = await self._get_request(f"users/{student_id}/courses?include[]=term&include[]=current_grading_period_scores&include[]=total_scores&per_page=50")
        parsed_json = await response.json()
        next = MultiDict(response.links.get('next', ''))
        if next:
            nextpage = await self._get_request(str(next.get('url')).replace(self._base_url, ''))
            parsed_json.extend(await nextpage.json())
        if response:
            return [CourseResponse(**resp) for resp in parsed_json]
        return []

    async def get_assignments(self, student_id: int, course_id: int) -> list[AssignmentResponse]:
        """Get Canvas Courses."""
        response = await self._get_request(
            f"users/{student_id}/courses/{course_id}/assignments?include[]=submission&per_page=50"
        )
        parsed_json = await response.json()
        next = MultiDict(response.links.get('next', ''))
        if next:
            nextpage = await self._get_request(str(next.get('url')).replace(self._base_url, ''))
            parsed_json.extend(await nextpage.json())
        if response:
            return [AssignmentResponse(**resp) for resp in parsed_json]
        return []

    async def get_submissions(self, student_id: int, course_id: int) -> list[SubmissionResponse]:
        """Get Canvas Courses."""
        response = await self._get_request(
            f"courses/{course_id}/students/submissions?student_ids[]={student_id}&per_page=50"
        )
        parsed_json = await response.json()
        next = MultiDict(response.links.get('next', ''))
        if next:
            nextpage = await self._get_request(str(next.get('url')).replace(self._base_url, ''))
            parsed_json.extend(await nextpage.json())
        if response:
            return [SubmissionResponse(**resp) for resp in parsed_json]
        return []
