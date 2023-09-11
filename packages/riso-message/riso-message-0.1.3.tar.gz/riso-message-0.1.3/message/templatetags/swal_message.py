from django import template
from django.forms import Media

register = template.Library()


@register.simple_tag()
def swal_message_media(use_jquery=True):
    js = [
        "sweetalert2/sweetalert2.all.min.js",
        "toastr/toastr.min.js",
    ]
    if use_jquery:
        js.insert(0, "jquery/jquery.min.js")
    return Media(
        js=js,
        css={
            "all": [
                "sweetalert2/sweetalert2.min.css",
                "toastr/toastr.min.css",
            ]
        },
    )
