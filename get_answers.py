import json

from xmodule.modulestore.django import modulestore
from courseware.models import StudentModule

courses = modulestore().get_courses()
c4 = courses[4]

p1 = c4.id.make_usage_key_from_deprecated_string('i4x://international-relations-and-organizations/iro101/problem/93f498da7ef4457caa85c18ed547b5c8')
p2 = c4.id.make_usage_key_from_deprecated_string('i4x://international-relations-and-organizations/iro101/problem/3d594cbde3404d558b91de160765835d')
p3 = c4.id.make_usage_key_from_deprecated_string('i4x://international-relations-and-organizations/iro101/problem/4ec9089271374e5dbdeb2809dc1670a6')
p4 = c4.id.make_usage_key_from_deprecated_string('i4x://international-relations-and-organizations/iro101/problem/2d65781ac76f46a6b1c29a636217124e')
p5 = c4.id.make_usage_key_from_deprecated_string('i4x://international-relations-and-organizations/iro101/problem/91919073d1f64af48679c9a13467fd1f')

ps = [p1,p2,p3,p4,p5]

def get_prob_answers(problem):
	student_module_data = StudentModule.objects.filter(course_id = c4.id, module_state_key=problem)
	student_module_data = student_module_data.order_by('student')
	datatable = {'header': ['user_id', 'username', 'email', 'answer', 'correctness']}
	datatable['data'] = [[int(x.student.id), x.student.username, x.student.email, get_answer_from_state(x.state), get_correctness_from_state(x.state)] for x in student_module_data]

	return datatable



def get_answer_from_state(state_json):
	state = json.loads(state_json)
	student_answers = state.get('student_answers', '')
	if student_answers:
		answer = state['student_answers'].items()[0][1]
	else:
		answer = ''

	return answer

def get_correctness_from_state(state_json):
	state = json.loads(state_json)
	student_answers = state.get('student_answers', '')
	if student_answers:
		correctness = state['correct_map'].items()[0][1]['correctness']
	else:
		correctness = ''

	return correctness