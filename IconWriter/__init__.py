import io

import azure.functions as func
from icon_writer import write_icon

def get_param(req, param_name, default_value=None):
    param_value = req.params.get(param_name)
    if not param_value:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            param_value = req_body.get(param_name)
    return param_value if param_value is not None else default_value

def main(req: func.HttpRequest) -> func.HttpResponse:
    text = get_param(req, 'text')
    size = int(get_param(req, 'size', 80))
    bgcolor = get_param(req, 'bgcolor', 'black')
    fontcolor = get_param(req, 'fontcolor', 'white')
    if text:
        img = write_icon(text, size=size, bgcolor=bgcolor, fontcolor=fontcolor)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return func.HttpResponse(img_byte_arr, mimetype='image/png')
    else:
        return func.HttpResponse(
             "Text must be specified",
             status_code=400
        )
