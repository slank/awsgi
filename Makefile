dist/awsgi-0.0.1.tar.gz:
	python setup.py sdist

dist/awsgi-0.0.1-py2-none-any.whl:
	python setup.py bdist_wheel

.PHONY: clean
clean:
	rm -rf dist build awsgi.egg-info
