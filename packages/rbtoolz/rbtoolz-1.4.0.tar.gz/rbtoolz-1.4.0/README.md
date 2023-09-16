# RBToolz

RBToolz is a package of generic tools for use in Jupyter Notebooks that currently cover:

  - Quick postprocessing of Pandas DataFrames wrapped around Plotly

### Tech

RBToolz wraps around a number of projects:

* Jupyter Notebook
* Pandas
* Plotly
* Orca

### Installation
Install using regular pip 3.7

```sh
$ pip install rbtoolz
```
### Notebook Setup and Plotting Example

Following steps are required to setup notebook and use postprocessing tools.

Rendering to PNG files requires Orca/PIO installation:

```bash
conda install -c plotly plotly-orca psutil
```

* Notebook cell width to 100% (optional)

```python
from IPython.core.display import display, SVG, HTML
from IPython.display import Image
display(HTML("<style>.container { width:100% !important; }</style>"))
```

* Import Plotly offline functions
```python
from plotly.offline import init_notebook_mode, iplot
```

* Import functions from RBToolz
```python
from rbtoolz.plotting import auto_plot, save_fig
```

* Run a plotting demo
```python
df = pd.DataFrame([1,2,3],['A','B','C'])

line_fig = auto_plot(df)
bar_fig = auto_plot(df, mode='bar')

iplot(line_fig)
iplot(bar_fig)
```

* And for rendering figure to png

```python
save_fig(line_fig,'chart.png')

display(Image('chart.png'))
```

License
----

MIT




