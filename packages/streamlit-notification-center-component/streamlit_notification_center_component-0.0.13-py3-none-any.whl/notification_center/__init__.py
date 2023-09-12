import os
import re
import streamlit.components.v1 as components
import streamlit as st
import random
import string

from bs4 import BeautifulSoup, SoupStrainer
from typing import Callable, Union, Dict

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

class NCEventManager:
  """
  The NCEventManager class provides an interface for managing event subscriptions,
  unsubscriptions, and publishing events. It enables a simple pub/sub pattern,
  allowing functions to be called in response to named events.

  :example:
    def on_custom_event(data):
      print("Custom event received:", data)

    manager = NCEventManager()
    manager.subscribe("custom_event", on_custom_event)
    manager.publish("custom_event", "Hello, World!")
  """

  def __init__(self):
    """
    Initializes a new instance of the NCEventManager with an empty set of listeners.
    """
    self.listeners = {}

  def subscribe(self, event_name, callback):
    """
    Subscribe to an event with a given callback function. If the event doesn't exist,
    it will be created, and the callback will be added to its listeners.

    :param event_name: The name of the event to subscribe to.
    :param callback:   The function to be called when the event is published.
    :type event_name:  str
    :type callback:    callable
    """
    if event_name not in self.listeners:
      self.listeners[event_name] = []
    self.listeners[event_name].append(callback)

  def unsubscribe(self, event_name, callback):
    """
    Unsubscribe a given callback function from an event. If the event or the callback
    does not exist, the method will do nothing.

    :param event_name: The name of the event to unsubscribe from.
    :param callback:   The function to be unsubscribed from the event.
    :type event_name:  str
    :type callback:    callable
    """
    if event_name in self.listeners:
      self.listeners[event_name].remove(callback)

  def publish(self, event_name, data=None):
    """
    Publish an event, triggering all subscribed listeners with the given data. If the event
    does not exist, the method will do nothing.

    :param event_name: The name of the event to publish.
    :param data:       Optional data to be passed to the subscribed listeners.
    :type event_name:  str
    :type data:        Any, optional
    """
    for callback in self.listeners.get(event_name, []):
      callback(data)

def nc_ensure():
  # Establish a event manager in the session_state
  if '_nc_events' not in st.session_state:
    st.session_state.setdefault('_nc_events', NCEventManager())

  # Establish a place for additional startup functions
  if '_nc_startup_fns' not in st.session_state:
    st.session_state.setdefault('_nc_startup_fns', [])

  # Create a _nc_debug value in session state that will govern debugging output
  # for the component while its in use.
  if '_nc_debug' not in st.session_state:
    st.session_state.setdefault('_nc_debug', False)

  # Setup the storage for NotificationCenter values. 
  if '_nc_data' not in st.session_state:
    st.session_state.setdefault('_nc_data', {})

  if '_nc_subs' not in st.session_state:
    st.session_state.setdefault('_nc_subs', {})

  # Setup html, css, script defaults
  if '_nc_script_srcs' not in st.session_state:
    st.session_state.setdefault('_nc_script_srcs', [])

  if '_nc_link_rels' not in st.session_state:
    st.session_state.setdefault('_nc_link_rels', [])

  if '_nc_javascript' not in st.session_state:
    st.session_state.setdefault('_nc_javascript', [
      f'''
        function ncSendMessage(target, body) {{
          Array.from(window.parent.frames).forEach((frame) => {{
            frame.postMessage({{ type: 'nc', target: target, payload: body }}, "*")
          }})
        }}

        function ncClearTarget(target) {{
          Array.from(window.parent.frames).forEach((frame) => {{
            frame.postMessage({{ type: 'nc', target: target, command: 'clear' }}, "*")
          }})
        }}

        function ncClearAll() {{
          Array.from(window.parent.frames).forEach((frame) => {{
            frame.postMessage({{ type: 'nc', command: 'clear-all' }}, "*")
          }})
        }}
      '''
    ])

  if '_nc_styles' not in st.session_state:
    st.session_state.setdefault('_nc_styles', [])
  
  if '_nc_html' not in st.session_state:
    st.session_state.setdefault('_nc_html', [])

  if len(st.session_state._nc_startup_fns):
    for fn in st.session_state._nc_startup_fns:
      if callable(fn):  # Type-check
        try:
          fn()
        except Exception as e:
          st.write(f"An exception occurred while running {fn.__name__}: {str(e)}")
      else:
        st.write(f"Registered function {fn} is not callable")

