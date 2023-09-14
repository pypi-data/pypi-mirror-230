# -*- coding: utf-8 -*-

import re
import orjson
from ..insomnia import validate_v4
from ..utils import DefaultTraceback, full_strip, generate_json_schema, open_file

work_space = []
# envs = []
groups_list = []
# requests = []

# tags = []s
# paths = []
servers = []

cookie_jar = []
api_spec = []


schema_export = {
    "openapi": "3.0.3",
    "info": {
        "title": "awesome api - OpenAPI 3.0",
        "description": "my awesome api",
        "termsOfService": "http://awesome.io/terms",
        "contact": {"email": "apiteam@awesome.io"},
        "license": {"name": "MIT", "url": "https://opensource.org/license/mit/"},
        "x-logo": {"url": "https://redocly.github.io/redoc/petstore-logo.png"},
        "version": "1.0.0",
    },
    "externalDocs": {"description": "Find out more about OpenApi", "url": "https://www.openapis.org"},
    "paths": [],
    "servers": [],
    "tags": [],
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "example: `Authorization: Bearer AWESOME_TOKEN_HERE`",
                "bearerFormat": "string",
            },
        },
        "schemas": {},
    },
}

default_responses = {
    "200": {"description": "successful"},
    "201": {"description": "created"},
    "400": {"description": "bad request"},
    "401": {"description": "authorization failed"},
    "403": {"description": "Forbidden"},
    "422": {"description": "validation failed"},
    "500": {"description": "unknown server error"},
}


def create_envs(envs_list=None):
    """create_envs(create_servers), procesa los entornos (envs)"""
    print("create_envs procesando entornos...")
    servers_list = []

    try:
        for item in envs_list:
            variables = {}
            print("nombre:", item["name"])
            data = item["data"]
            obj = {
                "description": item["name"],
            }

            if data is not None:
                for key in data:
                    # print("item data key:", key)
                    variables[key] = {"default": str(data[key])}

            url = list(variables.keys())
            if len(url) > 0:
                first = url[0]
                obj["url"] = data[first]
                obj["variables"] = variables
                servers_list.append(obj)

        # print()
        # print("create_envs variables:", variables)
        # print()
        # print("create_envs servers_list:", servers_list)
        return servers_list
    except Exception as e:
        print("create_envsException...", e)
        return None


def create_groups():
    pass


def create_requests():
    pass


def comp_schema_body(desc_name, method, body):
    try:
        rename_desc = full_strip(desc_name.lower())
        title = "Generated schema for Root"
        schema_json = generate_json_schema(title, body)

        if schema_json is not None:
            new_schema_name = [f"{rename_desc}_{method}"][0]

            # print("comp_schema_body new_schema_name...", new_schema_name)
            data = {new_schema_name: schema_json}
            # print("comp_schema_body data...", data)

            return (new_schema_name, data)
    except Exception as e:
        print("comp_schema_body Exception...", e)
    return None, None


def create_tags(groups_list, tags_list=None):
    # recorrer los grupos?
    print("create_tags procesando tags")
    tag_list = []

    for item in groups_list:
        # print("el item es:", item)
        tag_list.append(
            {
                "name": item["name"] if "name" in item else "Missing group name",
                "description": item["description"] if "description" in item else "",
            }
        )

    return tag_list


