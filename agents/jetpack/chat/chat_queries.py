import logging
from jinja2 import Environment, TemplateNotFound, select_autoescape
from grit import *
from wit import *
from jetpack.messages import ChatMessage

logger = logging.getLogger(__name__)

app = Wit()

@app.query("messages")
async def on_query_messages(core:Core, messagekey:str=None):
    message_filter = messagekey
    messages = await ChatMessage.load_from_tree(await core.gett("messages"), message_filter)
    logger.info(f"messages: {len(messages)}, filter: {message_filter}")
    return await render_template(core, "/templates/chat_messages.html", messages=messages)

env = Environment(autoescape=select_autoescape())
async def render_template(core:Core, template_path, **kwargs) -> BlobObject:
    template_blob = await core.get_path(template_path)
    if(template_blob is None):
        raise TemplateNotFound(f"Template not found: {template_path}")
    template_str = template_blob.get_as_str()
    template = env.from_string(template_str)
    rendered = template.render(**kwargs)
    rendered_blob = BlobObject.from_str(rendered)
    rendered_blob.set_headers_empty()
    rendered_blob.set_header('Content-Type', 'text/html')
    return rendered_blob