def nc_get(key, default_value=None):
  """
  Retrieves the value associated with a given key from the session state.
  
  Args:
      key (str): The key for the value to retrieve.
      default_value (optional): The value to return if the key is not found. Defaults to None.

  Returns:
      The value associated with the key if found, or the default value if the key is not found.
  """
  nc_ensure()

  if st.session_state._nc_data.get(key) is not None:    
    return st.session_state._nc_data[key]
  else:
    return default_value
  
def nc_get_last(key, default_value=None):
  """
  Retrieves the value associated with a given key from the session state.
  
  Args:
      key (str): The key representing an array of messages with tis target
      default_value (optional): The value to return if the key is not found. Defaults to None.

  Returns:
      The last value for the specified `key` rather than the whole array. If no
      value is forthcoming, `default_value` is returned instead.
  """
  nc_ensure()
  if st.session_state._nc_data.get(key) != None:
    channel = st.session_state._nc_data.get(key)
    if channel:
      return channel[-1]
    else:
      return default_value 
  else:
    return default_value

def nc_get_all():
  """
  Retrieves all key-value pairs stored in the session state.
  
  Returns:
      dict: A dictionary containing all key-value pairs in the session state.
  """
  nc_ensure()  
  return st.session_state.get('_nc_data', {})

def nc_set(key, value):
  """
  Stores a value in the session state, associated with a given key.
  
  Args:
      key (str): The key to associate with the value.
      value: The value to store.
  """
  nc_ensure()  
  channel = st.session_state._nc_data.setdefault(key, [])
  channel.append(value)
  st.session_state._nc_events.publish(key, value)

def nc_has(key):
  """
  Checks whether a given key exists in the session state.
  
  Args:
      key (str): The key to check for existence.

  Returns:
      bool: True if the key exists, False otherwise.
  """  
  return [False, True][nc_get(key) != None]

def nc_clear(key):
  """
  Clears the value associated with a given key in the session state.
  
  Args:
      key (str): The key for the value to clear.
  """  
  nc_ensure()  
  nc_get(key, []).clear()

def nc_clear_all():
  """
  Clears all key-value pairs stored in the session state.
  """
  nc_ensure()  
  st.session_state._nc_data = {}

def nc_add_substitution(str_or_re, val_or_fn):
  """
  Adds a substitution pattern to the session state for later use in string replacement.

  This function allows for the addition of a substitution pattern to the global session state,
  which can be later utilized by a string replacement function. The pattern to be replaced
  can be specified either as a string or as a compiled regular expression object, and the
  replacement value can be provided as either a string or a callable function.

  If the key for the callable value is a regular expression compilation, any grouped values
  in the expression should be applied as individual parameters to the callable.

  Args:
    str_or_re (str | _sre.SRE_Pattern): The string or regular expression pattern to be
      replaced. If given as a string, it will be used as a literal search pattern.
    val_or_fn (str | Callable): The replacement value, either as a string or as a callable
      function that returns the replacement string. If a callable is provided and the search
      pattern is a regular expression with groups, the callable will be invoked with the
      grouped values as individual parameters.

  Example:
    # Adding a simple string replacement
    nc_add_substitution('foo', 'bar')

    # Adding a regex pattern with callable replacement
    pattern = re.compile(r'(\d+)')
    nc_add_substitution(pattern, lambda x: str(int(x) * 2))

  Note:
    This function assumes the use of '_nc_subs' as an internal session state variable for
    managing substitutions within the app.
  """  
  nc_ensure()
  st.session_state._nc_subs[str_or_re] = val_or_fn

