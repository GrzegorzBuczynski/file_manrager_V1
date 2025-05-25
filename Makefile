all:
	python file_manager.py
	
push:
	git add .
	git commit -m "make push!"
	@echo manualy write git push


# make fclean