import docutils

from sphinx.transforms import SphinxTransform


class TranslationCSSSubstitutions(SphinxTransform):
    default_priority = 50

    def apply(self, **kwargs):
        source = self.document.get('source')
        self.app.translations[source] = {'total': 0, 'translated': 0}

        for node in self.document.traverse():
            if not hasattr(node, 'get'):
                continue

            if node.get('translated', False):
                self.app.translations[source]['translated'] += 1
                classes = node.get('classes', [])
                classes.append(self.app.env.config.translated_class)
                node.replace_attr('classes', classes)

            # Only count the nodes that are translatable
            if len(node.children) == 1 and isinstance(node.children[0], docutils.nodes.Text):
                self.app.translations[source]['total'] += 1

        self.app.translations[source]['percentage'] = (self.app.translations[source]['translated'] / self.app.translations[source]['total']) * 100


class TranslationSubstitutions(SphinxTransform):
    default_priority = 70

    def apply(self, **kwargs):
        # only handle those not otherwise defined in the document
        to_handle = 'translated-percentage'
        for ref in self.document.findall(docutils.nodes.substitution_reference):
            refname = ref['refname']
            if refname == to_handle:
                text = self.app.translations[self.document.get('source')]['percentage']
                ref.replace_self(docutils.nodes.Text(text))


def setup(app):
    """Setup ``translated`` Sphinx extension."""
    app.add_config_value('translated_class', 'translated', 'env')
    app.add_css_file('translated.css')

    app.add_transform(TranslationCSSSubstitutions)
    app.add_transform(TranslationSubstitutions)

    app.translations = {}


    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
