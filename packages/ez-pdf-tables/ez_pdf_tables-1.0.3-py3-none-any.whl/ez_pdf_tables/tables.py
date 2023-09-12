import csv
import warnings
from typing import List, Tuple, Union

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    KeepTogether,
    Paragraph,
    TableStyle,
)
from reportlab.platypus.tables import Table
from textwrap import TextWrapper

from ez_pdf_tables.constants import (
    A4LETTER,
    ALL_CUSTOM_STYLES,
    BOLD_STYLE,
    HALF_INCH,
    HEADING_STYLE,
    NORMAL_STYLE,
    SUBTITLE_STYLE,
    TITLE_STYLE,
)
from ez_pdf_tables.resources import columns_to_text, df_columns_to_text


def update_all_leadings() -> None:
    """Update the leading attribute in all styles."""
    for i in ALL_CUSTOM_STYLES:
        i.leading = i.fontSize * 1.2


class StandardTable():
    def __init__(
        self,
        data_source: Union[list, pd.DataFrame, str],
        pdf_outfile: str,
        title_text: str = '',
        default_leadings: bool = True,
        **kwargs
    ) -> None:
        self.title_text = title_text
        self.data_source = data_source
        self.final_file = pdf_outfile
        self._set_defaults(kwargs, default_leadings)

    def _set_defaults(
        self,
        override_mapping: dict = {},
        default_leadings: bool = True
    ) -> None:
        # Subtitles, empty by default
        self.subtitle_text = ''
        self.subsubtitle_text = ''
        # The default cell and header styles
        self.cell_style = NORMAL_STYLE
        self.header_style = HEADING_STYLE
        # Default page sizes
        self.page_size = A4LETTER
        self.page_width = self.page_size[0]
        self.page_margin = HALF_INCH
        self.right_page_margin = HALF_INCH
        self.left_page_margin = HALF_INCH
        self.top_page_margin = HALF_INCH / 2
        self.bottom_page_margin = HALF_INCH / 4
        # The wrap_limit for wrap columns
        self.wrap_limit = 30
        # How large the table should be in contrast to canvas
        self.table_scale = 1
        # Default cell size
        self.table_cell_size = 10
        # Default cell font size
        self.cell_fontsize = 18
        # What rows to repeat on each page
        self.repeat_rows = [1,]
        # Default header colour
        self.header_color = colors.cyan
        # Columns to convert to text when generating
        self.columns_as_text = []
        # Draw the table borders or not
        self.borderless = False
        # Define list of column numbers to omit certain columns when drawing
        self.omit_column_list = []
        # Define list of column order, will also drop any omitted columns
        self.order_column_list = []
        # Define list of column numbers to wrap text in
        self.wrap_column_list = []
        # If both bold_criteria and bold_criteria_index used, both must be met.
        # Define list of criteria to check for in each cell to see if that cell
        # should be bold, and/or a row index.
        self.bold_criteria = []
        self.bold_criteria_index = []
        # Bold the remainder of a row after a criteria or index is met if it
        # is also in this list
        self.bold_row_criteria = []
        # Define a manual table style
        self.table_style_override = []
        # Define a manual heading style
        self.override_heading_style = None
        # Set to true to disable wrapping of values in Paragraph()
        self.bypass_table_paragraphs = False
        # Set any defined attributes during initialisation
        for k,v in override_mapping.items():
            setattr(self, k, v)
        # If desired, update leadings once all attributes set
        if default_leadings:
            update_all_leadings()

    def _keep_column_calc(self, column_count: int) -> bool:
        """Determine if data re-arrangement is needed."""
        # If omit or keep column list, determine if any rearrangement is needed
        # by comparing the sorted values for each.
        if not self.order_column_list:
            if not self.omit_column_list:
                # If no omit or keep list, no rearrangement needed
                return False
            else:
                self.order_column_list = [
                    i for i in range(column_count) if i not in self.omit_column_list
                ]
        sorted_kcl = self.order_column_list.copy()
        sorted_kcl.sort()
        if self.order_column_list != sorted_kcl:
            return True
        else:
            return False

    def _read_data(self, omit_column_list: list) -> List[list]:
        """Read the data from the CSV file."""
        truncated_data = []
        if not omit_column_list:
            omit_column_list = []
        if isinstance(self.data_source, list):
            columns_to_text(
                self.data_source,
                [i for i,_ in enumerate(self.data_source[0])]
            )
            raw_data = self.data_source
        elif isinstance(self.data_source, pd.DataFrame):
            df = self.data_source
            df = df_columns_to_text(df, df.columns.tolist())
            raw_data = [df.columns.tolist()] + df.values.tolist()
        else:
            with open(self.data_source, 'rt', encoding='ANSI') as open_ds_path:
                raw_data = list(csv.reader(open_ds_path))
        # Remove excess columns from csv
        for i in raw_data:
            truncated_data.append(
                list(i[j] for j in range(len(i)) if j not in omit_column_list)
            )
        # Check if re-arrangement of column order is needed
        if self._keep_column_calc(len(raw_data[0])):
            rearranged_data = []
            for i, v in enumerate(truncated_data):
                rearranged_data.append(
                    [raw_data[i][j] for j in self.order_column_list]
                )
            truncated_data = rearranged_data
        return truncated_data

    def _autofit(
        self,
        data: List[list],
        page_width: Union[int, float]
    ) -> list:
        """
        Dynamically calculate the max widths of each cell, based on length of
        header cell contents but as a ratio to the overall max page width.
        """
        # Create list of 0s in length of column size.
        sizes = [0 for i in enumerate(data[0])]
        for i in data:
            for j, k in enumerate(i):
                size = len(i[j])
                if size > sizes[j]:
                    # If the length of the data in the cell is longer
                    # than the current max length in sizes, replace it
                    sizes[j] = size
        # If any wrap columns were specified, override their max
        # value to near the self.wrap_limit value
        if self.wrap_column_list:
            for i in self.wrap_column_list:
                sizes[i] = self.wrap_limit * .9
        total_size = sum(sizes)
        # Adjust the final value according to total size and scale
        return [
            (i / total_size * self.table_scale * page_width * .97) for i in sizes
        ]

    def _stylise(
        self,
        data: List[list],
        cell_style: ParagraphStyle,
        header_style: ParagraphStyle
    ) -> List[list]:
        """Set the style for cells."""
        # Map values and style to cells
        for index, row in enumerate(data):
            # Standard style assumed by default
            selected_style = cell_style
            # Skip checking if should be bold if both are empty (default)
            bold_check = not len(
                self.bold_criteria + self.bold_criteria_index + self.bold_row_criteria
            ) == 0
            # Don't bypass the reset by default
            reset_style = True
            # Loop through data to check for bold or paragraph bypass
            for col, val in enumerate(row):
                # Overwrite the cell style for the header
                if index == 0:
                    bold_check = False
                    selected_style = header_style
                    if self.override_heading_style:
                        selected_style = self.override_heading_style
                # Skip wrapping text in Paragraph class if requested
                if self.bypass_table_paragraphs:
                    data[index][col] = val
                else:
                    if bold_check:
                        # Check if entire row should be bold
                        if any(i in [col, val] for i in self.bold_row_criteria):
                            selected_style = BOLD_STYLE
                            # Disable the check for remainder
                            reset_style = False
                            # Change style for previous items
                            for i in range(col):
                                txt = data[index][i].text
                                data[index][i] = Paragraph(txt, selected_style)
                        # Or set to bold by both criteria and index
                        elif self.bold_criteria and self.bold_criteria_index:
                            if (
                                val in self.bold_criteria
                            ) and (
                                col in self.bold_criteria_index
                            ):
                                selected_style = BOLD_STYLE
                        # Or set to bold by either criteria or index
                        else:
                            # Set to bold if in the criteria only
                            if val in self.bold_criteria:
                                selected_style = BOLD_STYLE
                            # Set bold criteria by index only
                            elif col in self.bold_criteria_index:
                                selected_style = BOLD_STYLE
                    data[index][col] = Paragraph(val, selected_style)
                # Revert to cell_style if set to do so
                if reset_style:
                    selected_style = cell_style
        return data

    def _format_cells(
        self,
        data: List[list],
        cell_style: ParagraphStyle,
        header_style: ParagraphStyle
    ) -> Tuple[list, List[list]]:
        """
        Convenience method to call the autofit and stylise methods to
        prepare values for formatting.
        """
        return (
            self._autofit(data, self.page_width),
            self._stylise(data, cell_style, header_style)
        )

    def _assemble_table(
        self,
        in_data:
        List[list],
        row_heights: bool = False
    ) -> Table:
        """Create the table object and auto-check a few attributes."""
        column_widths, data = self._format_cells(
            in_data,
            self.cell_style,
            self.header_style
        )
        if row_heights:
            try:
                t = Table(
                    data,
                    colWidths=column_widths,
                    style=self.table_style,
                    repeatRows=self.repeat_rows,
                    rowHeights=row_heights
                )
            except Exception as e:
                # If the row heights don't match the data, try to truncate
                if 'rows in data but' and 'in row heights' in str(e):
                    msg = (
                        "Number of rows in row_heights doesn't match number"
                        " of rows in data. Attempting to automatically correct."
                    )
                    warnings.warn(msg)
                    row_heights = [
                        v for i, v in enumerate(row_heights) if i < len(in_data)
                    ]
                    t = Table(
                        data,
                        colWidths=column_widths,
                        style=self.table_style,
                        repeatRows=self.repeat_rows,
                        rowHeights=row_heights
                    )
                else:
                    raise
        else:
            t = Table(
                data,
                colWidths=column_widths,
                style=self.table_style,
                repeatRows=self.repeat_rows
            )
        return t

    def _make_fonts_consistent(self) -> None:
        """Set the fonts to be proportionate."""
        NORMAL_STYLE.fontSize = self.cell_fontsize
        BOLD_STYLE.fontSize = self.cell_fontsize
        HEADING_STYLE.fontSize = NORMAL_STYLE.fontSize

    def _finish(self, pdf_report: SimpleDocTemplate) -> str:
        """Assemble the final pdf."""
        pdf_report.build(self.elements)
        return pdf_report.filename

    def get(
        self,
        consistent_fonts: bool = True,
        update_leadings: bool = True
    ) -> str:
        """create the table after instantiation."""
        data = self._read_data(self.omit_column_list)
        if self.columns_as_text:
            columns_to_text(data, self.columns_as_text)
        # If there's a wrap list, cycle through data and concat
        if self.wrap_column_list:
            wrapper = TextWrapper(width=self.wrap_limit)
            for h, i in enumerate(data):
                if h > 0:
                    for j in self.wrap_column_list:
                        i[j] = wrapper.fill(i[j])
        outfile = self.final_file
        # Set up document
        pdf_report = SimpleDocTemplate(
            outfile,
            pagesize=self.page_size,
            rightMargin=self.right_page_margin,
            leftMargin=self.left_page_margin,
            topMargin=self.top_page_margin,
            bottomMargin=self.bottom_page_margin,
            title=self.title_text
        )
        self.c = canvas.Canvas(outfile, pagesize=self.page_size)
        # Create collection to house all pdf objects
        self.elements = []
        if consistent_fonts:
            self._make_fonts_consistent()
        if update_leadings:
            update_all_leadings()
        # Add texts to elements collection
        self.elements.append(
            KeepTogether(
                Paragraph(self.title_text, TITLE_STYLE)
            )
        )
        if self.subtitle_text != '':
            self.elements.append(
                KeepTogether(
                    Paragraph(self.subtitle_text, SUBTITLE_STYLE)
                )
            )
        if self.subsubtitle_text != '':
            if self.subtitle_text == '':
                msg = 'A subsubtitle_text was given but subtitle_text is empty.'
                warnings.warn(msg)
            self.elements.append(
                KeepTogether(
                    Paragraph(self.subsubtitle_text, SUBTITLE_STYLE)
                )
            )
        # Define cell ranges for table
        # [(start_column, start_row), (end_column, end_row)]
        all_cells = [(0, 0), (-1, -1)]
        header = [(0, 0), (-1, 0)]
        # Define style for table
        if self.table_style_override:
            table_style_selections = self.table_style_override
        else:
            table_style_selections = \
                [
                    ('BOX', header[0], header[1], 0.25, colors.black),
                    ('BACKGROUND', header[0], header[1], self.header_color),
                    ('SIZE', all_cells[0], all_cells[1], self.table_cell_size)
                ]
            if not self.borderless:
                table_style_selections[0] = (
                    'BOX', all_cells[0], all_cells[1], 0.25, colors.black
                )
                table_style_selections.append(
                    (
                        'INNERGRID',
                        all_cells[0],
                        all_cells[1],
                        0.25,
                        colors.black
                    )
                )
        self.table_style = TableStyle(table_style_selections)
        # Create table.
        t = self._assemble_table(data, row_heights=False)
        # Add table to elements collection.
        self.elements.append(t)
        return self._finish(pdf_report)
