# PDFInsight
Text Mining &amp; Classification Toolkit

Extract and categorise text-based PDFs into the following categories
- table of contents
- header
- heading
- tables
- content
- footnote
- footer
- page number
- unsure (text that cannot be categorised)

Prepare the extracted content into a document store ready for ingestion by a sentence transformers model

## Installation
`pip install pdfinsight`

## Example
```
from pdfinsight import pdf_extractor, remove_toc, pivot_df_by_heading, df2docstore
df = pdf_extractor("sample.pdf")
df
```
|	|file	|page	|block	|refined_block	|block_ymin_diff	|block_is_list	|...	|font_characteristics	|font	|font_color	|text	|image	|cat|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|0	|tests/sample.pdf	|1	|2	|1	|NaN	|False	|...	|0	|Calibri	|0	|THIS IS A	|	|toc|
|1	|tests/sample.pdf	|1	|3	|2	|95.0	|False	|...	|0	|Calibri	|0	|SAMPLE PDF	|	|toc|
|2	|tests/sample.pdf	|2	|1	|3	|-373.0	|False	|...	|0	|Calibri	|0	|Sample PDF	|	|toc|
|3	|tests/sample.pdf	|2	|6	|5	|-707.0	|False	|...	|16	|Calibri-Bold	|0	|TITLE	|	|toc|
|4	|tests/sample.pdf	|2	|7	|6	|30.0	|False	|...	|0	|Calibri	|0	|Lorem ipsum dolor sit amet, consectetur adipis...	|	|toc|
|...	|...	|...	|...	|...	|...	|...	|...	|...	|...	|...	|...	|...	|...|
|76	|tests/sample.pdf	|3	|15	|20	|-15.0	|False	|...	|0	|Calibri	|0	|3956	|	|table|
|77	|tests/sample.pdf	|3	|13	|20	|59.0	|False	|...	|0	|Calibri	|0	|euismod sit amet tortor.	|	|table|
|78	|tests/sample.pdf	|3	|14	|20	|-15.0	|False	|...	|0	|Calibri	|0	|rhoncus semper.	|	|table|
|79	|tests/sample.pdf	|3	|3	|15	|730.0	|False	|...	|0	|Calibri	|4485572	|THIS IS A FOOTER	|	|footer|
|80	|tests/sample.pdf	|3	|4	|15	|14.0	|False	|...	|0	|Calibri	|4485572	|Page 3 of 3	|	|footer|

```
# remove rows where cat column is marked as 'toc' 
df = remove_toc(df)

# pivot the dataframe such that for each row's text, it will
# 1) merge with previous row if they are of the same category
# 2) it will iteratively search up the rows to search for the 
#    relevant headings for the row's text
pivot_df = pivot_df_by_heading(df)
pivot_df
```
|	|file	|heading1	|heading2	|content|
|---|---|---|---|---|
|0	|tests/sample.pdf	|TITLE	|None	|Lorem ipsum dolor sit amet, consectetur adipis...|
|1	|tests/sample.pdf	|TITLE	|Maecenas eu dapibus diam.	|a) Suspendisse id sem sed lacus luctus digniss...|
|2	|tests/sample.pdf	|TITLE	|Proin at lorem eu	|Proin at lorem eu urna volutpat dignissim vel ...|

