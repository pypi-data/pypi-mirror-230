"""Base Canvas Class."""
import logging

from canvas_parent_api.models.submission import Submission

from .models.observee import Observee
from .models.course import Course
from .models.assignment import Assignment
from .canvas_api_client import CanvasApiClient

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)


class Canvas():
    """Define Canvas Class."""
    def __init__(
        self,
        base_url,
        api_key,
        path: str = None,
        debug=False,
    ):
        self._api_client = CanvasApiClient(base_url, api_key, path, debug)

        if debug:
            _LOGGER.setLevel(logging.DEBUG)

    async def observees(self) -> list[Observee]:
        """Get Observees."""
        observeesresp = await self._api_client.get_observees()
        observees = [Observee(response) for response in observeesresp]
        return observees

    async def courses(self, student_id) -> list[Course]:
        """Get Courses: must supply student id."""
        coursesresp = await self._api_client.get_courses(student_id)
        courses = [Course(response) for response in coursesresp]
        return courses

    async def assignments(self, student_id, course_id) -> list[Assignment]:
        """Get Assignments: must supply student id and course id."""
        assignmentsresp = await self._api_client.get_assignments(student_id, course_id)
        assignments = [Assignment(response) for response in assignmentsresp]
        return assignments

    async def submissions(self, student_id, course_id) -> list[Submission]:
        """Get Submissions: must supply student id and course id."""
        submissionsresp = await self._api_client.get_submissions(student_id, course_id)
        submissions = [Submission(response) for response in submissionsresp]
        return submissions
