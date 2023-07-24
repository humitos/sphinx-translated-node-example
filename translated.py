import docutils
from sphinx.transforms import SphinxTransform


class TranslationsManipulation(SphinxTransform):
    default_priority = 50

    def apply(self, **kwargs):
        filename = self.document.get('source')  # absolute source filename

        # Default values for current source filename
        self.app._translations[filename] = {
            'total': 0,
            'translated': 0,
        }

        # Traverse all the nodes of the document
        for node in self.document.traverse():
            if not hasattr(node, 'get'):
                # Discard nodes we cannot access to its attributes
                continue

            if any([isinstance(child, docutils.nodes.Text) for child in node.children]):
                # Only work over nodes with a text child
                if node.get('translated', False):
                    # Increase the translated nodes
                    self.app._translations[filename]['translated'] += 1
                    css_class = self.app.env.config.translated_class
                else:
                    css_class = self.app.env.config.untranslated_class

                # Append our custom untranslated CSS class to the node
                classes = node.get('classes', [])
                classes.append(css_class)
                node.replace_attr('classes', classes)

                # Increase the total of nodes
                self.app._translations[filename]['total'] += 1


        # Calculate total percentage of the page translated
        self.app._translations[filename]['percentage'] = (
            self.app._translations[filename]['translated'] /
            self.app._translations[filename]['total']
        ) * 100

        # Handle substitutions (used as ``|translated-page-percentage|`` in .rst source files)
        substitution = 'translated-page-percentage'
        for ref in self.document.findall(docutils.nodes.substitution_reference):
            refname = ref['refname']
            if refname == substitution:
                text = self.app._translations[filename]['percentage']
                newnode = docutils.nodes.Text(text)
                if 'classes' in ref:
                    ref.replace_attr('classes', [])
                ref.replace_self(newnode)


def setup(app):
    """
    Setup ``translated`` Sphinx extension.
    """
    # CSS class to add to translated nodes
    app.add_config_value('translated_class', 'translated', 'env')
    app.add_config_value('untranslated_class', 'untranslated', 'env')

    # Add the CSS file with our custom styles
    app.add_css_file('translated.css')

    app.add_transform(TranslationsManipulation)

    # Define an internal variable to store translated percentages
    app._translations = {}

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
