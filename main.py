import argparse
import os
import re
import zipfile
import shutil
from lxml import etree


def apply_replacements(extracted_dir: str, word_to_replace, replacement_word) -> None:
    for root, dirs, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(('.xhtml')):
                file_path = os.path.join(root, file)

                with open(file_path, "r+", encoding='utf-8') as f:
                    original_content = f.read()

                    # Remove XML declaration if present
                    updated_content = remove_xml_declaration(original_content)

                    # Parse the XHTML content
                    tree = etree.fromstring(
                        updated_content, parser=etree.XMLParser(recover=True))

                    # Perform replacements on text nodes
                    updated_content = find_replace_in_text_nodes(
                        tree, word_to_replace, replacement_word)

                    # Add back the XML declaration and doctype to make it valid XHTML again
                    updated_content = add_xml_and_doctype(updated_content)

                    # Re-write the file with the updated content
                    f.seek(0)
                    f.write(updated_content)
                    f.truncate()


def remove_xml_declaration(content: str) -> str:
    # Remove the XML declaration (<?xml version="1.0" encoding="UTF-8"?>)
    if content.startswith('<?xml'):
        content = content.split('?>', 1)[-1]

    return content


def add_xml_and_doctype(content: str) -> str:
    # Add the XML declaration and DOCTYPE declaration back to the content
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    doctype_declaration = '<!DOCTYPE html>\n'

    # Add the declarations at the beginning of the content
    return xml_declaration + doctype_declaration + content


def extract_epub(epub_path: str) -> str:
    extracted_dir = '_extracted_epub'
    if os.path.exists(extracted_dir):
        shutil.rmtree(extracted_dir)
    os.makedirs(extracted_dir)

    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_dir)

    return extracted_dir


def compress_epub(output_path: str, extracted_dir: str) -> None:
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        # Write the mimetype file uncompressed first
        mimetype_path = os.path.join(extracted_dir, 'mimetype')
        zip_ref.write(mimetype_path, 'mimetype',
                      compress_type=zipfile.ZIP_STORED)

        # Add the rest of the files with deflate compression
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Preserve directory structure
                arcname = os.path.relpath(file_path, extracted_dir)
                if file != 'mimetype':
                    zip_ref.write(file_path, arcname)


def replace_word_in_epub(epub_path: str, output_path: str, word_to_replace: str, replacement_word: str) -> None:
    extracted_dir = extract_epub(epub_path)

    apply_replacements(extracted_dir, word_to_replace, replacement_word)

    compress_epub(output_path, extracted_dir)

    # Clean up
    shutil.rmtree(extracted_dir)


def find_replace_in_text_nodes(tree: etree._Element, search: str, replace: str) -> str:
    for element in tree.iter():
        if element.text:
            updated_text = re.sub(
                r'\b' + re.escape(search) + r'\b', replace, element.text)
            element.text = updated_text

        # Also check tail text (text after the element itself)
        if element.tail:
            updated_tail = re.sub(
                r'\b' + re.escape(search) + r'\b', replace, element.tail)
            element.tail = updated_tail

    # Return the modified XML as a string
    return etree.tostring(tree, encoding='utf-8', method='xml').decode('utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Replace words in an EPUB file.")
    parser.add_argument("in_path", help="Path to the input EPUB file")
    parser.add_argument(
        "in_str", help="Word to search for in the EPUB content")
    parser.add_argument(
        "out_str", help="Word to replace the search word with in the EPUB content")
    parser.add_argument("--out_path", default=None,
                        help="Path to save the output EPUB file (default: 'out.' + in_path)")

    args = parser.parse_args()

    if not args.out_path:
        filename = os.path.basename(args.in_path)
        filename = filename.split("out.")[-1]
        name, ext = os.path.splitext(filename)
        args.out_path = f"out.{name}{ext}"

    replace_word_in_epub(args.in_path, args.out_path,
                         args.in_str, args.out_str)


if __name__ == "__main__":
    main()
