### vial-gui

# Docs and getting started

### Please visit [get.vial.today](https://get.vial.today/) to get started with Vial

Vial is an open-source cross-platform (Windows, Linux and Mac) GUI and a QMK fork for configuring your keyboard in real time.


![](https://get.vial.today/img/vial-win-1.png)


---


#### Releases

Visit https://get.vial.today/ to download a binary release of Vial.

#### Development

The project can be developed with Python 3.10 using [uv](https://docs.astral.sh/uv/).

Install dependencies with uv:

```
uv sync
```

To launch the application afterwards:

```
uv run fbs run
```

To run tests:

```
uv run pytest
```

If you prefer the legacy setup, Python 3.6 with `venv` and `pip` is still supported
(3.6 is the latest version officially supported by `fbs`).

Install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To launch the application afterwards:

```
source venv/bin/activate
fbs run
```
