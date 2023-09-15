<h1 align="center">lstm</h1>
<p align="center">
Pytorch implementation of LSTM variants
</p>

<p align="center">
    <a href="https://github.com/astariul/lstm/releases"><img src="https://img.shields.io/github/release/astariul/lstm.svg" alt="GitHub release" /></a>
    <a href="https://github.com/astariul/lstm/actions/workflows/pytest.yaml"><img src="https://github.com/astariul/lstm/actions/workflows/pytest.yaml/badge.svg" alt="Test status" /></a>
    <a href="https://github.com/astariul/lstm/actions/workflows/lint.yaml"><img src="https://github.com/astariul/lstm/actions/workflows/lint.yaml/badge.svg" alt="Lint status" /></a>
    <img src=".github/badges/coverage.svg" alt="Coverage status" />
    <a href="https://astariul.github.io/lstm"><img src="https://img.shields.io/website?down_message=failing&label=docs&up_color=green&up_message=passing&url=https%3A%2F%2Fastariul.github.io%2Flstm" alt="Docs" /></a>
    <a href="https://github.com/astariul/lstm/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="licence" /></a>
</p>

<p align="center">
  <i>⚠️ Work In progress</i>
</p>

<p align="center">
  <a href="#description">Description</a> •
  <a href="#install">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#contribute">Contribute</a>
  <br>
  <a href="https://astariul.github.io/lstm/" target="_blank">Documentation</a>
</p>


<h2 align="center">Description</h2>

The **`lstm`** package allows user to easily use various LSTM alternatives, implemented in Pytorch.

Currently implemented : 

* **Nothing**

Roadmap :

* **LSTM** (to ensure we get the same results as Pytorch implementation)
* **GRU** (to ensure we get the same results as Pytorch implementation)
* **CIFG**
* **LiGRU**


<h2 align="center">Install</h2>

Install `lstm` by running :


```
pip install lstm
```


<h2 align="center">Usage</h2>

-> TODO


<h2 align="center">Contribute</h2>

To contribute, install the package locally, create your own branch, add your code (and tests, and documentation), and open a PR !

### Pre-commit hooks

Pre-commit hooks are set to check the code added whenever you commit something.

If you never ran the hooks before, install it with :

```bash
pre-commit install
```

---

Then you can just try to commit your code. If your code does not meet the quality required by linters, it will not be committed. You can just fix your code and try to commit again !

---

You can manually run the pre-commit hooks with :

```bash
pre-commit run --all-files
```

### Tests

When you contribute, you need to make sure all the unit-tests pass. You should also add tests if necessary !

You can run the tests with :

```bash
pytest
```

---

Tests are not included in the pre-commit hooks, because running the tests might be slow, and for the sake of developpers we want the pre-commit hooks to be fast !

Pre-commit hooks will not run the tests, but it will automatically update the coverage badge !

### Documentation

The documentation should be kept up-to-date. You can visualize the documentation locally by running :

```bash
mkdocs serve
```
