
def is_empty_string(msg):

    if msg == 'None' or msg == '' or msg is None:
        return True

    return False


def escape_string(msg):
    if msg is None:
        return None
    return msg.replace("'", "").replace('"', '').strip()


def convert_to_numpy(arr, col=None):
    import numpy as np

    if arr is None or len(arr) == 0:
        return np.array([])

    data = np.char.mod('%s', np.array([i for i in arr]))

    if col == None or len(arr) == 0:
        return data

    return data[:, [index for index, item in enumerate(arr[0].keys()) if item in col]]


def map_pk(arr, value):
    import numpy as np
    assert isinstance(arr, np.ndarray)

    if len(arr) == 1:
        if arr[0][1] == value:
            return arr[0][0]

    # if dont have pj return none
    if arr[np.argwhere(arr == value)].size == 0:
        return None

    return arr[np.argwhere(arr == value)][0][0][0]


def map_name(arr, value):
    import numpy as np
    assert isinstance(arr, np.ndarray)
    value = str(value)

    if len(arr) == 1:
        if arr[0][0] == value:
            return arr[0][1]

    # if dont have pk return none
    if arr[np.argwhere(arr == value)].size == 0:
        return None
    return arr[np.argwhere(arr == value)][0][0][1]
