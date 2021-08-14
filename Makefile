dep:
	pip3 install -r requirements.txt

page:
	./get-content.py > index.html

deploy:
	./deploy.sh

bundle: page deploy
