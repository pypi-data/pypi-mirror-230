<h1 align="center">
  <br>
   <img src="https://github.com/bossenti/vistafetch/blob/main/docs/img/vistafetch.png?raw=true"
   alt="VistaFetch Logo" title="VistaFetch Logo" width=30%"/>
    <br>VistaFetch
  <br>
</h1>
<h4 align="center">VistaFetch is a simple and lightweight Python library for financial asset data retrieval (stocks, ETFs, etc.) from onvista.de.</h4>
<p align="center">
<a href="http://www.apache.org/licenses/LICENSE-2.0" target="_blank">
    <img src="https://img.shields.io/github/license/apache/streampipes.svg" alt="License Apache 2.0">
</a>
<a href="https://github.com/bossenti/vistafetch/actions/workflows/ci.yml" target="blank">
    <img src="https://github.com/bossenti/vistafetch/actions/workflows/ci.yml/badge.svg" alt="Continuous Integration status"> 
</a>
<a href="https://pypi.org/project/vistafetch/" target="blank">
    <img src="https://img.shields.io/pypi/v/vistafetch" alt="PyPI released version"> 
</a>
<a href="https://pypi.org/project/vistafetch/" target="blank">
    <img src="https://img.shields.io/pypi/pyversions/vistafetch" alt="PyPI supported Python versions"> 
</a>
<a href="https://github.com/psf/black" target="_blank">
    <img src="https://img.shields.io/badge/code%20style-black-black" alt="Code Style: Black">
</a>
<a href="https://github.com/python/mypy" target="_blank">
    <img src="https://img.shields.io/badge/typed-mypy-blue" alt="Typed: MyPy">
</a>
<a href="https://beta.ruff.rs/docs/" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Linting: Ruff">
</a>
<a href="https://python-poetry.org" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" alt="Dependency & Build Management: Poetry">
</a>
<a href="https://pre-commit.com/" target="_blank">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit">
</a>
<a href="https://pydantic.dev" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json" alt="Pydantic v2">
</a>
</p>

> [!WARNING]  
> The API used by this package is not public. Therefore, users should assume that using this package may violate the site's terms of use.
> The author of this package takes no responsibility for how individuals use the code. It is important to use the code respectfully and judiciously, keeping in mind the potential consequences of violating the terms of service and applicable laws.
> Users are encouraged to read the API Terms and Conditions, Acceptable Use Policy, and License Agreements before using any API. These agreements outline the legal, business, and technical considerations that apply to the use of an API.


## ⚡️ Quickstart
Please ensure that `vistafetch` is installed on your machine by running the following command:
```bash
pip install vistafetch
```
The first step is to initiate the client (`VistaFetchClient`):
```python
from vistafetch import VistaFetchClient

client = VistaFetchClient()
```

### 🔎 Exploratory search
The client now enables you to search for assets and allows you to investigate the results:
```python
result = client.search_asset(
    search_term="S&P",
)
result.visualize()
```
This produces the following console output:
```bash
               Financial assets discovered                
┏━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Index ┃      Name      ┃   Asset Type   ┃     ISIN     ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│   0   │    S&P 500     │     INDEX      │ US78378X1072 │
│   1   │ Siemens Energy │     STOCK      │ DE000ENER6Y0 │
│   2   │  Silberpreis   │ PRECIOUS_METAL │ XC0009653103 │
│   3   │      SAP       │     STOCK      │ DE0007164600 │
│   4   │ EURO STOXX 50  │     INDEX      │ EU0009658145 │
└───────┴────────────────┴────────────────┴──────────────┘
```
One now can access the asset of choice:
```python
asset = result.get(3)  # returns SAP in this case

# in case one simply wants the first one, the following shorthand takes you there
asset = result.get()
```
One can now access several parameters of the asset or convert them to a JSON string as show below.
```python
print(asset.isin)
print(asset.as_json())
```
```bash
DE0007164600
{
  "display_type":"Aktie",
  "entity_type":"STOCK",
  "isin":"DE0007164600",
  "name":"SAP",
  "tiny_name":"SAP",
  "wkn":"716460",
}
```

As a final step, the asset provides some recent price-related data:
```python
print(asset.price_data.as_json())
```
```bash
{
  "currency_symbol":"EUR",
  "datetime_high":"2023-08-25T14:17:15Z",
  "datetime_last":"2023-08-25T15:37:14Z",
  "datetime_low":"2023-08-25T15:02:12Z",
  "datetime_open":"2023-08-25T07:00:26.999000Z",
  "high":127.24,
  "last":126.16,
  "low":125.66,
  "open":126.2,
}
```

> [!NOTE]  
> Price data are currently only supported for funds and stocks.
> Feel free to send me a feature request if you'd like to see this feature
> supported for other asset types as well: https://github.com/bossenti/vistafetch/issues/new.
> As an alternative, contributions are welcome at any time.

### 🎯 Targeted search
In case you already know the identifier for your asset (both ISIN and WKN are supported),
you can directly query them. This returns then only one result:
```python
result = client.search_asset(
    search_term="DE0007164600",  # alternatively pass the WKN here
)
sap_stock = result.get()
```

## 🐛 Facing problems
Feel free to open an [issue](https://github.com/bossenti/vistafetch/issues/new) if you experience strange behavior or bugs when using `vistafetch`. <br>
If you are not sure if your problem should be considered a bug or if you have a question in general, reach out via [disussions](https://github.com/bossenti/vistafetch/discussions).


## 💻 Contributing
We welcome and appreciate contributions of any size.
or smaller or straightforward changes, feel free to create a pull request directly. 
If you plan to make significant improvements or extensions, please open an [issue](https://github.com/bossenti/vistafetch/issues/new) 
or [disussion](https://github.com/bossenti/vistafetch/discussions) beforehand.

### Initial Setup
For your convenience, please ensure that you have Poetry and Just installed. You can read more on them by following the links below:
* [poetry](https://python-poetry.org/)
* [just](https://github.com/casey/just)

To get all required dependencies installed, simply start with:
```bash
just poetry-install
```
Additionally, we make use of [pre-commit](https://github.com/pre-commit/pre-commit). To set it up, run the following command:
```bash
pre-commit install
```

To verify that everything is set up correctly, execute the test suite:
```bash
just unit-tests
```

### Code Conformance

Once you implemented your changes, please run the following commands:
```bash
just pretty   # formats the code and applies automatic linting fixes
just check  # checks code for conformance
```

### Opening PR

Please be aware that this repository follows [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/).
So please choose a PR title corresponding to the following:
```bash
<scope>(#<IssueID>): <description>  # supported scopes can be found here: https://github.com/commitizen/conventional-commit-types/blob/master/index.json

# e.g.
docs(#8): provide extensive project readme

# issue id is optional, so the following si valid as well
docs: provide extensive project readme
```

