from copy import deepcopy
import re


# Convert path of int and slice types to str type to be used in dotted_dict
# This is to handle data being a non-str.
def path_str(path):
    dotted_path = path
    if type(dotted_path) == int:
        dotted_path = f"$[{dotted_path}]"
    elif type(dotted_path) == slice:
        start = dotted_path.start if dotted_path.start != None else ""
        stop = dotted_path.stop if dotted_path.stop != None else ""
        step = dotted_path.step if dotted_path.step != None else ""
        dotted_path = f"$[{start}:{stop}:{step}]"
    return dotted_path


# Dotted Dict
#   Take a dict or list object and return the attribute identified in `key_path`.
#   If `value` is not None, set the attribute with `value`.
#   If `delete` is True, delete the attribute (and ignore `value`).
#
#   Recursive algorithm:
#   - Takes subscripts as individual attributes.
#     - e.g., "var[9]" -> "var.[9]", "var[9][8]" -> "var.[9].[8]"
#   - If leaf (path blank)
#     - return the root_dict as is
#   - Else (path non-blank)
#     - If not begins with [...]
#       - If begins with "$"
#         - If there are dots
#           - return dotted_dict without "$."
#         - Else (leaf with key)
#           - Error if delete or update
#           - return the root_dict as is
#       - Elif (addressed element exists)
#         - If there are dots
#           - return dotted_dict(addressed element)
#         - Else (check delete/update)
#           - get the parent (from arg list)
#           - delete and update if so
#           - return the addressed element (the old value)
#       - Else (addressed element not exists)
#         - If delete return None
#         - Elif update
#           - If there are dots
#             - create the element by assigning {} to it
#             - return dotted_dict(element)
#           - Else
#             - create the element by assigning the value to it
#             - return the element
#         - Else
#           - return default
#     - If begins with [...]
#       - Handling slicing
#       - If list
#         - If there are dots
#           - return dotted_dict(addressed element)
#         - Else (leaf on selfy)
#           - If delete, do so
#           - Elif update, do so
#           - return the old value
#       - Elif dict
#         - If there are dots
#           - If slice, error
#           - Else return dotted_dict(addressed element)
#         - Else (no dots)
#           - If delete, do so
#           - Elif update, do so
#           - return the old value


