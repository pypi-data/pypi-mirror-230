# Contributing to Travo

All contributions and feedback are welcome!

## Developer workflow

Start contributing forking the Travo repository on gitlab.com
https://gitlab.com/travo-cr/travo, then clone your fork locally
```
$ git clone https://gitlab.com/<your_username>/travo
```

Inside the cloned repository you can build the project in
[editable mode](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs)
```
$ pip install -e .
```
To install all the dependencies needed for running the tests
```
$ pi install -e .[test]
```

Then tests can be run either typing `$ pyest` or `$ tox`.
