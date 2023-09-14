def apply_html_fixes(html):
    """At least some signup genius templates have some malformed html,
    which affects our ability to parse them.
    """
    for fix_fn in (_fix_div_within_comment,):
        html = fix_fn(html)
    return html


def _fix_div_within_comment(html):
    return html.replace(
        '<!--<div><span class="glyphicon glyphicon-ok-sign SUGicon"></span>-->',
        '<div><!--<span class="glyphicon glyphicon-ok-sign sugicon"></span>-->',
    )
