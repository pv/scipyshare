from django import template
register = template.Library()

from scipyshare.catalog.models import Entry
from scipyshare.community.models import TagCache
from scipyshare.community import permissions

@register.inclusion_tag('community/tag_list.html')
def tag_list(entry):
    tags = entry.tags.all()
    return dict(tags=tags)

@register.tag
def ifperm(parser, token):
    r = token.split_contents()
    tag_name = r.pop(0)
    perm_name = r.pop(0)
    variable_names = r
    nodelist = parser.parse(('endifperm',))
    parser.delete_first_token()
    return IfPerm(perm_name, variable_names, nodelist)

@register.tag
def ifnperm(parser, token):
    r = token.split_contents()
    tag_name = r.pop(0)
    perm_name = r.pop(0)
    variable_names = r
    nodelist = parser.parse(('endifnperm',))
    parser.delete_first_token()
    return IfPerm(perm_name, variable_names, nodelist, negate=True)

class IfPerm(template.Node):
    def __init__(self, perm_name, variable_names, nodelist, negate=False):
        try:
            if not perm_name.startswith('can_'):
                raise AttributeError()
            self.check_func = getattr(permissions, perm_name)
        except AttributeError:
            raise template.TemplateSyntaxError("unknown permission %r"
                                               % perm_name)

        self.variables = [template.Variable(x) for x in variable_names]
        self.nodelist = nodelist
        self.negate = negate

    def render(self, context):
        user = template.Variable('user').resolve(context)
        args = [user] + [x.resolve(context) for x in self.variables]
        val = self.check_func(*args)
        if (not self.negate and val) or (self.negate and not val):
            return self.nodelist.render(context)
        else:
            return u""
