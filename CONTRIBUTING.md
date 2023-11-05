# How to contribute

There are many ways you can contribute to this project, regardless of your level of technical expertise.

Please note that this is part of the BookWyrm project and our code of conduct applies equally to this project. You should also be aware that `bw-file-resubmit` uses the _MIT License_, not the _Anti-Capitalist Software License_ used for BookWyrm.

## Feedback and feature requests

Please feel encouraged and welcome to point out bugs, suggestions, feature requests, and ideas for how things ought to work, using GitHub issues.

## Code contributions

So you want to contribute code to `bw-file-resubmit`: that rules! If there's an open issue that you'd like to fix, it's helpful to comment on the issue so work doesn't get duplicated. Try to keep the scope of pull requests small and focused on a single topic. That way it's easier to review, and if one part needs changes, it won't hold up the other parts.

If you aren't sure how to fix something, or you aren't able to get around to it, that's totally okay, just leave a comment on the pull request and we'll figure it out 💖.

Pull requests have to pass all the automated checks before they can be merged - this includes style checks, global linters, and unit tests.

### How to check your code before submitting your PR

We use [`tox`](https://tox.wiki/en/latest/index.html) for running linters and tests locally. You can install `tox` like this:

```sh
python -m pip install pipx-in-pipx --user
pipx install tox
tox --help
```

Or see [the tox instructions](https://tox.wiki/en/latest/installation.html) for other installation options.

Once you have `tox` installed, you can run commands from the base of your local `bw-file-resubmit` directory to run all the checks we run when you send a pull request:

* `tox`: run pytest
* `tox -e black`: run `black` on all directories
* `tox -e pylint -- src`: run `pylint` on the source code
* `tox -e pylint -- tests`: run `pylint` on the tests

## Asking questions and getting help

If you have questions about the project or contributing, you can join the [BookWyrm matrix chat](https://app.element.io/#/room/#bookwyrm:matrix.org) - just be sure to let people know you're asking about `bw-file-resubmit` rather than the main BookWyrm project.