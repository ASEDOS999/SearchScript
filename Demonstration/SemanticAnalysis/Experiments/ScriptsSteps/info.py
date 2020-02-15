import os
for i in os.listdir():
	if os.path.isdir(i):
		print(i, len(os.listdir(i)))
