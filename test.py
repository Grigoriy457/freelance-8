import os

PATH = "static/users/00/posts.csv"
PATH_2 = 'static/users/00'

if os.path.exists(PATH):
	with open(PATH, 'w') as file:
		file.write("1")
else:
	os.mkdir(os.path.abspath(PATH_2))
	with open(PATH, 'w') as file:
		file.write("2")