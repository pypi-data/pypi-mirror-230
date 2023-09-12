# todotree

[![Latest Release](https://gitlab.com/chim1aap/todotree/-/badges/release.svg)](https://gitlab.com/chim1aap/todotree/-/releases) 
[![pipeline status](https://gitlab.com/chim1aap/todotree/badges/master/pipeline.svg)](https://gitlab.com/chim1aap/todotree/-/commits/master) 
[![coverage report](https://gitlab.com/chim1aap/todotree/badges/master/coverage.svg)](https://gitlab.com/chim1aap/todotree/-/commits/master) 
[![Commit activity](https://img.shields.io/gitlab/commit-activity/m/chim1aap/todotree)](https://img.shields.io/gitlab/commit-activity/m/chim1aap/todotree)
[![License](https://img.shields.io/gitlab/license/chim1aap/todotree)](https://img.shields.io/gitlab/license/chim1aap/todotree)

A [todo.txt](http://todotxt.org/) implementation with more features:

- Define task dependency using the `bl:` and `by:` keywords.
- Hide tasks until a certain date using the `t:` keyword.
- Define due dates for tasks with the `due:` keyword.
- `git` integration.

- **GitLab repository**: <https://gitlab.com/chim1aap/todotree/>
- **Documentation** <https://chim1aap.gitlab.io/todotree/>

## Installation
To install the package, use `pip install todotree`.

Then, to initialize the needed files, run the following scripts:
```commandline
mkdir -p ~/.local/share/todotree/
touch ~/.local/share/todotree/todo.txt
touch ~/.local/share/todotree/done.txt
touch ~/.local/share/todotree/config.yaml
```



To make use of the `git` versioning, the following steps need to be done.

1. install `git`.
2. run `git init` in the directory where the todo.txt and done.txt are.
3. run `git remote add origin <url>` to set up a remote repository.
4. Set the `git_mode` in the configuration to `Full`.
5. run a todotree command which edits the files, such as `add` or `do`. It will push the data to the remote repository.

## Screenshots

projecttree

![projecttree](img/projecttree-example.png)

contexttree

![contexttree](img/contexttree-example.png)

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
