import ebooklib
from ebooklib import epub

book = epub.read_epub('test.epub')
for item in book.get_items():
    print(item)