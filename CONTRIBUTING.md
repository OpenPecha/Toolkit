# Contribute to openpecha-toolkit

Thanks for your interest in contributing to openpecha-toolkit 🎉 The project is maintained
by [@10zinten](https://github.com/10zinten) and [@eroux](https://github.com/eroux),
and we'll do our best to help you get started. This page will give you a quick
overview of how things are organised and most importantly, how to get involved.

## Table of contents

1. [Issues and bug reports](#issues-and-bug-reports)
1. [Contributing to the code base](#contributing-to-the-code-base)
1. [Code conventions](#code-conventions)
1. [Adding tests](#adding-tests)
1. [Code of conduct](#code-of-conduct)

## Issues and bug reports

* Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/OpenPecha/openpecha-toolkit/issues).
* If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.
* Be sure to add the complete error messages.

## Contributing to the code base

* Follow the [Angular commit convention](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines) when creating patch.
* Open a new GitHub pull request with the patch.
* Ensure that your PR includes a test that fails without your patch, and pass with it.
* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

## Code conventions

Code should loosely follow [pep8](https://www.python.org/dev/peps/pep-0008/).
Use uses [`black`](https://github.com/ambv/black) for code formatting and 
[`flake8`](http://flake8.pycqa.org/en/latest/) for linting its Python modules.

## Adding tests

openpecha-toolkit uses the [pytest](http://doc.pytest.org/) framework for testing. For more
info on this, see the [pytest documentation](http://docs.pytest.org/en/latest/contents.html).
All the tests live in tests directory in the root of the project.

When adding tests, make sure to use descriptive names, keep the code short and
concise and only test for one behaviour at a time. Try to `parametrize` test
cases wherever possible

## Code of conduct

openpecha-toolkit adheres to the
[Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).
By participating, you are expected to uphold this code.
