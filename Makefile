.PHONY: docs
docs:
	cd docs && html

.PHONY: docs-publish
docs-publish:
	git checkout -b docs_stage
	cd docs && make html
	echo "." > docs/_build/html/.nojekyll
	git add docs/_build/html
	git commit -m "Add docs/html"
	# There is no force-push for git subtree. Need to delete the remote branch first:
	git push origin --delete gh-pages
	git subtree push --prefix docs/_build/html origin gh-pages
	cd docs && make clean
	git checkout master
	git branch -D docs_stage

.PHONY: install
install:
	python setup.py install

.PHONY: test
test:
	cd test; bash run.sh

.PHONY:
test-docker:
	# Run test in supported docker environments
	docker run --rm -it -v "$$(pwd):/app" python:2.7-buster bash -c 'cd /app; make install test'
	docker run --rm -it -v "$$(pwd):/app" python:3.5-buster bash -c 'cd /app; make install test'
	docker run --rm -it -v "$$(pwd):/app" python:3.6-buster bash -c 'cd /app; make install test'
	docker run --rm -it -v "$$(pwd):/app" python:3.7-buster bash -c 'cd /app; make install test'
