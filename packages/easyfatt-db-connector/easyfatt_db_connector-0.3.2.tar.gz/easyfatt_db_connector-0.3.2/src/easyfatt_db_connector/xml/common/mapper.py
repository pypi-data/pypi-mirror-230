# import os as _os
# import xml.dom.minidom as minidom
from typing import get_type_hints

import lxml.etree as ET

from easyfatt_db_connector.core.exceptions import TypeConversionError

from .fields import BaseField, Field, FieldGroup


class XMLMapper(object):
    """Base class for XML mappers.

    - Use the `__xml_mapping__` class attribute to map XML elements to class attributes.
    - Use the `__xml_name__` class attribute to override the name of the XML element the class refers to.
    """

    __xml_name__: str = ""
    """ Customize the name of the XML tag. 
    
    If not specified, it will be the set to the name of the class.
    """

    __xml_mapping__: dict[str, str] = None

    def __str__(self) -> str:
        attributes = [
            (f"{attr}='{value}'" if type(value) == str else f"{attr}={value}")
            for attr, value in self.__dict__.items()
        ]
        return f"{self.__class__.__name__}({', '.join(attributes)})"

    def __repr__(self) -> str:
        return self.__str__()
    
    def __hash__(self) -> int:
        """ Returns a hash of the object. """
        return hash((type(self),) + tuple(
            [tuple(value) if type(value) == list else value for value in self.__dict__.values()]
        ))

    @classmethod
    def _get_xml_tag(cls) -> str:
        return cls.__xml_name__ if getattr(cls, "__xml_name__", None) else cls.__name__

    @classmethod
    def from_xml_string(cls, string: str, convert_types=True, normalize_none=False, *, _warn_untracked=True):
        """ Creates an instance of the class from an XML text.

        Args:
            string (str): The XML text to parse.
            convert_types (bool, optional): Whether to convert the types of the fields. Defaults to True.
            normalize_none (bool, optional): Whether to convert `None` values to empty strings or the default in case `convert_types=True`. Defaults to False.
            _warn_untracked (bool, optional): Whether to warn if there are untracked children (for internal use only). Defaults to True.
        
        Raises:
            NotImplementedError: If the class does not have an `__xml_mapping__` attribute or if is not a dictionary.
            TypeError: If the value of the `__xml_mapping__` attribute is not valid.
            TypeConversionError: If the type of the field is not supported.
            
        Returns:
            XMLMapper: An instance of the class.
        """
        return cls.from_xml(
            ET.fromstring(string),
            convert_types=convert_types,
            normalize_none=normalize_none,
            _warn_untracked=_warn_untracked,
        )

    @classmethod
    def from_xml(cls, element: ET._Element, convert_types=True, normalize_none=False, *, _warn_untracked=True):
        """ Creates an instance of the class from an XML text.
        
        Args:
            element (ET._Element): The XML element to parse.
            convert_types (bool, optional): Whether to convert the types of the fields. Defaults to True.
            normalize_none (bool, optional): Whether to convert `None` values to empty strings or the default in case `convert_types=True`. Defaults to False.
            _warn_untracked (bool, optional): Whether to warn if there are untracked children (for internal use only). Defaults to True.
            
        Raises:
            NotImplementedError: If the class does not have an `__xml_mapping__` attribute or if is not a dictionary.
            TypeError: If the value of the `__xml_mapping__` attribute is not valid.
            TypeConversionError: If the type of the field is not supported.
            
        Returns:
            XMLMapper: An instance of the class.
        """
        if getattr(cls, "__xml_mapping__", None) is None and type(cls.__xml_mapping__) != dict:
            raise NotImplementedError(
                "This class does not have an __xml_mapping__ attribute defined."
            )
        
        # Check if there are tags that are not tracked in the `__xml_mapping__` attribute
        # I did not use a list comprehension since it would have been too long and unreadable
        child_tags = []
        for child in cls.__xml_mapping__.values():
            if type(child) == str:
                child_tags.append(child)
            elif isinstance(child, FieldGroup):
                child_tags.extend(list(child.target.__xml_mapping__.values()))
            elif isinstance(child, Field):
                if getattr(child, "is_parent"):
                    child_tags.append(child.tag)
                elif getattr(child, "tag", None):
                    child_tags.append(child.tag)
                else:
                    child_tags.append(child.target._get_xml_tag())

        untracked_children = [
            child.tag for child in element.iterchildren() if child.tag not in child_tags
        ]

        if untracked_children and _warn_untracked:
            print(
                f"\nWARNING: A total of {len(untracked_children)} children are not tracked ({', '.join(untracked_children)}) in the `{cls.__name__}.__xml_mapping__` class attribute.\n"
            )

        xml_object = cls()
        for attr, target in cls.__xml_mapping__.items():
            # Fail if the attribute is of the wrong type
            if type(target) != str and not isinstance(target, BaseField):
                raise TypeError(f"target must be a string or Field, not {type(target)}")

            if isinstance(target, FieldGroup):
                setattr(
                    xml_object,
                    attr,
                    target.target.from_xml(element, convert_types=convert_types, normalize_none=normalize_none, _warn_untracked=False),
                )

            elif isinstance(target, Field):
                child_class_name = ""
                if getattr(target, "tag", None):
                    child_class_name = target.tag
                elif getattr(target, "target", None):
                    child_class_name = target.target._get_xml_tag()

                if getattr(target, "is_parent"):
                    children = element.xpath(
                        f"{child_class_name}/{target.child.target._get_xml_tag()}"
                    )

                    children_obj = [
                        target.child.target.from_xml(child_xml, convert_types=convert_types, normalize_none=normalize_none, _warn_untracked=_warn_untracked)
                        for child_xml in children
                    ]

                    setattr(xml_object, attr, children_obj)
                else:
                    child_element = element.find(child_class_name)

                    if child_element is not None:
                        setattr(
                            xml_object,
                            attr,
                            target.target.from_xml(child_element, convert_types=convert_types, normalize_none=normalize_none, _warn_untracked=_warn_untracked),
                        )
            else:
                element_text = ""

                # ---> XML Attribute
                if target.strip().startswith("@"):
                    element_text = element.get(target[1:])

                elif target.strip().upper() == "#TEXT":
                    element_text = element.text

                # ---> XML Child Element
                else:
                    child_element = element.find(target)

                    if child_element is None:
                        continue

                    element_text = child_element.text


                if element_text is None and normalize_none:
                    element_text = ""

                if not convert_types:
                    setattr(xml_object, attr, element_text)
                    continue

                # =======> Type conversion <=======
                expected_type = get_type_hints(cls)[attr]

                try:
                    converted_value = None
                    if expected_type == bool or "[bool]" in str(expected_type):
                        if element_text is None:
                            element_text = ""
                        converted_value = element_text.lower() == "true"

                    elif expected_type == int or "[int]" in str(expected_type):
                        if element_text is None or element_text == "":
                            element_text = 0
                        converted_value = int(float(element_text))

                    elif expected_type == float or "[float]" in str(expected_type):
                        if element_text is None or element_text == "":
                            element_text = 0
                        converted_value = float(element_text)

                    elif expected_type == str or "[str]" in str(expected_type):
                        if element_text is None:
                            element_text = ""
                        converted_value = str(element_text)

                    else:
                        converted_value = element_text

                except ValueError:
                    raise TypeConversionError(
                        f"Error while converting `{cls.__name__}.{attr}`: `{element_text}` cannot be converted to `{expected_type.__name__}`."
                    )
                else:
                    setattr(xml_object, attr, converted_value)

        return xml_object