def create_paths(requests_list, groups_list=None):
    """procesa la lista de requests y groups"""
    try:
        print("procesando requests...")
        print()
        request_paths = {}

        for key, item in enumerate(requests_list):
            parent_id = item["parentId"] if "parentId" in item else None
            desc_name = item["name"]
            dirty_url = item["url"]

            desc = item["description"] if "description" in item else None

            new_url = re.sub(r"\{\{.*?\}\}", "", dirty_url)
            method = item["method"].lower()

            _endpoint = [new_url][0].strip()
            _method = [method][0]
            _group = None

            # print("======================================================================")
            # print(f"procesando: {_method.upper()}->'{_endpoint[:40]}...'")

            if _endpoint is None or _endpoint == "" or _endpoint.startswith(("http", "https")):
                print(f"skipping (invalid endpoint): {_method.upper()} -> '{_endpoint[:25]}...' (desc: '{desc_name}')")
                continue

            if parent_id is not None:
                _group = next((d.get("name") for d in groups_list if d.get("id") == parent_id), "default")

            obj_request = {
                _endpoint: {
                    _method: {
                        "description": desc if desc is not None else "description not available",
                        "summary": desc_name,
                        "tags": [_group],
                        "operationId": f"op_{_method}_{key}",
                        "parameters": [
                            {
                                "name": "Accept-Encoding",
                                "schema": {"type": "string", "example": "gzip, deflate", "format": "string"},
                                "in": "header",
                            }
                        ],
                        "security": [{"bearerAuth": []}],  # TO FIX
                        "responses": default_responses,
                    }
                }
            }

            if _method in {"post", "put", "patch"}:
                body = item["body"] if "body" in item else None

                if body is not None and bool(body) is True:
                    mime_type = body["mimeType"] if "mimeType" in body else None
                    request_body = {}

                    match mime_type:
                        case "application/json":
                            example = body["text"] if "text" in body else None

                            if not example:
                                print(f"skipping (missing request body): {_method.upper()} -> '{desc_name}'")
                                continue

                            try:
                                example = orjson.loads(example)
                            except Exception:
                                print(f"invalid json at: {_method.upper()}->'{desc_name}'")
                                example = str(example)

                            # se crea un json_schema del request body
                            schema_name = f"schema_{key} {desc_name}"
                            ref_path, result_schema = comp_schema_body(schema_name, _method, example)

                            if ref_path is not None:
                                request_body = {
                                    "requestBody": {
                                        "required": True,
                                        "content": {
                                            mime_type: {
                                                "schema": {"$ref": f"#/components/schemas/{ref_path}"}
                                                # "schema": {
                                                #     "type": "object",
                                                #     "example": example,
                                                # }
                                            }
                                        },
                                    },
                                }

                                # se agrega el json_schema del body al components/schemas
                                schema_export["components"]["schemas"].update(result_schema)
                            else:
                                request_body = {
                                    "requestBody": {
                                        "required": True,
                                        "content": {mime_type: {}},
                                    },
                                }

                        case "multipart/form-data":
                            params = body["params"] if "params" in body else None

                            if not params:
                                print(f"skipping (missing multipart/form-data): {_method.upper()} -> '{desc_name}'")
                                continue

                            obj_form = {}

                            for item in params:
                                disabled = False
                                obj = {}

                                if "disabled" in item:
                                    disabled = item["disabled"]

                                if disabled is False:
                                    if "type" in item:
                                        if item["type"] == "file":
                                            obj: dict[str, str] = {"type": "string", "format": "binary"}
                                            obj_form["file"] = obj
                                        else:
                                            obj: dict[str, str] = {"type": "string", "format": "text"}
                                            name = item["name"]
                                            obj_form[name] = obj
                                    else:
                                        name = [item["name"]][0]
                                        obj = {"type": "string", "format": "uuid"}
                                        obj_form[name] = obj

                            request_body = {
                                "requestBody": {
                                    "required": True,
                                    "content": {
                                        mime_type: {
                                            "schema": {
                                                "type": "object",
                                                "properties": obj_form,
                                            }
                                        }
                                    },
                                },
                            }
                        case _:
                            print(f"skipping (unknown mime_type): {_method.upper()} -> '{desc_name}'")
                            continue

                    # esto agrega el request body como ejemplo
                    # de la solicitud
                    obj_request[_endpoint][_method].update(request_body)
                else:
                    print(f"skipping (missing body): {_method.upper()} -> '{desc_name}'")
                    continue

            request_paths.update(obj_request)
            obj_request = {}

        print()
        return request_paths
    except Exception as e:
        print("create_paths Exception...", e)
        DefaultTraceback(e)
        return None


def create_schema(json_data):
    if "servers" in json_data:
        schema_export["servers"] = json_data["servers"]

    if "paths" in json_data:
        schema_export["paths"] = json_data["paths"]

    if "tags" in json_data:
        schema_export["tags"] = json_data["tags"]

    return schema_export


# TO FIX
def generate_v30x(file_name):
    """lee un archivo de insomnia v4"""

    json_data = open_file(file_name)
    # resources = None

    if json_data is None:
        print("generate_v30x: no se pudo leer el json_data")
        return None

    resources = validate_v4(json_data)
    print("listo para procesar...")
    # print(resources)
    # print("======================")

    envs_result = create_envs(resources["envs"])
    # print("create_envs:", envs_result)
    tags_result = create_tags(resources["groups"])
    groups_list = resources["groups"]
    # print("=============groups=============")
    # print(groups)
    # print("=============groups=============")
    paths_result = create_paths(resources["requests"], groups_list)

    create_schema({"servers": envs_result, "tags": tags_result, "paths": paths_result})
    print("listo!...")

    # print()
    # print("el json listo de oas303...")
    # print("=================================")
    # print(schema_export)
    return schema_export
