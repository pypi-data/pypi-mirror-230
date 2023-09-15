import re

from typing import List, Dict, Type

from bs4 import BeautifulSoup


class NotAnElementError(ValueError):
    pass


class Element(dict):
    tag: str
    attributes: Dict[str, str]
    children: List["Element"]
    text: str
    _re = re.compile("^( +)")

    def __init__(
        self,
        element=None,
        /,
        attributes=None,
        children=None,
        text=None,
        *,
        tag=None,
        level=0,
        indent_level=4,
    ):
        self._level = level
        self._indent = indent_level

        if isinstance(element, dict):
            if tag or attributes or children or text:
                raise ValueError(
                    "Combining dictionary and named arguments is not allowed"
                )
            if "tag" not in element.keys():
                raise ValueError("The tag name was not provided")

            for key, value in element.items():
                if key not in ["tag", "attributes", "children", "text"]:
                    raise ValueError(f"Unrecognized dictionary key: {key}")

                if key == "children":
                    self["children"] = [
                        Element(child, level=(level + 1)) for child in value
                    ]
                else:
                    self[key] = value

            return

        elif isinstance(element, str) and tag is None:
            tag = element

        self["tag"] = tag
        if attributes:
            self["attributes"] = attributes
        if children:
            self["children"] = [
                Element(child, level=(level + 1)) for child in children
            ]
        if text:
            self["text"] = text

        if children and text:
            raise ValueError("Element cannot have children and text at the same time")

        if not self.is_element(self):
            raise NotAnElementError("The given object is not a valid element")

    @property
    def tag(self):
        "The element's tag"
        return self.get("tag")

    @property
    def attributes(self):
        "A dictionary of attributes"
        return self.get("attributes")

    @property
    def children(self):
        "A list of child elements"
        return self.get("children")

    @property
    def text(self):
        "The element's text"
        return self.get("text")

    @property
    def level(self):
        return self._level

    @tag.setter
    def tag(self, value):
        self["tag"] = value

    @attributes.setter
    def attributes(self, value):
        self["attributes"] = value

    @children.setter
    def children(self, value):
        self["children"] = value

    @text.setter
    def text(self, value):
        self["text"] = value

    @attributes.deleter
    def attributes(self):
        del self["attributes"]

    @children.deleter
    def children(self):
        del self["children"]

    @text.deleter
    def text(self):
        del self["text"]

    @classmethod
    def is_element(cls: Type["Element"], obj: dict) -> bool:
        tag = obj.get("tag")
        attributes = obj.get("attributes")
        children = obj.get("children")
        text = obj.get("text")

        if not isinstance(tag, str):
            return False

        if attributes is not None and not isinstance(attributes, dict):
            return False
        elif isinstance(attributes, dict):
            for value in attributes.values():
                if not isinstance(value, str):
                    return False

        if children is not None and text is not None:
            return False

        if children is not None:
            if not isinstance(children, list):
                return False
            for child in children:
                if not cls.is_element(child):
                    return False

        if text is not None and not isinstance(text, str):
            return False

        for key in obj.keys():
            if key not in ["tag", "attributes", "children", "text"]:
                return False

        return True

    def _get_children_str(self, parent: Type["Element"]) -> str:
        return [str(child) for child in parent.children]

    def _get_attr_str(self):
        if not self.attributes:
            return ""
        return " ".join([f'{key}="{value}"' for key, value in self.attributes.items()])

    def _clean(self, value: str) -> str:
        return value.replace("u'", "'").replace("'<", "<").replace(">'", ">")

    def __repr__(self):
        tag = self.tag
        attributes = self.attributes
        children = self.children
        text = self.text

        args = [f'tag="{tag}"']

        if attributes:
            attr = str(attributes).replace("'", '"')
            args.append(f"attributes={attr}")
        args.append(f"children={children}") if children else None
        args.append(f'text="{text}"') if text else None

        arg_list = ", ".join(args)

        return f"Element({arg_list})"

    def _to_xml(self):
        is_self_closed = not self.children and not self.text

        if self.children:
            content = [child._to_xml() for child in self.children]
            content = (
                str(content)
                .replace("'", "")
                .replace("[", "")
                .replace("]", "")
                .replace(", ", "")
            )
        elif self.text:
            content = self.text
        else:
            content = ""

        if self.attributes:
            open_tag_content = " ".join([self.tag, self._get_attr_str()])
        else:
            open_tag_content = self.tag

        if is_self_closed:
            open_tag = f"<{open_tag_content} />"
            close_tag = ""
        else:
            open_tag = f"<{open_tag_content}>"
            close_tag = f"</{self.tag}>"

        return f"{open_tag}{content}{close_tag}"

    # TODO: create Element instance from xml string
    @classmethod
    def from_xml_string(cls, xml_string):
        "Create new element from an XML formatted string"

        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>'

        value = xml_string.replace(xml_declaration, "")

        index = value.find(">")

        value = value[1:index].replace("/", "").strip()

        return cls(value)

    def _get_tag(self, value: str) -> str:
        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>'

        value = value.replace(xml_declaration, "")

        index = value.find(">")

        return ""


    def indent(self, value):
        "Change the number of spaces of indentation"
        self._indent = value

    def __str__(self):
        pattern = self._re
        xml = BeautifulSoup(self._to_xml(), features="xml").prettify().strip()
        lines = []
        for line in xml.split("\n"):
            lines.append(re.sub(pattern, r"\1" * self._indent, line))

        return "\n".join(lines)
