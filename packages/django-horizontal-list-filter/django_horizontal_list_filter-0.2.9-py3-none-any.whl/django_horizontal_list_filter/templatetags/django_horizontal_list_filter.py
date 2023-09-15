import re
import urllib
from django.template import Library
from django.template.loader import get_template
from django_simple_tags.utils import get_related_model_field

try:
    from django_middleware_global_request.middleware import get_request
except ImportError:
    def get_request():
        return None


register = Library()


@register.simple_tag
def django_horizontal_list_filter(cl, spec):
    request = get_request()
    tpl = get_template(spec.template)
    return tpl.render({
        "cl": cl,
        "title": spec.title,
        "choices": list(spec.choices(cl)),
        "spec": spec,
        "reqeust": request,
    })


@register.simple_tag
def django_horizontal_list_filter_search_box_label(cl):
    model = cl.model
    model_admin = cl.model_admin
    search_fields = model_admin.search_fields
    search_labels = []
    for search_field in search_fields:
        related_model, field = get_related_model_field(model, search_field)
        label = str(field.verbose_name)
        search_labels.append(label)
    return "/".join(search_labels)


@register.simple_tag
def django_horizontal_list_filter_turn_mptt_padding_style_to_padding_string(cl, spec, choice):
    padding_style = choice.get("padding_style", None)
    if not padding_style:
        return ""
    padding = int(re.findall("\d+", padding_style)[0])
    model_admin = cl.model_admin
    mptt_level_indent = getattr(model_admin, "mptt_level_indent", spec.mptt_level_indent)
    if not mptt_level_indent:
        return ""
    return "----" * (padding // mptt_level_indent)

@register.simple_tag
def django_horizontal_list_filter_clean_query_string(cl, spec, query_string):
    if not query_string:
        return ""
    if query_string.startswith("?"):
        query_string = query_string[1:]
    qsl = urllib.parse.parse_qsl(query_string)
    expected_parameters = spec.expected_parameters()
    qsl_new = []
    for k,v in qsl:
        if k in expected_parameters:
            qsl_new.append((k, v))
    query_string = urllib.parse.urlencode(qsl_new)
    return "?" + query_string
