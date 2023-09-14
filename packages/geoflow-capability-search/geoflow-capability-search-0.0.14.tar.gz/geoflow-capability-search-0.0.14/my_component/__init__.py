import os
import streamlit as st
import streamlit.components.v1 as components

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
_get_react_component = components.declare_component(
    "gf_capability_search",
#     url="http://localhost:3001",
#     TODO: For building should refer to build_dir
    path=build_dir,
)

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

# if not _RELEASE:
#     _component_func = components.declare_component(
#         # We give the component a simple, descriptive name ("my_component"
#         # does not fit this bill, so please choose something better for your
#         # own component :)
#         "my_component",
#         # Pass `url` here to tell Streamlit that the component will be served
#         # by the local dev server that you run via `npm run start`.
#         # (This is useful while your component is in development.)
#         url="http://localhost:3001",
#     )
# else:
#     # When we're distributing a production version of the component, we'll
#     # replace the `url` param with `path`, and point it to to the component's
#     # build directory:
#     parent_dir = os.path.dirname(os.path.abspath(__file__))
#     build_dir = os.path.join(parent_dir, "frontend/build")
#     _component_func = components.declare_component("my_component", path=build_dir)
#


def _process_search(
    search_function,
    key,
    searchterm,
):
    if searchterm == st.session_state[key]["search"]:
        return st.session_state[key]["result"]

#   Left this part to see what the searchterm will be
    print(searchterm, "SEARCHTERM")

    st.session_state[key]["search"] = searchterm
    search_results = search_function(searchterm)

    if search_results is None:
        search_results = []

    def _get_label(label: any) -> str:
            return str(label[0]) if isinstance(label, tuple) else str(label)

    def _get_value(value: any) -> any:
        return value[1] if isinstance(value, tuple) else value

    # used for react component
    st.session_state[key]["options"] = [
        {
            "label": _get_label(v),
            "value": i,
        }
        for i, v in enumerate(search_results)
    ]

    # used for proper return types
    st.session_state[key]["options_real_type"] = [_get_value(v) for v in search_results]

    st.experimental_rerun()


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def my_component(
    search_function,
    details_function,
    suggest_function,
    placeholder = "Search...",
    label = None,
    default = None,
    clear_on_submit = False,
    key = "searchbox",
    suggestions = None,
    **kwargs,
):
    """Create a new searchbox instance, that provides suggestions based on the user input
           and returns a selected option or empty string if nothing was selected".
    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    # key without prefix used by react component
    key_react = f"{key}_react"

    if key not in st.session_state:
        st.session_state[key] = {
            # updated after each selection / reset
            "result": default,
            # updated after each search keystroke
            "search": "",
            # updated after each search_function run
            "options": [],
            "suggestions": [],
        }

    # everything here is passed to react as this.props.args
    react_state = _get_react_component(
        options=st.session_state[key]["options"],
        suggestions=st.session_state[key]["suggestions"],
        clear_on_submit=clear_on_submit,
        placeholder=placeholder,
        label=label,
        # react return state within streamlit session_state
        key=key_react,
        **kwargs,
    )

    if react_state is None:
        return st.session_state[key]["result"]

    interaction, value = react_state["interaction"], react_state["value"]

    if interaction == "search":
        # triggers rerun, no ops afterwards executed
        _process_search(search_function, key, value)

    if interaction == "details":
        details_function(value)

    if interaction == "submit":
        suggest_function(value)

    if interaction == "reset":
        st.session_state[key]["result"] = default
        return default

    # no new react interaction happened
    return st.session_state[key]["result"]


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
if not _RELEASE:
    st.subheader("Capabilities search")

    def searchFunc (searchterm):
        print(searchterm, "SEARCHTERM from search func")

    def detailsFunc (details):
        print(details, "DETAILS from details func")

    def suggestFunc (suggest):
        print(suggest, "SUGGEST from suggest func")
#
#     # Create an instance of our component with a constant `name` arg, and
#     # print its output value.
    my_component(searchFunc, detailsFunc, suggestFunc)
#
