from pathlib import Path


def complete_filename(incomplete: str):
    completion = []
    for name in Path('.').iterdir():
        name = str(name)
        if name.startswith(incomplete):
            completion.append(name)
    return completion


if __name__ == '__main__':
    # test
    d = complete_filename('')
    print(d)
