.PHONY: sdist
sdist:
	python setup.py sdist

.PHONY: wheel
wheel:
	python setup.py bdist_wheel

.PHONY: clean
clean:
	rm -rf dist build aws_wsgi.egg-info
