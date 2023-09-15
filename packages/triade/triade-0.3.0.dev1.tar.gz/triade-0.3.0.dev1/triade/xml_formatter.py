from triade.element import Element, NotAnElementError


class XML:
    @staticmethod
    def loads(input_data: str) -> dict:
        "Parse XML string into Python object"

        element = Element.from_xml_string(input_data)

        if not Element.is_element(element):
            error_msg = "The given string can't be converted to XML"
            raise NotAnElementError(error_msg)

        return element

    @staticmethod
    def dumps(input_data: dict) -> str:
        "Converts Python object into XML string"

        if not Element.is_element(input_data):
            raise NotAnElementError("The given object is not a valid element")

        return str(Element(input_data))
