from django.template import loader
from fastapi.responses import HTMLResponse


def render(
    request,
    template_name,
    context=None,
    content_type=None,
    status=None,
    using=None,
    headers=None,
):
    """
    Return an HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    content = loader.render_to_string(
        template_name, context, request, using=using)
    return HTMLResponse(
        content, media_type=content_type, status_code=status or 200, headers=headers
    )
