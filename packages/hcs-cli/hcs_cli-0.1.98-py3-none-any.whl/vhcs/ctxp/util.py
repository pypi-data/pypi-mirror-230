"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import subprocess
import json
import yaml
import types
import sys
import httpx
import traceback
import click
from typing import Any, Callable
import questionary


class CtxpException(Exception):
    pass


def error(reason: any, return_code: int = 1) -> tuple[CtxpException, int]:
    # Shortcut if the reason is an Exception already
    if isinstance(reason, Exception):
        return reason, return_code

    # Convert reason to string and wrap as CtxpException
    if isinstance(reason, str):
        pass
    elif isinstance(reason, dict):
        reason = json.dumps(reason, indent=4)
    else:
        reason = str(reason)
    return CtxpException(reason), return_code


def validate_error_return(reason, return_code):
    if return_code == 0:
        raise CtxpException("Invalid return code. return_code must not be 0 (success) in error situation.")
    if not isinstance(return_code, int):
        raise CtxpException("Invalid return code. return_code must be integer, but got " + type(return_code).__name__)


def print_output(data: Any, output: str = "json", fields: str = None, id_only: bool = False, file=sys.stdout):
    if type(data) is str:
        text = data
    elif isinstance(data, Exception):
        text = f"{type(data).__name__}: {data}"
    else:
        try:
            data = _convert_generator(data)
            if id_only:
                if fields:
                    raise CtxpException("--id-only and --fields should not be used together.")
                data = _convert_to_id_only(data)
            elif fields:
                data = _filter_fields(data, fields)

            if output == "json":
                text = json.dumps(data, default=vars, indent=4)
            elif output == "json-compact":
                text = json.dumps(data, default=vars)
            elif output == "yaml":
                import vhcs.ctxp as ctxp

                text = yaml.dump(ctxp.jsondot.plain(data), sort_keys=False)
            elif output == "text":
                if isinstance(data, list):
                    text = ""
                    for i in data:
                        line = i if type(i) is str else json.dumps(i)
                        text += line + "\n"
                elif isinstance(data, dict):
                    text = json.dumps(data, indent=4)
                elif isinstance(data, str):
                    text = data
                else:
                    text = json.dumps(data, indent=4)
            else:
                raise Exception(f"Unexpected output format: {output}")
        except Exception as e:
            print("Fail converting object:", e, file=sys.stderr)
            text = data
    print(text, end="", file=file)


def print_error(error):
    critical_errors = [KeyError, TypeError]
    for ex in critical_errors:
        if isinstance(error, ex):
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            break
    msg = error_details(error)
    print(msg, file=sys.stderr)


def _convert_generator(data: Any):
    if isinstance(data, types.GeneratorType):
        return list(data)
    return data


def _convert_to_id_only(data: Any):
    def _get_id(o):
        return o.get("id") if isinstance(o, dict) else o

    if isinstance(data, list):
        ret = []
        for d in data:
            ret.append(_get_id(d))
        return ret

    if isinstance(data, dict):
        return _get_id(data)

    return data


def _filter_fields(obj: Any, fields: str):
    parts = fields.split(",")

    def _filter_obj(o):
        if not isinstance(o, dict):
            return o
        for k in list(o.keys()):
            if k not in parts:
                del o[k]
        return o

    if isinstance(obj, list):
        return list(map(_filter_obj, obj))
    return _filter_obj(obj)


def panic(reason: Any = None, code: int = 1):
    if isinstance(reason, Exception):
        text = error_details(reason)
    else:
        text = str(reason)
    print(text, file=sys.stderr)
    sys.exit(code)


def launch_text_editor(file_name: str, default_editor: str = None):
    if not default_editor:
        default_editor = "vi"
    cmd = os.environ.get("EDITOR", default_editor) + " " + file_name
    subprocess.call(cmd, shell=True)


def choose(prompt: str, items: list, fn_get_text: Callable = None, selected=None):
    if len(items) == 0:
        panic(prompt + " ERROR: no item available.")

    if fn_get_text == None:
        fn_get_text = lambda t: str(t)

    if len(items) == 1:
        ret = items[0]
        print(prompt + " only one item available. Select by default: " + fn_get_text(ret))
        return ret

    choices = []
    size = len(items)
    for i in range(size):
        label = fn_get_text(items[i])
        # if label in choices:
        #    raise Exception("Problem with the provided fn_get_text: generates non-unique label. Item=" + label)
        choices.append(label)

    # hack workaround bug of the questionary lib
    selected_key = fn_get_text(selected) if selected else None
    k = questionary.select(prompt, choices, default=selected_key, show_selected=True).ask()
    if k == None:
        panic()
    for i in range(size):
        if k == choices[i]:
            return items[i]
    raise Exception("This is a bug and should not happen")


def input_array(prompt: str, default: list[str] = None):
    default_value = ",".join(default) if default else None

    input_value = click.prompt(prompt, default_value)
    if not input_value:
        return []
    parts = input_value.split(",")
    ret = []
    for p in parts:
        ret.append(p.strip())
    return ret


def error_details(e: Exception | Any):
    if isinstance(e, Exception):
        details = e.__class__.__name__ + ": " + str(e)
        cause = e.__cause__
        if cause and cause != e:
            details += " | Caused by: " + error_details(cause)

        if isinstance(e, httpx.HTTPStatusError):
            details += "\n" + e.response.text
        return details
    else:
        return str(e)


def avoid_trace_for_ctrl_c():
    import sys

    def my_except_hook(exctype, value, traceback):
        if exctype == KeyboardInterrupt:
            print("Aborted (KeyboardInterrupt).")
            sys.exit(1)
        else:
            sys.__excepthook__(exctype, value, traceback)

    sys.excepthook = my_except_hook