def nc_add_script_src(src, attributes=None, raw=False):
  """
  Appends a new script source to the '_nc_script_srcs' session state list.

  This function takes a script source (URL or path) and optionally a dictionary 
  of HTML attributes, and appends a formatted script tag or raw source to the 
  '_nc_script_srcs' session state list. If 'raw' is False, the 'src' and 
  'attributes' are used to create a '<script>' tag using BeautifulSoup.

  Args:
    src (str): The source URL or path of the script.
    attributes (dict, optional): Additional HTML attributes to be set on the script tag.
                                 Should be provided as a dictionary of attribute 
                                 name-value pairs.
    raw (bool, optional): If True, the 'src' is appended as-is without wrapping in 
                          a script tag.
                          If False, a '<script>' tag is created with the provided 
                          'src' and 'attributes'.

  Raises:
    SomeTypeError: If the provided 'attributes' is not a dictionary 
                   (if implemented in the code).
    SomeOtherPotentialError: Any other potential exception that could be relevant, 
                             depending on the rest of the code context.

  Example:
    nc_add_script_src('https://example.com/script.js', {'async': True}, False)
  """
  nc_ensure()
  if raw:
    st.session_state._nc_script_srcs.append(src)
  else:
    soup = BeautifulSoup('<script></script>', 'lxml')
    attrs = {'src': src}
    if attributes is not None and isinstance(attributes, dict):
      attrs.update(attributes)
    soup.script.attrs = attrs 
    st.session_state._nc_script_srcs.append(str(soup.script))

def nc_add_link_rel(href, attributes=None, raw=False):
  """
  Appends a new link rel tag to the '_nc_link_rels' session state list.

  This function takes a link source (URL or path) and optionally a dictionary 
  of HTML attributes, and appends a formatted link tag or raw source to the 
  '_nc_link_rels' session state list. If 'raw' is False, the 'href' and 
  'attributes' are used to create a '<link>' tag using BeautifulSoup.

  Args:
    href (str): The source URL or path of the link.
    attributes (dict, optional): Additional HTML attributes to be set on the link tag.
                                 Should be provided as a dictionary of attribute 
                                 name-value pairs.
    raw (bool, optional): If True, the 'href' is appended as-is without wrapping in 
                          a link tag.
                          If False, a '<link>' tag is created with the provided 
                          'href' and 'attributes'.

  Raises:
    SomeTypeError: If the provided 'attributes' is not a dictionary 
                   (if implemented in the code).
    SomeOtherPotentialError: Any other potential exception that could be relevant, 
                             depending on the rest of the code context.

  Example:
    nc_add_link_rel('https://example.com/styles.css', {'rel': 'stylesheet'}, False)
  """
  nc_ensure()
  if raw:
    st.session_state._nc_link_rels.append(href)
  else:
    soup = BeautifulSoup('<link />', 'lxml')
    attrs = {'href': href, 'rel': 'stylesheet'}
    if attributes is not None and isinstance(attributes, dict):
      attrs.update(attributes)
    soup.link.attrs = attrs 
    st.session_state._nc_link_rels.append(str(soup.link))

def nc_add_script(script):
  """
  Adds a JavaScript snippet to the session state for inclusion in subsequent HTML
  rendering.

  This function allows for the addition of JavaScript code snippets to the global
  session state, which can be later utilized by the nc_html function to render
  within the Streamlit app.

  Args:
    script (str): A string containing the JavaScript code snippet to add.

  Returns:
    None.

  Example:
    nc_add_script("console.log('This script was added.');")
  """
  nc_ensure()
  st.session_state._nc_javascript.append(script)

def nc_add_style(style):
  """
  Adds a CSS snippet to the session state for inclusion in subsequent HTML rendering.

  This function allows for the addition of CSS code snippets to the global session
  state, which can be later utilized by the nc_html function to render within the
  Streamlit app.

  Args:
    style (str): A string containing the CSS code snippet to add.

  Returns:
    None.

  Example:
    nc_add_style("div { color: blue; }")
  """
  nc_ensure()
  st.session_state._nc_styles.append(style)

def nc_add_html(html):
  """
  Adds an HTML snippet to the session state for inclusion in subsequent HTML rendering.

  This function allows for the addition of HTML code snippets to the global session
  state, which can be later utilized by the nc_html function to render within the
  Streamlit app.

  Args:
    html (str): A string containing the HTML code snippet to add.

  Returns:
    None.

  Example:
    nc_add_html("<div class='added-html'>This HTML was added.</div>")
  """
  nc_ensure()
  st.session_state._nc_html.append(html)

