# -*- coding: utf-8 -*-

from .openapi import generate_v30x
from .utils import check_file, save_file


def convert(file_name, from_schema=None, output_file=None):
    if file_name is None:
        print("oaspy: unknow file_name...")
        print("exiting...")
        print()

    if from_schema == "v30":
        result_oa3 = generate_v30x(file_name)

        if result_oa3 is not None:
            print("generando archivo de OpenApi 3.0.x...")
            output_file_name = output_file or "export_openapi_v303.json"
            save_file(output_file_name, result_oa3)
    elif from_schema == "v31":
        print("oaspy: this schema has not been implemented yet...")
        print("exiting...")
        print()
    else:
        print(f"oaspy: unknow schema '{from_schema}' use any of the following arguments:")
        print("> oaspy gen -f Insomnia_file_v4.json -s v30")
        print("for OpenApi Specification v3.0.x")
        print()
        print("> oaspy gen -f Insomnia_file_v4.json -s v31")
        print("for OpenApi Specification v3.1.x")
        print("exiting...")
        print()
