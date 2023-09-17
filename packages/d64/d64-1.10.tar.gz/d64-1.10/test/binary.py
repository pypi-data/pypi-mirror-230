import json


def load_binary(path):
    """Return the contents of a file as a byte string."""
    with path.open('rb') as fileh:
        return fileh.read()


def load_patch(path):
    """Return a patch as an array of changes."""
    with path.open() as fileh:
        return json.load(fileh)


def diff(bin1, bin2):
    """Return the difference between two byte strings as an array of changes."""
    if len(bin1) != len(bin2):
        raise ValueError("Binary lengths differ")

    ret = []
    current_delta = None

    for i in range(0, len(bin1)):
        if bin1[i] == bin2[i]:
            if current_delta:
                ret.append(current_delta)
                current_delta = None
        else:
            if current_delta is None:
                current_delta = {'at': i, 'from': bytes([bin1[i]]), 'to': bytes([bin2[i]])}
            else:
                current_delta['from'] += bytes([bin1[i]])
                current_delta['to'] += bytes([bin2[i]])

    if current_delta:
        ret.append(current_delta)

    return ret


def patch(bin, patch, out_path):
    """Create a new file by patching a byte string."""
    pos = 0

    with out_path.open('wb') as fileh:
        for delta in patch:
            if pos != delta['at']:
                fileh.write(bin[pos:delta['at']])
                pos = delta['at']
            fileh.write(delta['to'])
            pos += len(delta['to'])

        if pos != len(bin):
            fileh.write(bin[pos:])
