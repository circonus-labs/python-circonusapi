# Release procedure

 * Edit setup.py and increase the version number
 * Commit the change to setup.py with a message:

        Version bump to 0.1.X
 * Create the release and upload to pypi:

        ./setup.py sdist upload