def nc_add_startup(fn):
  """
  Adds a startup function to automatically execute every time nc_ensure is invoked. Note
  that caution should be taken with the function as it will execute often. Ensure that
  usage does not clog the session_state and that the functions execution does not
  inadvertently slow down overall page execution.

  Args:
    fn (callable): A function to execute everytime nc_ensure executes

  Returns:
    None.

  Example:
    def app_setup:
      ...

    nc_add_startup(app_setup)
  """
  nc_ensure()
  st.session_state._nc_startup_fns.append(fn)

def nc_reset_script_srcs():
  """
  Resets the session state list of script sources ('_nc_script_srcs').

  This function removes the '_nc_script_srcs' key from the Streamlit session state
  if it exists, effectively resetting the list of stored script sources. It then ensures
  the initialization of session state by calling the 'nc_ensure' function.

  Note that '_nc_script_srcs' is assumed to be an internal session state variable used
  to manage script sources within the app.

  Example:
    # To reset the stored script sources
    nc_reset_script_srcs()
  """
  if '_nc_script_srcs' in st.session_state:
    del st.session_state._nc_script_srcs
  nc_ensure()

def nc_reset_link_rels():
  """
  Resets the session state list of link relationship tags ('_nc_link_rels').

  This function removes the '_nc_link_rels' key from the Streamlit session state
  if it exists, effectively resetting the list of stored link relationship tags. It
  then ensures the initialization of session state by calling the 'nc_ensure' function.

  Note that '_nc_link_rels' is assumed to be an internal session state variable used
  to manage link relationship tags within the app.

  Example:
    # To reset the stored link relationship tags
    nc_reset_link_rels()
  """
  if '_nc_link_rels' in st.session_state:
    del st.session_state._nc_link_rels
  nc_ensure()

def nc_reset_subs():
  """
  Resets the session state list of subscriptions ('_nc_subs').

  This function removes the '_nc_subs' key from the Streamlit session state if it exists,
  effectively resetting the list of stored subscriptions. It then ensures the initialization
  of session state by calling the 'nc_ensure' function.

  Note that '_nc_subs' is assumed to be an internal session state variable used to manage
  subscriptions within the app.

  Example:
    # To reset the stored subscriptions
    nc_reset_subs()
  """
  if '_nc_subs' in st.session_state:
    del st.session_state._nc_subs
  nc_ensure()

def nc_reset_scripts():
  """
  Resets the JavaScript snippets stored in the session state.

  This function removes all JavaScript snippets added through nc_add_script, 
  returning the session state to its default without any additional scripts.

  Returns:
    None.
  """
  if '_nc_javascript' in st.session_state:
    del st.session_state._nc_javascript 
  nc_ensure()

def nc_reset_styles():
  """
  Resets the CSS snippets stored in the session state.

  This function removes all CSS snippets added through nc_add_style, 
  returning the session state to its default without any additional styles.

  Returns:
    None.
  """
  if '_nc_styles' in st.session_state:
    del st.session_state._nc_styles
  nc_ensure()

def nc_reset_html():
  """
  Resets the HTML snippets stored in the session state.

  This function removes all HTML snippets added through nc_add_html, 
  returning the session state to its default without any additional HTML snippets.

  Returns:
    None.
  """
  if '_nc_html' in st.session_state:
    del st.session_state._nc_html
  nc_ensure()

def nc_reset_startup_fns():
  """
  Resets the additional startup functions called every time nc_ensure executes

  This function removes all additional user defined startup functions from the
  internal list of startup functions.

  Returns:
    None.
  """
  if '_nc_startup_fns' in st.session_state:
    del st.session_state._nc_startup_fns
  nc_ensure()

