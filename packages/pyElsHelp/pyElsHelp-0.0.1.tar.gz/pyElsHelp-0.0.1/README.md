# pyElsHelp Library #

## What is this? ##
The module allows you to authenticate and get information from ELSCHOOL diary with your login and password

## Quick Guide ##
The module is based on the following structure:

	user = ElsUser(login='login', password='pass')

	print(user.auth())
	print(user.get_class())
	print(user.get_marks(subject='math', period='1'))

## Developer ##
My GitHub profile [here](https://github.com/theslothbear)