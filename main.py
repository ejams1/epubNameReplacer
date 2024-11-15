import argparse
import os
import re
import zipfile
import shutil
from bs4 import BeautifulSoup


def replace_word_in_epub(epub_path, output_path, word_to_replace, replacement_word):
    extracted_dir = '_extracted_epub'
    if os.path.exists(extracted_dir):
        shutil.rmtree(extracted_dir)
    os.makedirs(extracted_dir)

    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_dir)

    for root, dirs, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(('.xhtml', '.html')):
                file_path = os.path.join(root, file)

                with open(file_path, "r+", encoding='utf-8') as f:
                    updated_content = find_replace_in_text_nodes(
                        f.read(), word_to_replace, replacement_word)

                    f.seek(0)
                    f.write(updated_content)
                    f.truncate()

    # After replacements are complete, compress back to epub
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Preserve directory structure
                arcname = os.path.relpath(file_path, extracted_dir)
                zip_ref.write(file_path, arcname)

    # Clean up
    shutil.rmtree(extracted_dir)


def find_replace_in_text_nodes(html: str, search: str, replace: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    # Compile the regex pattern with word boundaries for case-sensitive replacement
    pattern = r'\b' + re.escape(search) + r'\b'

    for element in soup.find_all(string=True):
        if element.strip():
            # Replace occurrences of the exact word with the new word
            updated_text = re.sub(pattern, replace, element)
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