def nc_listen(to, callback) -> Callable:
  """
  Subscribes a callback function to a specified event within the Streamlit app's session state.

  This function associates the given callback with the specified event name within the
  session state's event manager. A lambda function is then returned, allowing for easy
  unsubscription from the event at a later time.

  Args:
    to (str): The name of the event to which the callback should be subscribed. This is a
              string identifier for the event.
    callback (Callable): The callback function to be invoked when the specified event is
                         published. The signature of this function will depend on the
                         expected data for the event.

  Returns:
    Callable: A lambda function that, when invoked, will unsubscribe the given callback
              from the specified event within the session state's event manager.

  Raises:
    This function may raise exceptions if used outside the context of a Streamlit app, or
    if there are issues with the provided parameters (e.g., invalid event name).

  Example:
    # Subscribe to an event called 'data_received'
    unsubscribe = nc_listen('data_received', lambda data: print('Data:', data))

    # Later in the code, you can call `unsubscribe()` to remove the callback
    unsubscribe()
  """
  nc_ensure()
  st.session_state._nc_events.subscribe(to, callback)
  return lambda: st.session_state._nc_events.unsubscribe(to, callback)

def generate_semi_unique_id(section_count=3):
  """Generate a semi-unique ID made of 3-letter combinations separated by dashes.

  Args:
      section_count (int): The number of 3-letter sections in the ID.

  Returns:
      str: The generated semi-unique ID.
  """
  sections = []
  for _ in range(section_count):
    section = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
    sections.append(section)

  return '-'.join(sections)

def nc_html(
        html = None,
        file_path = None,
        id = None,
        extra_js = None,
        extra_css = None,
        width = None,
        height = None,
        scrolling = False
):
  """
  Renders HTML content in a component using specified parameters.

  Args:
    html (str, optional): A string containing the raw HTML content to be rendered. 
                          Default is None.
    file_path (str, optional): The path to the HTML file that needs to be rendered. 
                               Default is None.
    extra_js (list, optional): A list of additional JavaScript code segments that 
                              need to be included. Default is None.
    extra_css (list, optional): A list of additional CSS styles that need to be 
                               included. Default is None.
    width (int, optional): The width of the rendered component in pixels. 
                           Default is None.
    height (int, optional): The height of the rendered component in pixels. 
                            Default is None.
    scrolling (bool): If True, a scrollbar will be included if the content 
                      overflows the defined height and width. Default is False.

  Raises:
    ValueError: If both 'html' and 'file_path' are provided or none of them is provided.

  Notes:
    Only one of 'html' and 'file_path' should be provided to render the content.
    If 'html' is provided, it will be rendered as raw HTML and not escaped.

  Examples:
    nc_html(html='<h1>Title</h1>', extra_css=['body { color: red; }'])
    nc_html(file_path='path/to/file.html', width=500, height=300)
  """  
  nc_ensure()

  if id is None:
    id = generate_semi_unique_id()

  if html is not None and file_path is not None:
    raise ValueError("Only one of 'html' or 'file_path' should be provided.")  

  if html is None and file_path is None:
    raise ValueError("One of 'html' or 'file_path' must be provided.")

  js = '\n'.join(st.session_state._nc_javascript + ([] if extra_js is None else extra_js))
  css = '\n'.join(st.session_state._nc_styles + ([] if extra_css is None else extra_css))
  pre = '\n'.join(st.session_state._nc_html)
  linkrels = '\n'.join(st.session_state._nc_link_rels)
  scriptsrcs = '\n'.join(st.session_state._nc_script_srcs)
  content = ''
  loaded_from_disk = False

  if height is None:
    # Automatically resizes the iframe to the size of the content once its DOM content
    # has loaded completely. Will not solve for all solutions, but will solve for most
    # Also why 22? It seems the iframe likes to cutoff the bottom of the content in at
    # least
    #   Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
    #   AppleWebKit/537.36 (KHTML, like Gecko)
    #   Chrome/116.0.0.0 Safari/537.36
    js += f'''
        document.addEventListener("DOMContentLoaded", function() {{
          Array
            .from(top.document.querySelectorAll('iframe[srcdoc*={id}]'))
            .forEach(iframe => {{
              if (iframe?.contentWindow?.document?.body?.clientHeight) {{
                iframe.setAttribute(
                  'height',
                  iframe.contentWindow.document.body.clientHeight + 22
                );
              }}
            }})
          }})
    '''

  soup = None
  if file_path is not None:
    with open(file_path, 'r') as file:
      file_contents = file.read()
      soup = BeautifulSoup(file_contents, 'lxml')
      if not soup.html or not soup.body:
        soup = None

  if file_path is None or soup is None:
    content = f'''
      <!DOCTYPE html>
      <html id="{id}">
        <head>
          {linkrels}
        </head>
        <body>
          {scriptsrcs}
          <script>{js}</script>
          <style>{css}</style>
          {pre}
          {html}
        </body>
      </html>
    '''
  else:      
    index = 0
    loaded_from_disk = True
    if soup.body and not soup.html:
      old_soup = soup
      soup = BeautifulSoup('<html></html>', 'lxml')
      soup.html.append(old_soup.body.extract())

    if not soup.head:
      soup.html.append(soup.new_tag('head'))

    if not soup.body:
      soup.html.append(soup.new_tag('body'))

    if len(linkrels):
      link_tags_soup = BeautifulSoup(linkrels, 'lxml')
      for tag in link_tags_soup.find_all('link'):
        soup.head.insert(index, tag)
        index += 1

    if len(scriptsrcs):
      script_tags_soup = BeautifulSoup(scriptsrcs, 'lxml')
      for tag in script_tags_soup.find_all('script'):
        soup.body.insert(index, tag)
        index += 1

    if len(js):
      script_tag = soup.new_tag('script')
      script_tag.string = js
      soup.body.insert(index, script_tag)
      index += 1

    if len(css):
      style_tag = soup.new_tag('style')
      style_tag.string = css
      soup.body.insert(index, style_tag)
      index += 1

    if len(pre):
      pre_soup = BeautifulSoup(pre, 'lxml', parse_only=SoupStrainer(True))
      for tag in pre_soup.contents:
        soup.body.insert(index, tag)
        index += 1

    if html and len(html):
      html_soup = BeautifulSoup(html, 'lxml', parse_only=SoupStrainer(True))
      for tag in html_soup.contents:
        soup.body.append(tag)
      
    soup.find('html').attrs['id'] = id
    content = str(soup)

  if len(st.session_state._nc_subs):
    content = replace_string(content, st.session_state._nc_subs)

  if loaded_from_disk:
    content = replace_string(content, {
      '{{': '{',
      '}}': '}'
    })

  st.components.v1.html(content, width=width, height=height, scrolling=scrolling)

