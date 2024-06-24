import sys
from bs4 import BeautifulSoup

# ANSI color codes
ansi_colors = {
    'c000000': '\033[30m',
    'cFFFFFF': '\033[37m',
    'cFFFF00': '\033[33m',
    'c00FF00': '\033[32m',
    'c0000FF': '\033[34m',
    'c00FF00': '\033[32m',
    'bc000000': '\033[40m',
    'bcFFFFFF': '\033[47m',
    'bcFFFF00': '\033[43m',
    'bc00FF00': '\033[42m',
    'bc0000FF': '\033[44m'
}

# ANSI reset code
ansi_reset = '\033[0m'

# Function to convert teletextlinedrawregular characters to ANSI blocks
def convert_line_draw(char):
    if char == '/':
        return '\u2588'  # Full block
    elif char == ',':
        return '\u2584'  # Lower half block
    elif char == "'":
        return '\u2580'  # Upper half block
    else:
        return '\u2588'  # Default to full block for other characters

# Function to process span tags
def process_span(span):
    classes = span.get('class', [])
    style = ''
    
    for cls in classes:
        if cls in ansi_colors:
            style += ansi_colors[cls]
    
    content = span.text
    if 'teletextlinedrawregular' in classes:
        content = ''.join(convert_line_draw(char) for char in content)
    
    return style + content + ansi_reset

# Read the HTML file from stdin
html_content = sys.stdin.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the content div
content_div = soup.find('div', id='content')

if content_div:
    # Process each row within the content div
    for row_div in content_div.find_all('div', class_='row'):
        row_content = ''
        for span in row_div.find_all('span'):
            row_content += process_span(span)
        # Print the row content
        print(row_content)
else:
    print("No content found with id 'content'.", file=sys.stderr)
