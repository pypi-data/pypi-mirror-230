# hypymedia/main.py
from hypymedia.html_list import tags


def element(tag_name, end_tag=True) -> str:
    """
    This function takes in a tag name and an optional end tag flag.
    It returns a function that takes in any number of arguments.
    The first argument can be a dictionary of attributes.
    All other arguments are reduced to string outputs 
    and treated as content for the HTML tag.
    """
    def attributes_to_string(attributes: dict) -> str:
        """
        This function takes in a dictionary of attributes and converts it to a string.
        """
        return (
            " ".join(
                f'{k}="{v}"' if v is not True else k
                for k, v in (attributes or {}).items()
            )
            if attributes
            else ""
        )

    def inner(*args):
        # If the first argument is a dictionary, 
        # it is treated as attributes for the HTML tag
        attributes = args[0] if args and isinstance(args[0], dict) else None
        # All other arguments are treated as content for the HTML tag
        content_args = args if not attributes else args[1:]
        # All content arguments are reduced to string outputs
        content = "".join(map(str, content_args))

        # Convert the attributes dictionary to a string
        attributes_str = attributes_to_string(attributes)

        # If end_tag is True, include the end tag in the output
        end_tag_str = f"</{tag_name}>" if end_tag else ""

        # Return the final HTML tag string
        return f'<{tag_name}{" " + attributes_str if attributes_str else ""}>{content}{end_tag_str or ""}'  # noqa: E501

    return inner


for tag in tags:
    function_name = f"{tag[0]}"
    tag_name = tag[0][:-1]
    end_tag = tag[1]

    globals()[function_name] = element(tag_name, end_tag)
