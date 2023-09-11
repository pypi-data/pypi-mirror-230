from ic_parent_api import InfiniteCampus
import asyncio
from urllib.parse import urljoin

base_url = "https://rockwoodmo.infinitecampus.org"
username = "sschwartz4230"
secret = "oE7X43H*C6c$"
district = "rockwood"

async def get_students():
	client = InfiniteCampus(f"{base_url}",f"{username}",f"{secret}",f"{district}")
	return await client.students()

async def get_courses(student_id):
	client = InfiniteCampus(f"{base_url}",f"{username}",f"{secret}",f"{district}")
	return await client.courses(student_id)

async def get_assignments(student_id):
	client = InfiniteCampus(f"{base_url}",f"{username}",f"{secret}",f"{district}")
	return await client.assignments(student_id)

async def get_terms():
	client = InfiniteCampus(f"{base_url}",f"{username}",f"{secret}",f"{district}")
	return await client.terms()

students = asyncio.run(get_students())
for student in students:
	courses = asyncio.run(get_courses(student.personid))
	assignments = asyncio.run(get_assignments(student.personid))
	terms = asyncio.run(get_terms())
#print([x.as_dict() for x in students])

urls = ['https://test.infinitecampus.com','https://test.infinitecampus.com/']
path = "campus/test"

for url in urls:
	print(urljoin(url,path))