```
# set the links to be the same as the filename
link_dict = dict(zip(transformed_df.file.unique(), transformed_df.file.unique()))

# convert the pivot_df into a dictionary format suitable for ingestion by a sentence transformers model
docStore = df2docstore(pivot_df, chunk_size = 100, link_dict = link_dict)
docStore
```
output:
```json
[{'content': 'TITLE\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Nam accumsan sollicitudin ullamcorper. Integer id vestibulum risus. Suspendisse odio erat, venenatis dictum mi at, porttitor cursus mauris. Mauris non leo eu nisi rhoncus lacinia bibendum vitae orci. Maecenas diam lectus, ultricies vitae enim a, maximus porta magna. Fusce posuere dolor blandit, egestas leo posuere, ornare enim. Ut dignissim iaculis leo eu euismod. Etiam pulvinar ac ex non pretium. Sed tempus in est vitae tristique. Sed ac justo ut eros gravida laoreet in vel erat. Sed finibus non ante elementum pretium. Proin leo nunc, feugiat vel nulla at, porttitor pulvinar nibh.\n1. Sed rhoncus posuere mattis.\n2. Fusce dictum nisi at faucibus vulputate.\n3. Cras massa velit, suscipit a eros et, aliquet consequat mauris. Proin maximus pharetra ligula bibendum commodo. Fusce quis neque dui. In molestie purus et turpis maximus ultricies. Morbi ultricies tincidunt tellus, ac pharetra urna consequat a. Nullam consequat leo lobortis aliquet tincidunt. Etiam lacinia fermentum ipsum. Phasellus dapibus leo magna, nec sollicitudin sapien aliquet vel. Suspendisse a ante sed tortor sollicitudin luctus non nec ligula. Ut auctor elit sed dui sodales blandit. Fusce vulputate magna non arcu mollis, eu eleifend erat tincidunt. Aenean consectetur, erat vel sollicitudin venenatis, felis ante cursus velit, quis pellentesque tellus lorem id neque. Praesent viverra tincidunt odio, in luctus tellus sodales viverra.',
  'source': 'tests/sample.pdf',
  'update': ''},
 {'content': 'TITLE\nMaecenas eu dapibus diam.\na) Suspendisse id sem sed lacus luctus dignissim ac eu mi. Praesent eu nisl enim. Etiam ac libero sapien. Mauris at eros neque. Vestibulum lectus ligula, tempor accumsan nunc ut, sodales rhoncus purus. Duis vel tristique ipsum. Ut nec nulla et turpis finibus pulvinar. Aenean eleifend malesuada sapien vel malesuada. Proin viverra nisi non tellus congue auctor. Nam euismod gravida dui at aliquet. Praesent vitae facilisis libero. Donec vestibulum sodales augue, et commodo mauris. Ut sodales interdum ex, quis feugiat nisi fringilla sit amet. Fusce eget neque ac est ullamcorper tristique at nec leo.\nb) Donec sem enim, fermentum sit amet tincidunt sed, semper sit amet odio. Quisque vitae odio turpis. Aliquam erat volutpat. Suspendisse potenti. Praesent sit amet viverra enim, porta pellentesque turpis. Ut posuere lacus pharetra sapien maximus, sed feugiat mi eleifend. Duis congue eros in blandit varius. Maecenas efficitur, urna sed commodo pulvinar, mi nisi consectetur augue, vel sagittis tortor risus nec tellus. Nam sollicitudin lacus eu enim fringilla, vel dapibus quam mattis. Nullam ac leo et 1 mauris pharetra dictum ac quis tortor . Aenean nulla mi, semper ac ultricies sed, placerat et erat. Maecenas ullamcorper, orci eget pulvinar fermentum, magna tortor laoreet magna, eget lacinia quam nulla vitae nulla. Quisque augue lacus, ullamcorper in nunc sed, sodales accumsan dui.',
  'source': 'tests/sample.pdf',
  'update': ''},
 {'content': 'TITLE\nProin at lorem eu\nProin at lorem eu urna volutpat dignissim vel nec erat. Mauris ac dui vel felis rutrum malesuada eget quis ante. Phasellus elementum porta lorem, eu sagittis tortor congue sed. Vivamus nec diam sagittis, sagittis erat nec, lacinia erat. Maecenas at leo metus. Vestibulum sit amet diam ut leo accumsan pharetra. Proin tincidunt vestibulum tincidunt. Pellentesque purus nibh, fermentum sit amet dui at, maximus porttitor sapien.\nColumn 1 Column 2 Column 3 Praesent varius consequat id ultricies diam aliquam 456 justo, volutpat\nVestibulum ante ipsum\net posuere elit elit sed orc 567\nprimis in faucibus orci luctus et ultrices posuere cubilia curae;\ncongue nec molestie et, Nullam posuere nibh ut nisi 3956 euismod sit amet tortor. rhoncus semper.',
  'source': 'tests/sample.pdf',
  'update': ''}]
```

## References
[https://github.com/pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF)