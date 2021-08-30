# Contribute to openpecha-toolkit

Thanks for your interest in contributing to openpecha-toolkit 🎉 The project is maintained
by [@10zinten](https://github.com/10zinten) and [@eroux](https://github.com/eroux),
and we'll do our best to help you get started. This page will give you a quick
overview of how things are organised and most importantly, how to get involved.

## Table of contents

1. [Issues and bug reports](#issues-and-bug-reports)
1. [Contributing to the code base](#contributing-to-the-code-base)
2. [☑️ Naming Conventions](#-naming-conventions)
3. [Code conventions](#code-conventions)
4. [Adding tests](#adding-tests)
5. [Code of conduct](#code-of-conduct)

## Issues and bug reports

* Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/OpenPecha/openpecha-toolkit/issues).
* If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.
* Be sure to add the complete error messages.

## Contributing to the code base

* Follow the [Angular commit convention](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines) when creating patch.
* Open a new GitHub pull request with the patch.
* Ensure that your PR includes a test that fails without your patch, and pass with it.
* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

<a name="-naming-conventions"></a>
## ☑️ Naming Conventions
from [jina](https://github.com/jina-ai/jina/blob/master/CONTRIBUTING.md)

For branches, commits, and PRs we follow some basic naming conventions:

* Be descriptive
* Use all lower-case
* Limit punctuation
* Include one of our specified [types](#specify-the-correct-types)
* Short (under 70 characters is best)
* In general, follow the [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/#summary) guidelines

Note: If you don't follow naming conventions, your commit will be automatically flagged to be fixed.

### Specify the correct types

Type is an important prefix in PR, commit message. For each branch, commit, or PR, we need you to specify the type to help us keep things organized. For example,

```
feat: add hat wobble
^--^  ^------------^
|     |
|     +-> Summary in present tense.
|
+-------> Type: chore, docs, feat, fix, refactor, style, or test.
```

- build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- ci: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
- docs: Documentation only changes
- feat: A new feature
- fix: A bug fix
- perf: A code change that improves performance
- refactor: A code change that neither fixes a bug nor adds a feature
- style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- test: Adding missing tests or correcting existing tests
- chore: updating grunt tasks etc; no production code change

### Naming your Branch

Your branch name should follow the format `type-scope(-issue_id)`:

* `type` is one of the [types above](#specify-the-correct-types)
* `scope` is optional, and represents the module your branch is working on.
* `issue_id` is [the GitHub issue](https://github.com/OpenPecha-dev/openpecha-toolkit/issues) number. Having the correct issue number will automatically link the Pull Request on this branch to that issue.

> Good examples:
>
```text
fix-executor-loader-113
chore-update-version
docs-add-cloud-section-33
```

> Bad examples:
>

| Branch name     | Feedback                                              |
| ---             | ---                                                   |
| `FIXAWESOME123` | Not descriptive enough, all caps, doesn't follow spec |
| `NEW-test-1`    | Should be lower case, not descriptive                 |
| `mybranch-1`    | No type, not descriptive                              |

### Writing your Commit Message

A good commit message helps us track openpecha-toolkit's development. A Pull Request with a bad commit message will be *rejected* automatically in the CI pipeline.

Commit messages should stick to our [naming conventions](#naming-conventions) outlined above, and use the format `type(scope?): subject`:

* `type` is one of the [types above](#specify-the-correct-types).
* `scope` is optional, and represents the module your commit is working on.
* `subject` explains the commit, without an ending period`.`

For example, a commit that fixes a bug in the executor module should be phrased as: `fix(executor): fix the bad naming in init function`

> Good examples:
>
```text
fix(indexer): fix wrong sharding number in indexer
feat: add remote api
```

> Bad examples:
>

| Commit message                                                                                | Feedback                           |
| ---                                                                                           | ---                                |
| `doc(101): improved 101 document`                                                             | Should be `docs(101)`              |
| `tests(flow): add unit test for flow exception`                                               | Should be `test(flow)`             |
| `DOC(101): Improved 101 Documentation`                                                        | All letters should be in lowercase |
| `fix(pea): i fix this pea and this looks really awesome and everything should be working now` | Too long                           |
| `fix(pea):fix network receive of the pea`                                                     | Missing space after `:`            |
| `hello: add hello-world`                                                                      | Type `hello` is not allowed          |

#### What if I Mess Up?

We all make mistakes. GitHub has a guide on [rewriting commit messages](https://docs.github.com/en/free-pro-team@latest/github/committing-changes-to-your-project/changing-a-commit-message) so they can adhere to our standards.

You can also install [commitlint](https://commitlint.js.org/#/) onto your own machine and check your commit message by running:

```bash
echo "<commit message>" | commitlint
```

### Naming your Pull Request

We don't enforce naming of PRs and branches, but we recommend you follow the same style. It can simply be one of your commit messages, just copy/paste it, e.g. `fix(readme): improve the readability and move sections`.

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
