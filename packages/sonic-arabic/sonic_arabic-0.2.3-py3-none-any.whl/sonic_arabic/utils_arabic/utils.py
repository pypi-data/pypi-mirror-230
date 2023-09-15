
def get_text(file_name='./data/text.txt', size=500, one_line=True):
    with open(file_name) as f:
        lines = f.readlines()[:size]
        lines = [line[26:] for line in lines]
    if one_line:
        return ' '.join(lines)
    return lines


def save_res(path_to_file, text):
    with open(path_to_file, "w") as text_file:
        text_file.write(text)