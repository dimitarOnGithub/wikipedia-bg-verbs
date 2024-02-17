import re
from xml.etree import ElementTree
import sys
from dataclasses import dataclass
from transliterate import translit


@dataclass
class PageInfo:

    title: str
    letter: str
    text: str
    references: list[str]

    def __str__(self):
        return f"<Page: title={self.title}"

    def __repr__(self):
        return self.__str__()

    def collect_references(self):
        self.references = re.findall("\[\[(\S+)\|", self.text)


def main(xml_file):
    root_tree = ElementTree.parse(xml_file)
    pages = []
    for element in root_tree.getroot():
        # Collect only the actual pages
        if element.tag.endswith("page"):
            pages.append(element)
    obj_pages = []
    for page in pages:
        title = None
        text = None
        letter = None
        for field in page:
            if field.tag.endswith("title"):
                title = field.text
                letter = title[-1]
                if letter.isalpha():
                    letter = translit(letter, "bg", reversed=True)
                else:
                    letter = None
            if field.tag.endswith("revision"):
                for subfield in field:
                    if subfield.tag.endswith("text"):
                        text = subfield.text
        page_obj = PageInfo(title=title, letter=letter, text=text, references=[])
        page_obj.collect_references()
        obj_pages.append(page_obj)
    print(f"Collected a total of {len(obj_pages)} unique pages")
    all_references = open(f"page-references/all-verbs-references.txt", "w+")
    for page in obj_pages:
        letter_reference = open(f"./data/page-references/{page.letter}-verbs-references.txt", "w+")
        for ref in page.references:
            all_references.write(f"{ref}\n")
            letter_reference.write(f"{ref}\n")
        letter_reference.close()
    all_references.close()


if __name__ == '__main__':
    main(sys.argv[1])
