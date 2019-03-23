IMAGE_NAME=annotation_tool
PORT=8000

build:
	docker build -t $(IMAGE_NAME) .

dev:
	docker run --rm -ti -p $(PORT):$(PORT) \
		-v $(PWD)/:/project \
		-w '/project' \
		$(IMAGE_NAME) \
		gunicorn -b 0.0.0.0:$(PORT) --chdir app web:app