def dotted_dict(
        root_dict,
        key_path="",
        default=None,
        delete=False,
        value=None,
        _parent_obj=None,
        _parent_key=None
    ):

    # root_dict is passed by reference
    # root_node is a twin of root_dict (a reference to the root node)
    # If delete is True, value will be ignored

    root_node = root_dict
    # Break down "var[9]" into "var.[9]", "var[9][8]" into "var.[9].[8]"
    path_keys = re.sub(r"(\[(-?[0-9:]+)\])", ".\\1", key_path).split(".")
    # Remove empty path key
    path_keys = [k for k in path_keys if k]

    # logger.debug(f"dotted_dict({root_node}, key_path={key_path}->{'.'.join(path_keys[1:])}, default={default}, delete={delete}, value={value}, _parent_obj, _parent_key={_parent_key})")

    # In each case, ret should be set.
    if len(path_keys) == 0:
        # Blank key addresses the root
        # logger.debug(f"dotted_dict - blank key")
        return root_node
    else:
        # Branch or leaf node the root_node is
        # The next level down is root_node[key]

        # _value = value
        # # Deepcopy value if dict
        # if type(_value) == dict or type(_value) == list:
        _value = deepcopy(value)

        key = path_keys[0]
        index_str = re.sub(r"^\[(.*)\]$", "\\1", key)

        if index_str == key:
            # It is a key
            if key == "$":
                # Path variable
                if len(path_keys) > 1:
                    # Branch node key exists - down one level
                    # logger.debug(f"dotted_dict - branch node: {key}")
                    return dotted_dict(root_node, '.'.join(path_keys[1:]), default, delete, _value, root_node, None)  # No parent
                else:
                    # Leaf node key exists - act on self
                    # logger.debug(f"dotted_dict - leaf node: {key}")
                    old_value = root_node
                    if delete:
                        # logger.debug(f"Error: Cannot delete {key}")
                        # return None
                        raise KeyError(f"Cannot delete {key}")
                    elif _value != None:
                        # logger.debug(f"Error: Cannot set value for {key}")
                        # return old_value
                        raise KeyError(f"Cannot set value for {key}")
                    else:
                        return old_value
            elif key in root_node:
                # Key exists
                if len(path_keys) > 1:
                    # Branch node key exists - down one level
                    # logger.debug(f"dotted_dict - branch key exists: {key}")
                    return dotted_dict(root_node[key], '.'.join(path_keys[1:]), default, delete, _value, root_node, key)
                else:
                    # Leaf node key exists - act on self
                    # logger.debug(f"dotted_dict - leaf key exists: {key}")
                    # logger.debug(f"dotted_dict - root_node: {root_node}")
                    old_value = root_node[key]

                    parent_obj = _parent_obj if _parent_obj else root_node
                    if _parent_key != None:
                        parent_obj = parent_obj[_parent_key]

                    if delete:
                        # logger.debug(f"dotted_dict - delete {key} from {root_node} (value={old_value})")
                        del parent_obj[key]
                    elif _value != None:
                        # logger.debug(f"dotted_dict - set {key} to {value}")
                        # logger.debug(f"dotted_dict - _parent_obj={_parent_obj}")
                        # logger.debug(f"dotted_dict - _parent_key={_parent_key}")
                        parent_obj[key] = _value
                    return old_value
            else:
                # logger.debug(f"dotted_dict - key not exists: {key}")
                # Key does not exists
                if delete:
                    # logger.debug(f"dotted_dict - delete nothing")
                    # Nothing to delele
                    return None
                elif _value != None:
                    # Set value
                    if len(path_keys) > 1:
                        # Branch node - create the key (part of the path)
                        # logger.debug(f"dotted_dict - set value {value} on new branch {key}")
                        root_node[key] = {}
                        return dotted_dict(root_node[key], '.'.join(path_keys[1:]), default, delete, _value, root_node, key)
                    else:
                        # Leaf node
                        # logger.debug(f"dotted_dict - set value {value} on new leave {key}")
                        root_node[key] = _value
                        return root_node[key]
                else:
                    return default
        else:
            # It is an index
            # Index string is in index_str

            # Determine the indexes regardless of root_node type
            indexes_str = index_str.split(":")
            # logger.debug(f"dotted_dict - indexes_str: {indexes_str}")
            if len(indexes_str) == 0 or len(indexes_str) > 3:
                # [] or [9:9:9:9...]
                raise KeyError(f"Invalid index syntax {indexes_str}")
            # [9] or [9:9] or [9:9:9]
            # logger.debug(f"dotted_dict - root_node len: {len(root_node)}")
            index_single = None
            index_slice = None
            if len(indexes_str) == 1:
                # indexes_str[0] must be not null,
                # or it would have been an error upon len(indexes_str) == 0
                # Special case of a single index
                index_single = int(indexes_str[0])
                # logger.debug(f"dotted_dict - index_single: {index_single}")
            else:
                indexes = [None] * 3
                for ii in range(3):
                    if len(indexes_str) > ii and indexes_str[ii]:
                        indexes[ii] = int(indexes_str[ii])
                index_slice = slice(indexes[0], indexes[1], indexes[2])
                # logger.debug(f"dotted_dict - index_slice: {index_slice}")
            index_me = index_single if index_single != None else index_slice
            if index_me == None:
                # Should not happen - just to be defensive
                raise KeyError(f"Invalid index range {indexes_str} for {key} - index_me={index_me}")

            # logger.debug(f"dotted_dict - indexes: {indexes}")
            # logger.debug(f"dotted_dict - root_node is {type(root_node)}")

            if type(root_node) == list:
                if len(path_keys) > 1:
                    # Branch node
                    # logger.debug(f"dotted_dict - list branch single - recur root_node={root_node}")
                    return dotted_dict(root_node[index_me], '.'.join(path_keys[1:]), default, delete, _value, root_node, index_me)
                else:
                    # Leaf node - act on self
                    # logger.debug(f"dotted_dict - list leaf - act on self root_node={root_node}")
                    old_value = root_node[index_me]
                    if delete:
                        del root_node[index_me]
                    elif _value != None:
                        root_node[index_me] = _value
                    return old_value
            elif type(root_node) == dict:
                if len(path_keys) > 1:
                    # Branch node
                    if index_slice:
                        # Range index
                        # logger.debug(f"Error: Invalid index range {indexes_str} for branch node {key}")
                        # return default
                        raise KeyError(f"Invalid index range {indexes_str} for branch node {key}")
                    else:
                        # Single index
                        # logger.debug(f"dotted_dict - dict branch single - recur")
                        k = list(root_node.keys())[index_me]
                        return dotted_dict(root_node[k], '.'.join(path_keys[1:]), default, delete, _value, root_node, k)
                else:
                    # Leaf node - act on self, element by element
                    # List of keys in root_node that is to be returned, deleted or set value

                    # logger.debug(f"dotted_dict - root_node.keys(): {root_node.keys()}")
                    # logger.debug(f"dotted_dict - indexes: {indexes}")

                    ndx_key_list = list(root_node.keys())[index_me]
                    if type(ndx_key_list) != list:
                        ndx_key_list = [ndx_key_list]

                    # logger.debug(f"dotted_dict - dict leaf {ndx_key_list}")

                    old_value = {k: root_node[k] for k in ndx_key_list}

                    if delete:
                        for k in ndx_key_list:
                            del root_node[k]
                    elif _value != None:
                        # logger.debug(f"Error: Cannot set value for {key}[{indexes_str}]")
                        # return default
                        raise KeyError(f"Cannot set value for {key}[{indexes_str}]")

                    return old_value

    return default
