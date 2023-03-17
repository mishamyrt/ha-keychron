VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;

configure: $(VENV_PATH) 

clean:
	rm -rf venv

$(VENV_PATH): requirements.txt
	python3 -m venv $(VENV_PATH)
	$(VENV) pip install -r requirements.txt