def nc_use_htmx():
  """
  Includes htmx 1.9.4 JavaScript library in the current session.

  This function ensures that htmx's library is included in all susequent calls to 
  nc_html(). This library allows a lot of modern JavaScript features to be easily
  accessible from html tags. To learn more about the usage of htmx, visit this url:
  https://htmx.org/docs/#introduction

  Examples:
    nc_use_htmx()

  Notes:
    - This function specifically loads htmx version 1.9.4
    - It must be called after `nc_ensure()` to properly initialize the context.
    - The htmx JavaScript bundle is also loaded with anonymous crossorigin attributes.
  """
  nc_ensure()
  nc_add_script_src(
    "https://unpkg.com/htmx.org@1.9.4",
    attributes={
      'integrity': 'sha384-zUfuhFKKZCbHTY6aRR46gxiqszMk5tcHjsVFxnUo8VMus4kHGVdIYVbOYYNlKmHV',
      'crossorigin': 'anonymous'
    }
  )

def nc_is_using_htmx():
  """
  Checks to see if nc_use_htmx() has been called yet.

  This function returns True if nc_use_htmx() has been invoked and False otherwise

  Examples:
    def setup_fn():
      if not nc_is_using_htmx():
        nc_use_htmx()

    nc_add_startup(setup_fn)
  """
  has_htmx_js = False
  for script in st.session_state._nc_script_srcs:
    if "htmx.org@" in script:
      has_htmx_js = True
      break

  return has_htmx_js

