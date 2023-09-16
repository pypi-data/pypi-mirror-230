import mistune
# pip install mistune

def convert_markdown_to_html(markdown_content):
    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer=renderer)
    html = markdown(markdown_content)
    return html
