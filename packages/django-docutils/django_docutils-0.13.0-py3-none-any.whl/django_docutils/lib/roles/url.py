from .common import generic_url_role


def url_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Role for linking to url articles.

    :url:`https://google.com` ->
       link: https://google.com
       text: https://google.com

    :url:`Google <https://google.com>` ->
        link: https://google.com
        text: Google

    :url:`*Google* <https://google.com>` ->
        link: https://google.com
        text (html): <em>Google</em>

    """

    if content is None:
        content = []
    if options is None:
        options = {}

    def url_handler(target):
        return target

    return generic_url_role(name, text, url_handler)