def nc_use_bootstrap():
  """
  Includes Bootstrap (v5.1.3) CSS and JavaScript in the current session.

  This function ensures that Bootstrap's styles and scripts are added to the page,
  allowing the use of Bootstrap components and styling within the HTML content.
  Bootstrap is loaded from a CDN and includes integrity attributes for security.

  Examples:
    nc_use_bootstrap()

  Notes:
    - This function specifically loads Bootstrap version 5.1.3.
    - It must be called after `nc_ensure()` to properly initialize the context.
    - The Bootstrap CSS is loaded with integrity and anonymous crossorigin attributes.
    - The Bootstrap JavaScript bundle is also loaded with anonymous crossorigin attributes.
  """
  nc_ensure()
  nc_add_link_rel(
    "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
    attributes={
      "integrity": "sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3",
      "crossorigin": "anonymous"
    }
  )
  nc_add_script_src(
    "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js", 
    attributes={"crossorigin":"anonymous"}
  )

def nc_is_using_bootstrap():
  """
  Checks to see if nc_use_bootstrap() has been called yet.

  This function returns True if nc_use_bootstrap() has been invoked and False otherwise

  Examples:
    def setup_fn():
      if not nc_is_using_bootstrap():
        nc_use_bootstrap()

    nc_add_startup(setup_fn)
  """
  has_bootstrap_css = False
  for link in st.session_state._nc_link_rels:
    if "bootstrap@" in link:
      has_bootstrap_css = True
      break

  has_bootstrap_js = False
  for script in st.session_state._nc_script_srcs:
    if "bootstrap" in script:
      has_bootstrap_js = True
      break

  return has_bootstrap_css and has_bootstrap_js

def replace_string(text: str, replacements: Dict[Union[str, re.Pattern], Union[str, Callable]]) -> str:
  """Replaces substrings in the given text using the provided replacements dictionary.

  This function iterates over the replacements dictionary, where the keys can be either 
  strings or compiled regular expression patterns, and the values can be either 
  replacement strings or Callables (functions). If a key is a regular expression with 
  groups, the matched groups are passed as individual parameters to the Callable value.

  Args:
    text (str): The original text to be modified.
    replacements (Dict[Union[str, re.Pattern], Union[str, Callable]]): The dictionary of replacements.
      - Key: A string or a compiled regular expression pattern to be replaced.
      - Value: A string or a Callable that returns the replacement string.

  Returns:
    str: The modified text after performing the replacements.

  Raises:
    TypeError: If the search pattern is not a string or a compiled regular expression.

  Examples:
    Basic string replacements:
    >>> replace_string("Hello world!", {'world': 'Python world'})
    'Hello Python world!'

    Using a Callable as a replacement:
    >>> replacements = {'world': lambda: 'Python world'}
    >>> replace_string("Hello world!", replacements)
    'Hello Python world!'

    Regular expression with groups and Callable:
    >>> pattern = re.compile(r'(\d+) (\w+)')
    >>> replacements = {pattern: lambda num, word: f'{int(num) * 2} {word}s'}
    >>> replace_string("I have 3 apples and 5 oranges.", replacements)
    'I have 6 apples and 10 oranges.'
  """  
  for search_pattern, replacement in replacements.items():
    # Check if the search pattern is a string or a compiled regular expression
    if isinstance(search_pattern, str):
      text = text.replace(search_pattern, replacement if isinstance(replacement, str) else replacement())
    elif isinstance(search_pattern, re.Pattern):
      def repl(match):
        # Check if the replacement is a Callable and apply groups from the regular expression as parameters
        if callable(replacement):
          return replacement(*match.groups())
        return replacement
      text = search_pattern.sub(repl, text)
    else:
      raise TypeError("The search pattern must be either a string or a compiled regular expression (_sre.SRE_Pattern)")
  return text

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
  _component_func = components.declare_component(
    # We give the component a simple, descriptive name ("notification_center"
    # does not fit this bill, so please choose something better for your
    # own component :)
    "notification_center",

    # Pass `url` here to tell Streamlit that the component will be served
    # by the local dev server that you run via `npm run start`.
    # (This is useful while your component is in development.)
    url="http://localhost:3001",
  )
