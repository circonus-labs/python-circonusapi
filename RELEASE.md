# Release procedure

1. Edit setup.py and increase the version number
2. Update ./docs/changelog.rst
3. Commit the change to setup.py with a message:

    v0.x.y

4. Create the release and upload to pypi:

    ./setup.py sdist upload

5. Publish updated documentation

    make docs-publish
