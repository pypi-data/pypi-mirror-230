
# ez_pdf_tables

Quickly make PDF tables.

## Requirements and Supported Environments

Python 3.7+ and Windows or Linux (tested on Ubuntu 20.04.3).

This package is dependent on the following Pythjon packages.
* [reportlab](https://pypi.org/project/reportlab/) 3.5+
* [pandas](https://pypi.org/project/pandas/) 1.3+

## Installation

Install via pypi.

```
pip install ez-pdf-tables
```

## Usage

To create a table, an existing dataset is needed. This can be a path to a CSV file, a pandas `DataFrame` object, or a list of lists.

Provide this along with a destination file and title when instantiating the `StandardTable` object.
```python
from ez_pdf_tables import StandardTable

t = StandardTable(
	r'C:\some\dataset.csv',
	r'C:\some\destination.pdf',
	'My Report'
)
```

This creates the object, but not the PDF itself. To finish creation, call the `get` function.
```python
report_pdf = t.get()
```

`StandardTable` also has an optional `default_leadings` parameter, which is set to `True` by default.
This option sets the `leading` attribute for all defined `ez_pdf_tables` styles in `ALL_CUSTOM_STYLES`
to automatically account for the font size.

Any styles within or added to `ALL_CUSTOM_STYLES` list will be updated when ***any***
`StandardTable` is instantiated with `default_leadings` set to `True` and/or `StandardTable.get`
is called with `update_leadings` set to `True`.

### Customization

You can optionally set numerous attributes that make table manipulation simple.
A list of all of the possible attributes is in the Table Attributes section below.
```python
from ez_pdf_tables import StandardTable

t = StandardTable(
	'/some/dataset.csv',
	'/some/destination.pdf',
	'Another Report',
	subtitle_text = 'A Subtitle',
	borderless = True
)
t.get()
```

Alternatively, all attributes can be set after instantiation. The below produces the same result as the above.
```python
from ez_pdf_tables import StandardTable

t = StandardTable(
	'/some/dataset.csv',
	'/some/destination.pdf',
	'Another Report',
)
t.subtitle_text = 'A Subtitle',
t.borderless = True
t.get()
```
#### Be Aware

There are a few options that may conflict with one another, or override each other.
For instance, `table_style_override` will ignore `borderless`, since it is expected the user
will specify exactly their custom `reportlab.lib.styles.ParagraphStyle` object.

## To Do

* Documentation.
* Ambiguous variable names - some variables are named poorly.

## All `StandardTable` Attributes

This section explains all the possible attributes that can manipulate a table's appearance, and their default values.

Text to appear below the title. By default, both are not drawn. If `subsubtitle_text` is supplied and `subtitle_text` is not, the `subsubtitle_text` will be drawn directly below the title and a warning issued.
* `subtitle_text = ''`
* `subsubtitle_text = ''`

The default cell and header styles.
* `cell_style = NORMAL_STYLE`
* `header_style = HEADING_STYLE`

Default page sizes. `A4LETTER` is equal to `(913.92, 666.96)`.
* `page_size = A4LETTER`
* `page_width = self.page_size[0]`
* `page_margin = HALF_INCH`
* `right_page_margin = HALF_INCH`
* `left_page_margin = HALF_INCH`
* `top_page_margin = HALF_INCH / 2`
* `bottom_page_margin = HALF_INCH / 4`

How large the table should be in contrast to canvas.
* `table_scale = 1`

Default cell size and font size.
* `table_cell_size = 10`
* `cell_fontsize = 18`

Which rows to repeat on each page. If changed to and empty list, none will repeat.
* `repeat_rows = [1,]`

Default header colour, which is `reportlab.lib.colors.cyan`.
* `header_color = colors.cyan`

Draw the table borders or not.
* `borderless = False`

Define a list of column indices to omit certain columns when drawing.
* `omit_column_list = []`
	* Example: `t.omit_column_list = [3,9,14]`

Define a list of column indices to set the column order, will also drop any omitted columns
* `order_column_list = []`
	* Example: `t.order_column_list = [0,1,2,5,3]` will rearrange the dataset to put column 5 after column 2 and omit column 4.

The length of text a column must reach to be automatically text-wrapped. It is not recommended to set this very high.
* `wrap_limit = 30`

Define a list of column indices to wrap text in.
* `wrap_column_list = []`

Define a list of criteria to check for in each cell to see if that entire row should be bold, and/or define a column index where an entire row should be bolded after. Note that if both `bold_criteria` and `bold_criteria_index` are specified, both must be met.
* `bold_criteria = []`
	* Example: `t.bold_criteria = ['Total', 'Count']` will bold cells that match either "Total" or "Count".
* `bold_criteria_index = []`
	* Example: `t.bold_criteria_index = [3,]` will bold any cell that is within the target column, 3.

Bold the entire row if a criteria is met and is in this list. Note this list can contain criteria without needing to be in bold_criteria.
* `bold_row_criteria = []`

Define a manual table style. Do not pass a `reportlab.platypus.TableStyle` object here! Pass the parameters to be passed to the object. See the [ReportLab documentation (section 7.2, page 85)](https://www.reportlab.com/docs/reportlab-userguide.pdf) for information on creating a manual table style.
* `table_style_override = []`

Define a manual heading style. Must be a `reportlab.lib.styles.ParagraphStyle` object.
* `override_heading_style = None`

Set to true to disable wrapping of cell values in `reportlab.platypus.Paragraph`. Also prevents any `reportlab.lib.styles.ParagraphStyle` from being applied to cells.
* `bypass_table_paragraphs = False`

Columns to convert to text when generating. Note that this shouldn't ever be needed as `pandas.DataFrame` and `list` are both converted to text automatically during processing.
* `columns_as_text = []`

### Styles

All included styles in `ez_pdf_tables` are added to the `ALL_CUSTOM_STYLES` list constant.

* `NORMAL_STYLE` is `reportlab.lib.styles.getSampleStyleSheet()['Normal']`.
* `HEADING_STYLE` is `reportlab.lib.styles.getSampleStyleSheet()['Heading5']`.
* `TITLE_STYLE` is based on `reportlab.lib.styles.getSampleStyleSheet()['Title']`, with the following modifications:
	* Center alignment
	* Font size of 48
	* Font type of Helvetica
* `SUBTITLE_STYLE`  is based on `reportlab.lib.styles.getSampleStyleSheet()['Title']`, with the following modifications:
	* Font size of 22
	* Space after text of 6
* `BOLD_STYLE` is the same as `NORMAL_STYLE` but with a font type of Helvetica-Bold.
* `CENTERED_STYLE` is the same as `NORMAL_STYLE` but with center alignment.
* `SMALL_STYLE` is the same as `NORMAL_STYLE` but with a font size of 6.
* `BLUE_HIGHLIGHT_STYLE`, `YELLOW_HIGHLIGHT_STYLE`, and `GREEN_HIGHLIGHT_STYLE` are all the same as `NORMAL_STYLE` but with back color of `reportlab.lib.colors.PCMYKColor(25,0,0,0)` (blue),  `reportlab.lib.colors.PCMYKColor(0,0,33,0)` (yellow), and `reportlab.lib.colors.PCMYKColor(25,0,25,0)` (red), respectively.
	* They are all usused and left as examples/options.
	* Each sets `backColor` initially to a preset `reportlab.lib.colors` option and then overwrites it. This is left as an example of what can be done.

### Additional Features
When creating PDF reports, it can be advantageous to produce a multiindex dataset without repeating the indices.
This package contains a method for just that, `multiindex_as_is`.

In `pandas`,  a multiindex can be set on a `DataFrame` via passing a list of target
indices to `pandas.DataFrame.set_index`. The same logic will apply here.
```python
from ez_pdf_tables import multiindex_as_is

df = pd.read_csv(r'C:\some\dataset.csv')
df = multiindex_as_is(df, ['List', 'Of', 'Indices'])
```

Using this method can produce some pleasant tables. See examples for a full example.

## Examples

### Make a Default Table

No frills, default options.
```python
from ez_pdf_tables import StandardTable

t = StandardTable(
	'/home/username/Desktop/salaries.csv',
	'/home/username/Desktop/salaries.pdf',
	'Employee Salaries'
)
t.get()
```
!["A default table."](https://github.com/LamerLink/ez_pdf_tables/blob/main/photos/default.png?raw=true)

### Borderless and Subtitles

Setting the table to be borderless and adding a subtitle.
```python
t = StandardTable(
	'/home/username/Desktop/salaries.csv',
	'/home/username/Desktop/salaries.pdf',
	'Employee Salaries',
	borderless=True,
	subtitle_text='As of 05/20/2020'
)
t.get()
```
!["A borderless table with subtitles."](https://github.com/LamerLink/ez_pdf_tables/blob/main/photos/borderless_subtitle.png?raw=true)

### Using Bold

Specifying values in the `bold_criteria` parameter is a simple way to apply bold selectively.
```python
t = StandardTable(
	r"C:\some\dataset.csv",
	r"C:\some\bold.pdf",
	'Team Scores',
    bold_criteria = ['Yes',]
)
t.get()
```
!["A table with bold_criteria."](https://github.com/LamerLink/ez_pdf_tables/blob/main/photos/bold1.png?raw=true)

However, it can be problematic if values are repeated in multiple columns.
!["A problematic table with bold_criteria."](https://github.com/LamerLink/ez_pdf_tables/blob/main/photos/bold2.png?raw=true)

In this case, using `bold_criteria_index` with `bold_criteria` can narrow the search.
```python
t = StandardTable(
	r"C:\some\dataset.csv",
	r"C:\some\bold.pdf",
	'Team Scores',
    bold_criteria = ['Yes',],
    bold_criteria_index = [2,]
)
t.get()
```
!["A table with bold_criteria_index."](https://github.com/LamerLink/ez_pdf_tables/blob/main/photos/bold3.png?raw=true)

Of course, if an entire column should always be bold, using `bold_criteria_index` alone works, too.
```python
t = StandardTable(
	r"C:\some\dataset.csv",
	r"C:\some\bold.pdf",
	'Team Scores',
    bold_criteria_index = [2,]
)
t.get()
```

Sometimes it may be desirable to embolden the entire row if the row contains some criteria.
This can be defined similar to the above, by cell contents, in `bold_row_criteria`.
```python
t = StandardTable(
	r"C:\some\dataset.csv",
	r"C:\some\bold.pdf",
	'Team Scores',
    bold_row_criteria = [15,]
)
t.get()
```
!["A table with bold_row_criteria."](https://github.com/LamerLink/ez_pdf_tables/blob/main/photos/bold4.png?raw=true)

Combining all of these is possible, but likely unnecessary.
```python
t = StandardTable(
	r"C:\some\dataset.csv",
	r"C:\some\bold.pdf",
	'Team Scores',
    bold_criteria = ['Yes',],
    bold_criteria_index = [2,],
    bold_row_criteria = [15,]
)
t.get()
```
!["A table with all bold options."](https://github.com/LamerLink/ez_pdf_tables/blob/main/photos/bold5.png?raw=true)

### Multiindex Tables

Multiindex allows tables to have sorted and/or hanging values. Pass a CSV file or `pandas.DataFrame` object into the `multiindex_as_is` function, along with a list of what indices should be used, in the correct order.
```python
from ez_pdf_tables import multiindex_as_is, StandardTable

mi = multiindex_as_is(r"C:\some\dataset.csv", ['Team','Score'])
t = StandardTable(mi, r"C:\some\mi.pdf", 'Team Scores')
t.borderless = True # These look great borderless
t.get()
```
!["A multiindex table."](https://github.com/LamerLink/ez_pdf_tables/blob/main/photos/multiindex.png?raw=true)
