import docutils.core
import docutils.io
import docutils.nodes


extra_params = {
    'initial_header_level': '2',
    'syntax_highlight': 'short',
    'input_encoding': 'utf-8',
    'exit_status_level': 2,
    'embed_stylesheet': False
}

with open('mytest.rst') as fp:
    raw_data = fp.read()


publisher = docutils.core.Publisher(
            source_class=docutils.io.StringInput,
            destination_class=docutils.io.StringOutput)

publisher.set_components('standalone', 'restructuredtext', 'html')
# publisher.writer.translator_class = PelicanHTMLTranslator
publisher.process_programmatic_settings(None, extra_params, None)
publisher.set_source(source=raw_data)
output = publisher.publish(enable_exit_status=True)


print(output)