else:
  # When we're distributing a production version of the component, we'll
  # replace the `url` param with `path`, and point it to the component's
  # build directory:
  parent_dir = os.path.dirname(os.path.abspath(__file__))
  build_dir = os.path.join(parent_dir, "frontend", "build")
  _component_func = components.declare_component("notification_center", path=build_dir)

# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def notification_center(key=None):
  """Create a new instance of "notification_center".

  Parameters
  ----------
  key: str or None
    An optional key that uniquely identifies this component. If this is
    None, and the component's arguments are changed, the component will
    be re-mounted in the Streamlit frontend and lose its current state.

  Returns
  -------
  dict
    A dictionary of string targets with an array of data or payloads
    from the messages in question. (This is the value passed to 
    `Streamlit.setComponentValue` on the frontend as a JSON serializable
    object.) The returned dictionary is stored in and is part of the
    st.session_state so it will persist beyond an update of the UI. If
    the message received by the notification center was added, you 
    will see its `target` key mapping to an array of `payload` data objects

  """
  nc_ensure()
  component_value = _component_func(key=key)

  if component_value == None:
    return nc_get_all()

  target = component_value.get('target')  
  if component_value.get('command') is not None:
    if component_value.get('command') == 'clear':
      nc_clear(target)

    elif component_value.get('command') == 'clear-all':
      nc_clear_all()

  else:
    payload = component_value.get('payload')
    if payload is None:
      return nc_get_all()
    nc_set(target, payload)

  if st.session_state._nc_debug:    
    print(f'[NotificationCenter({key})][{target}]', nc_get(target))  

  # We could modify the value returned from the component if we wanted.
  # There's no need to do this in our simple example - but it's an option.
  return nc_get_all()

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run notification_center/__init__.py`
if not _RELEASE:
  notification_center(key="globalnc")

  has_foo = nc_has('foo')
  foo_message_count = 0
  if has_foo:
    print(nc_get('foo'))
    foo_message_count = len(nc_get('foo'))

  has_tally = nc_has('tally')
  tally_message_count = 0
  if has_tally:
    print(nc_get('tally'))
    tally_message_count = len(nc_get('tally'))

  has_replacement = nc_has('replacement')
  replacement_message_count = 0
  if has_replacement:
    print(nc_get('replacement'))
    replacement_message_count = len(nc_get('replacement'))

  if not nc_is_using_bootstrap():
    nc_use_bootstrap()

  nc_add_style("* { font-weight: 150%; }")
  nc_add_substitution(
    re.compile(r'bsbutton:(\w+):(\w+):(.*?):(\{.*\})'),
    lambda type,key,text,data: f'''
      <button 
        type="button" 
        class="btn btn-{type}" 
        onclick="ncSendMessage(\'{key}\', {data})"
      >{text}</button>
    '''
  )

  nc_add_substitution(
    re.compile(r'bsbutton:cmd:(\w+):(.*?):(\w+)'),
    lambda type,text,key: f'''
      <button 
        type="button" 
        class="btn btn-{type}" 
        onclick="ncClearTarget(\'{key}\')"
      >{text}</button>
    '''
  )

  nc_add_substitution(
    re.compile(r'bsbutton:clearall:(\w+):(.*?):'),
    lambda type,text: f'''
      <button 
        type="button" 
        class="btn btn-{type}" 
        onclick="ncClearAll()"
      >{text}</button>
    '''
  )

  nc_add_substitution('{replacement_count}', f'{replacement_message_count}')

  nc_html(
    f'''
    <div>
      <p>
        <div>Streamlit component communication</div>
        bsbutton:primary:foo:Send to 'foo':{{button: 'foo'}}
        bsbutton:primary:tally:Send to 'tally':{{button: 'tally'}}
        <hr/>        
        <div>"foo" message received count: {foo_message_count}</div>
        <div>"tally" message received count: {tally_message_count}</div>
        <hr/>
      </p>
    </div>

    <p>
      bsbutton:cmd:warning:Clear 'foo':foo
      bsbutton:cmd:warning:Clear 'tally':tally
      bsbutton:clearall:primary:Clear All:
    </p>    
    '''
  )

  nc_html(file_path="/Users/brie/c/Python/streamlit_notification_center_component/notification_center/frontend/public/sample.html")
