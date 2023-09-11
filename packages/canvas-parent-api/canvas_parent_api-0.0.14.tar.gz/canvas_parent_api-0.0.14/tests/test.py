from re import S
from canvas_parent_api import Canvas
import asyncio
import time

base_url = "https://rsdmo.instructure.com"
api_token = "7951~dwodqd7i7puHzjBMJ8nwfHztydGpuuNeKJVrkk5jkpBKRRXWc6DWVIVPOTM0Po8C"

async def get_students():
	client = Canvas(f"{base_url}",f"{api_token}")
	return await client.observees()

async def get_courses(student_id,sem):
	client = Canvas(f"{base_url}",f"{api_token}")
	async with sem:
		return await client.courses(student_id)

async def get_assignments(student_id,course_id,sem):
	client = Canvas(f"{base_url}",f"{api_token}")
	async with sem:
		return await client.assignments(student_id,course_id)

async def get_submissions(student_id,course_id,sem):
	client = Canvas(f"{base_url}",f"{api_token}")
	async with sem:
		return await client.submissions(student_id,course_id)

async def main():

	students = await get_students()

	semaphore = asyncio.Semaphore(25)
	count = 0
	tasks = []
	s = time.perf_counter()
	for student in students:
		tasks.append(asyncio.create_task(get_courses(student.id,semaphore)))
		courses = await asyncio.gather(*tasks)
		print(time.perf_counter() - s)
		tasks = []
		for course in courses[0]:
			print(len(tasks))
			tasks.append(asyncio.create_task(get_submissions(student.id,course.id,semaphore)))
		for course in courses[0]:
			tasks.append(asyncio.create_task(get_assignments(student.id,course.id,semaphore)))
	assignments = await asyncio.gather(*tasks)
	for result in assignments:
		for assignment in result:
			count += 1
			print(assignment)

	elapsed = time.perf_counter() - s
	print(count)
	print(elapsed)

asyncio.run(main())