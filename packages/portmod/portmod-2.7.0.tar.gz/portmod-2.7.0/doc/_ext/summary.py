import os

import docutils
from docutils.parsers.rst import Directive, Parser
from docutils.utils import new_document


class Summary(Directive):
    has_content = True

    def run(self):
        path = os.path.join(
            os.path.dirname(self.state.document.current_source), self.content[0]
        )

        self.state.document.settings.record_dependencies.add(path)

        with open(path) as file:
            document = new_document(path, self.state.document.settings)
            Parser().parse(file.read(), document)
            for paragraph in document.findall(docutils.nodes.paragraph):
                if paragraph.astext().strip():
                    if paragraph.astext().startswith("Duplicate implicit target name"):
                        continue
                    summary = paragraph
                    break

        return [summary]


def setup(app):
    app.add_directive("summary", Summary)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
