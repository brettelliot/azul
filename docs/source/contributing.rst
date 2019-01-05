============
Contributing
============
This repo uses the `Git Branching Model <https://nvie.com/posts/a-successful-git-branching-model/>`_. The head of master branch should always be production ready. The head of the develop branch should contain the latest delivered development changes for the next release. Features should be created in feature branches that branch from the develop branch.

Create virtualenv::

    $ mkvirtualenv azul-dev

Then get the repo::

    $ git clone https://github.com/brettelliot/azul.git
    $ pip install -r requirements.txt

Run the tests::

    $ python setup.py test

Creating a ``develop`` branch from the ``master`` branch::

    $ git checkout -b develop master

Creating a new feature branch from the ``develop`` branch::

    $ git checkout -b be-feature develop

Committing code to the new ``be-feature`` branch::

    $ git add .
    $ git commit -am 'Commit message'
    $ git push --set-upstream origin be-feature

Committing code to an existing ``be-feature`` branch::

    $ git add .
    $ git commit -am 'Commit message'
    $ git push


Building the documentation (from the docs/ directory)::

    $ sphinx-apidoc -f -o source/ ../azul/
    $ make html

Incorporating a finished feature onto ``develop``::

    $ git checkout develop
    $ git merge --no-ff be-feature
    $ git push origin develop
    $ git branch -d be-feature
    $ git push origin --delete be-feature

Create a release branch from ``develop``, and merge it into ``master``:

.. parsed-literal::

    $ git checkout -b release-|release| develop
    $ git checkout master
    $ git merge --no-ff release-|release|
    $ git push
    $ git tag -a |release| -m "release |release|"
    $ git push origin |release|

Merge the release branch changes back into ``develop`` so it's up to date:

.. parsed-literal::

    $ git checkout develop
    $ git merge --no-ff release-|release|
    $ git branch -d release-|release|

Generating distribution archives::

    $ git checkout master
    $ python setup.py check --strict --metadata
    $ rm -rf dist/
    $ python3 setup.py sdist bdist_wheel

Upload to test.pypi.org::

    $ twine upload --repository-url https://test.pypi.org/legacy/ dist/*

To test the package from test.pypi.org, create a new virtual env, install the package, then run python and import it::

    $ rm -rf ~/.virtualenvs/azul_test_pypi
    $ mkvirtualenv azul_test_pypi
    $ python3 -m pip install --no-cache-dir --extra-index-url https://test.pypi.org/simple/ azul
    $ python
    >>> import azul
    >>> azul.name
    'azul'
    >>> quit()
    $ deactivate

Upload the package to the real pypi.org website::

    $ twine upload dist/*

To test the package from pypi.org, create a new virtual env, install the package, then run python and import it::

    $ rm -rf ~/.virtualenvs/azul_pypi
    $ mkvirtualenv azul_pypi
    $ pip install --no-cache-dir azul
    $ python
    >>> import azul
    >>> azul.name
    'azul'
    >>> quit()
    $ deactivate

If you're going to use polygon, and you're using virtualenvwrapper then you might want to set the env var using scripts like this. In ``$VIRTUAL_ENV/bin/activate`` add::

    export AZUL_POLYGON_API_KEY=XXX

And in ``$VIRTUAL_ENV/bin/predeactivate`` add::

    unset AZUL_POLYGON_API_KEY

