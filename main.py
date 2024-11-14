import argparse
import os
import ebooklib
import ebooklib.epub
from bs4 import BeautifulSoup


def replace_word_in_epub(epub_path, output_path, word_to_replace, replacement_word):
    book = ebooklib.epub.read_epub(epub_path)

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            html_content = item.content.decode('utf-8')

            item.content = find_replace_in_text_nodes(
                html_content, word_to_replace, replacement_word).encode('utf-8')

    ebooklib.epub.write_epub(output_path, book)


def find_replace_in_text_nodes(html: str, search: str, replace: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for element in soup.find_all(string=True):
        if element.strip() and search in element:
            updated_text = element.replace(search, replace)
            element.replace_with(updated_text)

    return str(soup)


def main():
    parser = argparse.ArgumentParser(
        description="Replace words in an EPUB file.")
    parser.add_argument("in_path", help="Path to the input EPUB file")
    parser.add_argument(
        "in_str", help="Word to search for in the EPUB content")
    parser.add_argument(
        "out_str", help="Word to replace the search word with in the EPUB content")
    parser.add_argument(
        "--out_path", default=None, help="Path to save the output EPUB file (default: 'out.' + in_path)")

    args = parser.parse_args()

    if not args.out_path:
        filename = os.path.basename(args.in_path)
        # Prevent adding multiple prefixes if reusing the same epub
        filename = filename.split("out.")[-1]
        name, ext = os.path.splitext(filename)
        args.out_path = f"out.{name}{ext}"

    replace_word_in_epub(args.in_path, args.out_path,
                         args.in_str, args.out_str)


if __name__ == "__main__":
    main()
