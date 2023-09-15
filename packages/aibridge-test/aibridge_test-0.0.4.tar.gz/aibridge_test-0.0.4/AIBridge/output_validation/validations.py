from abc import ABC, abstractmethod
import json
from AIBridge.exceptions import AIBridgeException, ValidationException
import csv
import io
import xml.etree.ElementTree as ET
import re
import sqlparse
from json import JSONDecodeError
import jsonschema


class Validation(ABC):
    @abstractmethod
    def validate(self, output_string, schema):
        pass


class JsonSchema(Validation):
    def validate(self, output_string, schema=None):
        try:
            if type(output_string) == dict:
                json_data = json.loads(output_string)
            else:
                if "}" not in output_string:
                    output_string += '"}'
                    output_string = output_string + "}"
                json_string = output_string[
                    output_string.index("{") : len(output_string)
                    - output_string[::-1].index("}")
                ]
                json_string = json_string.replace("\n", "")
                json_data = json.loads(json_string)
        except AIBridgeException as e:
            raise JSONDecodeError(f" Error in the AI output for the validation->{e}")
        if schema:
            try:
                user_schema = json.loads(schema)
            except AIBridgeException as e:
                raise JSONDecodeError(f"Error in the schema you entred {e}")
            try:
                jsonschema.Draft7Validator.check_schema(user_schema)
                jsonschema.Draft7Validator.check_schema(json_data)
            except jsonschema.exceptions.SchemaError as e:
                raise ValidationException(f"Invalid output JSON schema: {e}")
        return json.dumps(json_data)


class CSVSchema(Validation):
    def validate(self, output_string, schema=None):
        try:
            if schema:
                if schema in output_string:
                    str_split = output_string.split(schema + "\n")
                    if len(str_split) == 2:
                        output_string = schema + "\n" + str_split[1]
                else:
                    csv_data = output_string.strip().split("\n")
                    expected_columns = expected_columns = [
                        column.strip().lower() for column in schema.split(",")
                    ]
                    if not expected_columns:
                        expected_columns = expected_columns = [
                            column.strip().lower() for column in schema.split("")
                        ]
                    if csv_data:
                        result = False
                        for column in csv_data:
                            columns = [col.strip().lower() for col in column.split(",")]
                            if len(columns) == len(expected_columns):
                                str_split = output_string.split(column + "\n")
                            if len(str_split) == 2:
                                output_string = (
                                    schema + "\n" + column + "\n" + str_split[1]
                                )
                                result = True
                            else:
                                output_string = schema + "\n" + output_string
                                result = True
                            if result:
                                break
                        if not result:
                            raise ValidationException(
                                f"Csv schema genrated by AI is not a valid schema"
                            )
            return output_string
        except csv.Error as e:
            raise ValidationException(f"{e}")


class SQLSchema(Validation):
    def validate(self, output_string, schema=None):
        sql_keywords = [
            "SELECT",
            "UPDATE",
            "INSERT",
            "DELETE",
            "FROM",
            "WHERE",
            "JOIN",
        ]
        pattern = r"\b(?:{})\b".format("|".join(sql_keywords))
        if re.search(pattern, output_string, re.IGNORECASE):
            parsed = sqlparse.parse(output_string)
            if any(parsed):
                return output_string
            else:
                raise ValidationException(
                    f"Sql schema genrated by AI is not a valid schema"
                )
        else:
            raise ValidationException(
                f"Sql schema genrated by AI is not a valid schema"
            )


class XMLSchema(Validation):
    def validate(self, output_string, schema=None):
        if """<?xml version="1.0" encoding="UTF-8" ?>""" in output_string:
            output_string = output_string.replace(
                """<?xml version="1.0" encoding="UTF-8" ?>""", ""
            )
        try:
            output_schema = ET.fromstring(output_string)
        except AIBridgeException as e:
            raise ValidationException(
                f"Xml schema genrated by AI is not a valid schema->{e}"
            )
        if schema:
            input_schema = ET.fromstring(schema)

            def validate_xml(output_schema, input_schema):
                if output_schema.tag != input_schema.tag:
                    return False
                if output_schema.attrib != input_schema.attrib:
                    return False
                for child1, child2 in zip(output_schema, input_schema):
                    if not validate_xml(child1, child2):
                        return False

                return True

            result = validate_xml(output_schema, input_schema)
            if not result:
                raise ValidationException(
                    f"Xml schema genrated by AI is not a valid schema"
                )
        return output_string
