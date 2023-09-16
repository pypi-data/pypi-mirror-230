# Contributing to model_dml

First off, thanks for taking the time to contribute!

## Who is concerned by this file

This file is for:

- Project owners - creators and maintainers of the project
- Project contributors - users of the project who want to know items they're welcome to
  tackle, and tact they need in navigating the project/respecting those involved with
  the project
- Project consumers - users who want to build off the project to create their own
  project

## Code of Conduct

Please note that this project is released with
a [Contributor Code of Conduct](https://lab.frogg.it/dorianturba/model_dml/-/blob/main/CODE_OF_CONDUCT.md).
By participating in this project you agree to abide by its terms.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for model_dml. Following these
guidelines helps maintainers and the community understand your report.

- Use the [issue search][issue search] — check if the issue has already been reported.
- Check if the issue has been fixed — try to reproduce it using the latest `main` branch
  in the repository.
- Isolate the problem — ideally create a reduced test case.

Please provide as much detail as you can. This helps us resolve the issue more quickly.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for model_dml,
which can range from small improvements in existing functionality to proposing new
features.

When you are creating an enhancement suggestion, please:

#### 1. Check Existing Enhancements

Before creating an enhancement suggestion, please check
the [issue tracker][issue search] to see if a similar suggestion has already been made.
If it exists and is still open, add a comment to the existing issue instead of opening a
new one.

#### 2. Provide a Clear Summary

When you create your enhancement suggestion, provide a clear and concise summary in the
title of the issue to help us understand the scope of the suggestion.

#### 3. Describe Your Suggestion

In the issue description, explain the following:

- **What is the current behavior?** Describe what happens in the software currently.
- **What would you like to suggest?** Describe what you want to happen instead.
- **What are the potential benefits of this change?** Describe the benefits of the
  change you suggest.
- **Are there any potential drawbacks?** While every change has potential downsides,
  it's important to try to anticipate them if possible.

You may also want to include additional details, such as how the change might be
implemented.

Your detailed description helps us to understand your ideas clearly, consider them
thoughtfully, and hopefully integrate them into model_dml.

### Merge Requests

The process described here has several goals:

- Maintain model_dml's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible model_dml
- Enable a sustainable system for model_dml's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Use the [MERGE_REQUEST_TEMPLATE.md][merge request template], or one of the other
   templates provided, to describe the changes in your merge request
2. After you submit your merge request, verify that all status checks are passing
3. If a status check is failing, and you believe that the failure is unrelated to your
   change, please leave a comment on the pull request explaining why you believe the
   failure is unrelated.

## Development environment

### All

By running the following command, you'll install the dependencies for Quality and
Testing purposes. See [Quality Standards](#quality-standards) and [Testing](#testing)
for more information.

```shell
pip install --upgrade pip
pip install -e .[ALL]
```

See following sections for more information about each environment.

### Quality Standards

#### Style Guide

Please adhere to
the [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/) to
maintain
consistency in the codebase.

#### Pre-commit hooks

Please use the pre-commit hooks provided in this repository to maintain consistency in
the codebase.

```bash
pip install --upgrade pip
pip install -e .[QUALITY]
pre-commit install
```

You can manually run the pre-commit hooks on all files:

```bash
pre-commit autoupdate
pre-commit run --all-files
```

This will run the following hooks:

- `black`
- `flake8`
- `isort`
- `mypy`
- `ruff`

##### Fixing quality issues

You can automatically fix some of the quality issues by running:

```bash
black .
isort .
```

#### Testing

##### Installing dependencies

```bash
pip install --upgrade pip
pip install -e .[TEST]
```

##### Running tests

###### Environment variables

Before running tests, you can define the following environment variables in a `.env`
file at project root:

```.env
sqlalchemy_test_url = "sqlite:///db.sqlite3"
sqlalchemy_test_file_name = "db.sqlite3"
```

###### Running pytest

Run tests using `pytest` in the root directory.

```bash
pytest
```

## Generating distribution archives

### Build archive

```bash
pip install --upgrade pip
pip install -r build_requirements.txt
python -m build
```

## Share archive

```bash
pip install --upgrade twine
python -m twine upload --repository pypi dist/* --skip-existing
```

You will be prompted for a username and password. For the username, use __token__. For
the password, use the token value, including the pypi- prefix.

[issue search]: https://lab.frogg.it/search?project_id=987&repository_ref=main&scope=issues

[merge request template]: https://lab.frogg.it/dorianturba/model_dml/-/blob/main/.gitlab/merge_request_templates/MERGE_REQUEST_TEMPLATE.md
