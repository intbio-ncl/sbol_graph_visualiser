def calculate_next_color(curr_color):
    curr_color = list(curr_color)
    if curr_color[0] != 0 and curr_color[1] == 0 and curr_color[2] == 0:
        curr_color[1] = curr_color[0]
        curr_color[0] = 0
    elif curr_color[0] == 0 and curr_color[1] != 0 and curr_color[2] == 0:
        curr_color[2] = curr_color[1]
        curr_color[1] = 0
    elif curr_color[0] == 0 and curr_color[1] == 0 and curr_color[2] != 0:
        curr_color[0] = curr_color[2]
        curr_color[1] = curr_color[2]
        curr_color[2] = 0
    elif curr_color[0] != 0 and curr_color[1] != 0 and curr_color[2] == 0:
        curr_color[2] = curr_color[1]
        curr_color[0] = 0
    elif curr_color[0] == 0 and curr_color[1] != 0 and curr_color[2] != 0:
        curr_color[0] = curr_color[1]
        curr_color[1] = 0
    elif curr_color[0] != 0 and curr_color[1] == 0 and curr_color[2] != 0:
        curr_color[0] = curr_color[0] / 2
        curr_color[1] = 0
        curr_color[2] = 0
    else:
        raise ValueError(curr_color)
    return tuple(curr_color)

def calculate_role_color(node_color,curr_mapping):
    role_color = [0,0,0]
    for index,e in enumerate(node_color):
        if e != 0:
            role_color[index] = 0
        else:
            for inner_e in node_color:
                if inner_e != 0:
                    role_color[index] = inner_e
    if tuple(role_color) in curr_mapping.values():
        # Index of elements that need to change
        to_change_elements = [index for index,e in enumerate(role_color) if e != 0]
        while tuple(role_color) in curr_mapping.values():
            # Get the values of the elements that need to change.
            curr_col = [e for index,e in enumerate(role_color) if index in to_change_elements]
            # Calculate updated Colors.
            colors = calculate_next_color_role(curr_col,max(role_color))
            # Get the new color value in the list if the index 
            role_color = [colors.pop() if index in to_change_elements else 0 for index,x in enumerate(role_color)]
    return tuple(role_color)


def calculate_next_color_role(color,not_zero_color):
    curr_color = color.copy()
    if len(curr_color) == 1:
        curr_color[0] = not_zero_color * 0.75

    elif len(curr_color) == 2:   
        if curr_color[0] != 0 and curr_color[1] != 0:
            curr_color[1] = curr_color[0]
            curr_color[0] = 0

        elif curr_color[0] == 0 and curr_color[1] != 0:
            curr_color[0] = curr_color[1]
            curr_color[1] = 0

        elif curr_color[0] != 0 and curr_color[1] == 0:
            curr_color[0] = curr_color[0] * 0.75
            curr_color[1] = curr_color[0] * 0.75
        else:
            raise ValueError(f'{curr_color}')
    else:
        return calculate_next_color(curr_color)

    return curr_color