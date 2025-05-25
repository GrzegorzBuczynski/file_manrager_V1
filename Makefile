push:
	git add .
	git commit -m "make push!"
	@echo manualy write git push

all:
	python file_manager.py

# make fclean