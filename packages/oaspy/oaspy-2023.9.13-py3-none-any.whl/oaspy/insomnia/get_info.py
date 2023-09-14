# -*- coding: utf-8 -*-

import jmespath
from jmespath import exceptions as jmEexceptions
from ..utils import validate_json_schema

schema_insomnia_V4 = {
    "$id": "https://example.com/tree",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "description": "insomnia V4 schema",
    "type": "object",
    "required": ["_type", "__export_format", "__export_date", "__export_source", "resources"],
    "properties": {
        "_type": {"type": "string", "minLength": 3},
        "__export_format": {"type": "integer", "minimum": 0, "enum": [4]},
        "__export_date": {"type": "string", "minLength": 3},
        "__export_source": {"type": "string", "minLength": 3},
        "resources": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "_id": {"type": "string", "minLength": 3},
                    "name": {"type": "string", "minLength": 3},
                },
                "additionalProperties": True,
                "required": ["_id"],
            },
        },
    },
    "additionalProperties": False,
}


def get_info(body):
    result = validate_json_schema(schema_insomnia_V4, body)

    if result is None:
        return None

    try:
        _export_format = jmespath.search("__export_format", body)
        _export_date = jmespath.search("__export_date", body)
        _export_source = jmespath.search("__export_source", body)
        _workspace = jmespath.search("resources[?_type=='workspace']|[0]", body)
        _api_spec = jmespath.search("resources[?_type=='api_spec']|[0]", body)
        _cookie_jar = jmespath.search("resources[?_type=='cookie_jar']|[0]", body)
        _environment = jmespath.search("resources[?_type=='environment']", body)
        _request_group = jmespath.search("resources[?_type=='request_group']", body)

        _request = jmespath.search("length(resources[?_type=='request'])", body)

        _request_get = jmespath.search("length(resources[?_type=='request' && method=='GET'])", body)
        _request_post = jmespath.search("length(resources[?_type=='request' && method=='POST'])", body)
        _request_put = jmespath.search("length(resources[?_type=='request' && method=='PUT'])", body)
        _request_delete = jmespath.search("length(resources[?_type=='request' && method=='DELETE'])", body)
        _request_patch = jmespath.search("length(resources[?_type=='request' && method=='PATCH'])", body)

        _request_json = jmespath.search(
            "length(resources[?_type=='request' && headers && headers[?value == 'application/json']])", body
        )
        _request_form_data = jmespath.search(
            "length(resources[?_type=='request' && headers && headers[?value == 'multipart/form-data']])", body
        )
        _request_unknow = jmespath.search("length(resources[?_type=='request' && !headers])", body)

        print("===Insomnia format===")
        print(_export_format)

        print("===Insomnia export===")
        print("export date:", _export_date)

        print("===Insomnia source===")
        print("source:", _export_source)

        print("===Insomnia workspace===")
        print("workspace name:", _workspace.get("name", None))
        print("description:")
        print(f"""{_workspace.get("description", None)}""")

        print("===Insomnia api_spec===")
        print("api_spec name:", _api_spec.get("fileName", None))

        print("===Insomnia cookie_jar===")
        print("cookie_jar name:", _cookie_jar.get("name", None))
        print("cookie_jar cookies:", _cookie_jar.get("cookies", None))

        print("===Insomnia environments===")
        print(len(_environment))

        for item in _environment:
            print("- name:", item.get("name", None))

        print("===Insomnia request groups===")
        print(len(_request_group))

        for item in _request_group:
            print("- group name:", item.get("name", None))

        print("===request Methods===")
        print(_request)
        print("- GET:", _request_get)
        print("- POST:", _request_post)
        print("- PUT:", _request_put)
        print("- DELETE:", _request_delete)
        print("- PATCH:", _request_patch)

        print("===request using application/json===")
        print(_request_json)

        print("===request using multipart/form-data===")
        print(_request_form_data)

        print("===request headers unknow===")
        print(_request_unknow)

    except jmEexceptions.JMESPathError as jme:
        print("get_info JMESPathError Exception:", jme)
    except Exception as e:
        print("get_info Exception:", e)

    return None
