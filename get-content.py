#!/usr/bin/env python3

import json
from bs4 import BeautifulSoup, SoupStrainer
from domonic.html import body, div, h1, h2, h3, h4, br, p, html, head, link, script


class God:

    images_link = 'https://arobogo-cdn.s3.eu-central-1.amazonaws.com/img/'

    def __init__(self, original_htm: str, texteditor_html: str) -> None:
        self.orig_htm = original_htm
        self.editor_html = texteditor_html
        self.added_topics = []
        self.images = []
        self.opening = div(_id='Opening')
        self.topics = div( h1('Tartalom'), _id='Topics')
        self.sections = div(_id='Sections')

    def get_images(self):
        with open(self.orig_htm, 'r', encoding='latin-1') as f:
            for link in BeautifulSoup(f, parse_only=SoupStrainer('a'), features="lxml"):
                if link.has_attr('href'):
                    link_value = link['href']
                    if 'Images' in link_value:
                        self.images.append(link_value.replace('Images\\', self.images_link))

    def next_image(self) -> str:
        if len(self.images) == 0:
            return None
        next_image = self.images[0]
        self.images = self.images[1:]
        return next_image

    def get_opening(self):
        with open(self.editor_html, 'r', encoding='utf-8') as f:
            for paragraph in BeautifulSoup(f, parse_only=SoupStrainer('p'), features="lxml"):
                elem = self.get_elem(paragraph)
                if not elem:
                    continue
                if elem['content']:
                    if elem['content'][0] == 'Tartalom':
                        break
                if elem['elem_type'] == 'h1':
                    self.opening.appendChild(h1(elem['content'][0]))
                if elem['elem_type'] == 'h2':
                    self.opening.appendChild(h2(elem['content'][0]))
                if elem['elem_type'] == 'h3':
                    for paragraph in elem['content']:
                        if paragraph == 'IMAGE':
                            self.opening.appendChild(div('KÉP', **{"_data-link":self.next_image()}))
                        else:
                            self.opening.appendChild(h3(paragraph))
                if elem['elem_type'] == 'h4':
                    self.opening.appendChild(h4(elem['content'][0]))
                if elem['elem_type'] == 'p':
                    for paragraph in elem['content']:
                        self.opening.appendChild(p(paragraph))
                if elem['elem_type'] == 'br':
                    self.opening.appendChild(br())

    def get_topics(self):
        with open(self.editor_html, 'r', encoding='utf-8') as f:
            parse_from = False
            for paragraph in BeautifulSoup(f, parse_only=SoupStrainer('p'), features="lxml"):
                elem = self.get_elem(paragraph)
                if not elem:
                    continue

                if elem['content'] and elem['content'][0] == 'Tartalom':
                    parse_from = True
                    continue

                if parse_from:
                    if elem['elem_type'] == 'h3':
                        content = elem['content'][0]
                        if content in self.added_topics:
                            break
                        self.added_topics.append(content)
                        self.topics.appendChild(h3(content, **{"_data-section":len(self.added_topics)}))

    def get_sections(self):
        with open(self.editor_html, 'r', encoding='utf-8') as f:
            current_section = False
            parse_from = False
            first_occupance = True
            section_index = 1
            for paragraph in BeautifulSoup(f, parse_only=SoupStrainer('p'), features="lxml"):
                elem = self.get_elem(paragraph)
                if not elem:
                    continue

                if elem['content'] and (elem['content'][0] == 'Kezdetnek szófacsarás'):
                    if first_occupance:
                        first_occupance = False
                        continue
                    else:
                        parse_from = True

                if parse_from:
                    if len(elem['content']) == 1 and elem['content'][0] in self.added_topics:
                        if current_section:
                            self.sections.appendChild(current_section)
                            section_index += 1
                        current_section = div(h4(elem['content'][0]), _class='Section', **{"_data-section":section_index})
                    else:
                        for paragraph in elem['content']:
                            if paragraph == 'IMAGE':
                                current_section.appendChild(div('KÉP', **{"_data-link":self.next_image()}))
                            else:
                                current_section.appendChild(p(paragraph))



            self.sections.appendChild(current_section)

    def get_elem(self, paragraph) -> dict:
        try:
            p_class = paragraph.get('class')[0]
        except:
            return None

        type_map = {
            'p1': 'h1',
            'p2': 'h2',
            'p3': 'br',
            'p4': 'p',
            'p5': 'h3',
            'p6': 'br',
            'p7': 'h4',
            'p8': 'h3',
            'p9': 'br',
            'p10': 'br',
            'p11': 'h3',
            'p12': 'P12',
        }

        elem_type = type_map[paragraph.get('class')[0]]

        contents = self.parse_contents(elem_type, paragraph.contents)

        if not contents or contents == []:
            return None

        return {
            'elem_type': elem_type,
            'content': contents,
        }

    def parse_contents(self, elem_type: str, contents: list) -> list:
        if elem_type == 'br':
            return None
        out = []
        for elem in contents:
            elem_str = f'{elem}'
            if 'span class=' in elem_str:
                continue
            elem_str = self.clear_str(elem_str)
            parsed_elems = self.separate_images(elem_str)
            out.extend(parsed_elems)
        return out

    def clear_str(self, in_str: str) -> str:
        out = self.remove_tag('i', in_str)
        return self.remove_tag('b', out)

    def remove_tag(self, tag: str, orig: str) -> str:
        out_str = orig.strip()
        if out_str.startswith(f'<{tag}>'):
            out_str = out_str[3:]
        if out_str.endswith(f'</{tag}>'):
            out_str = out_str[:-(3+len(tag))]
        return out_str

    def separate_images(self, elem_str:str) -> list:
        elems = []
        while True:
            index = elem_str.find('KÉP')
            if index == -1:
                elems.append(elem_str.strip())
                break
            if index == 0:
                elems.append('IMAGE')
            else:
                elems.append(elem_str[:index].strip())
                elems.append('IMAGE')
            elem_str = elem_str[index + 3:].strip()
            if elem_str == "":
                break
        return elems

    def render(self):
        h = html(head(
            link(_href='style.css', _rel='stylesheet'),
            link(_href="data:image/x-icon;base64,AAABAAEAEBAAAAEACABoBQAAFgAAACgAAAAQAAAAIAAAAAEACAAAAAAAAAEAAAAAAAAAAAAAAAEAAAAAAAAAAAAACE6AAEaZ1AAHGEcADj+hAOCxfgBrPQwABjZwAAADCgAWTOAAP3/MAMSQWAALIVwAL2T3AJGcngBUXV4AEkrjAB8RAwAJInMAGEK4AABBkQBSfvcAUH3mABc0hQAoTbAABBA4AAsxmQCcYyUAien6AB9OzwCS8vcABRxpAAQVTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABERAAAAAAAAAAgRAAAAABEODwAAAAAAAAgODwgAACAgICAgICAgICAICAgICAggExMQEBATExMTEwMDAwMZEhAQEBAMERERFxATGhoaHAQWEBAMAAAADBcNCRMTGiAUBBYQDAAADAwYFQ0JExIAHx8WEBEAAAwHBwcHBwcAAB4SFgAdHQAAAgIKCgEBAAAACxsGAAAAAAAAAAAAAAAAAAALGwYAAAAAAAAAAAAAAAAAAAsbAAAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//AAD//wAAz+cAAIfDAAAAAAAAAAAAAAAAAAAHAAAABgEAAAYDAAADAwAAgf8AAMf/AADn/wAA9/8AAP//AAA=", _rel="icon", _type="image/x-icon"),
        ))
        b = body()
        b.appendChild(self.opening)
        b.appendChild(self.topics)
        b.appendChild(self.sections)
        b.appendChild(script(_src='index.js'))
        h.appendChild(b)

        print(h)

def main():
    g = God('orig.htm', 'texteditor.html')
    g.get_images()
    g.get_opening()
    g.get_topics()
    g.get_sections()
    g.render()

main()
