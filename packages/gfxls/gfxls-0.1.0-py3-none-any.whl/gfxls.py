#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import os
from shutil import get_terminal_size, which
from pathlib import Path
from argparse import ArgumentParser
import subprocess

import PIL.Image as Image
import vignette
from prettytable import PrettyTable, ALL, SINGLE_BORDER


__version__ = "0.1.0"


def get_list_and_thumbs(path):
    if path.is_dir():
        listed = path.iterdir()
    else:
        listed = [path]

    ret = {}
    for sub in listed:
        ret[sub] = vignette.get_thumbnail(str(sub))
    return ret


def fit_size(original, other):
    qw = original[0] / other[0]
    qh = original[1] / other[1]
    if qw > qh:
        return (other[0], int(original[1] // qw))
    else:
        return (int(original[0] // qh), other[1])


def image_to_ansi_basic(filename, size=(32, 32), halfblocks=True, fill=False):
    im = Image.open(filename)
    im = im.convert('RGB')
    im.thumbnail(size)
    if fill:
        new = Image.new('RGB', size)
        coords = (
            (size[0] - im.size[0]) // 2,
            (size[1] - im.size[1]) // 2,
        )
        new.paste(im, coords)
        im = new

    buf = []
    pix = im.load()
    w, h = im.size

    if halfblocks:
        yrange = range(0, h, 2)
    else:
        yrange = range(h)

    fmt = '2;%d;%d;%d'

    for y in yrange:
        for x in range(w):
            if halfblocks:
                if y + 1 >= h:
                    buf.append(u'\x1b[38;%sm\u2580' % fmt % pix[x, y])
                else:
                    buf.append(u'\x1b[38;%sm' % fmt % pix[x, y])
                    buf.append(u'\x1b[48;%sm\u2580' % fmt % pix[x, y + 1])
            else:
                buf.append(u'\x1b[48;%sm ' % fmt % pix[x, y])
        buf.append(u'\x1b[0m%s' % os.linesep)
    return ''.join(buf).rstrip()


def image_to_ansi_chafa(filename, size=(32, 32), halfblocks=True, fill=False):
    return subprocess.check_output(
        ['chafa', "-s", f"{size[0]}x{size[1] // 2}", filename],
        encoding='utf-8',
    ).rstrip()


def image_to_ansi(
    filename, size=(32, 32), halfblocks=True, fill=False, has_chafa=False
):
    if has_chafa:
        return image_to_ansi_chafa(filename, size, halfblocks, fill)
    else:
        return image_to_ansi_basic(filename, size, halfblocks, fill)


def grouping(iterable, n):
    assert n > 0

    iterable = iter(iterable)
    no_value = object()
    while True:
        group = tuple(next(iterable, no_value) for _ in range(n))
        if group[0] is no_value:
            break
        group = tuple(e for e in group if e is not no_value)
        yield group


def wrap_at(name, wrap_len):
    if len(name) <= wrap_len:
        return name
    return '\n'.join(''.join(block) for block in grouping(name, wrap_len))


def make_files_table(
    files,
    icon_columns=1, name_side=True, iconsize=32, iso_size=False,
    wrap_names=False,
    has_chafa=False,
):
    term_size = get_terminal_size()
    nb_columns = icon_columns
    if name_side:
        nb_columns *= 2
    # 4: 2 borders + 2 padding
    wrap_max = term_size.columns // nb_columns - 4

    table = PrettyTable()
    table.set_style(SINGLE_BORDER)

    empty_icon = ''
    if iso_size:
        empty_icon = '\n'.join(
            '\u2591' * iconsize
            for _ in range(iconsize // 2)
        )

    for paths in grouping(files, icon_columns):
        thumbs = [
            empty_icon
            if not files[path]
            else image_to_ansi(
                files[path], (iconsize, iconsize), fill=iso_size,
                has_chafa=has_chafa,
            )
            for path in paths
        ]
        names = [path.name for path in paths]
        if wrap_names:
            names = [wrap_at(name, wrap_max) for name in names]

        assert len(thumbs) == len(names)

        thumbs.extend('' for _ in range(-len(names) % icon_columns))
        names.extend('' for _ in range(-len(names) % icon_columns))
        if name_side:
            table.add_row(sum(zip(thumbs, names), ()))
        else:
            table.add_row(list(thumbs))
            table.add_row(names)

    return table


def set_style(table):
    table.hrules = ALL
    table.header = False
    table.vrules = False
    table.align = 'l'


def _default_sort(path):
    # dirs first, lower-alphabetic then
    return (not path.is_dir(), path.name.lower())


def sort_size(path):
    return path.lstat().st_size


def sort_mtime(path):
    return path.lstat().st_mtime


sort_functions = {
    "default": _default_sort,
    "size": sort_size,
    "mtime": sort_mtime,
}


def sort_files(files, key=_default_sort):
    return {
        path: files[path]
        for path in sorted(files, key=key)
    }


def main():
    parser = ArgumentParser()
    parser.add_argument('path', type=Path, nargs='*')
    parser.add_argument('--icon-columns', type=int, default=1)
    parser.add_argument('--icon-size', type=int, default=32)
    parser.add_argument('-b', '--name-below-icon', action='store_true')
    parser.add_argument('-u', '--uniform-icon-size', action='store_true')
    parser.add_argument('-w', '--wrap-names', action='store_true')
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument(
        "--sort", choices=["default", "mtime", "size"],
        default="default",
    )
    args = parser.parse_args()

    if not args.path:
        args.path = [Path.cwd()]

    args.has_chafa = bool(which('chafa'))

    for path in args.path:
        if len(args.path) > 1:
            print(f"{path}:")
        process_path(path, args)


def process_path(path, args):
    files = get_list_and_thumbs(path)
    files = sort_files(files, sort_functions[args.sort])
    if args.reverse:
        files = dict(reversed(files.items()))

    table = make_files_table(
        files,
        icon_columns=args.icon_columns,
        iconsize=args.icon_size,
        name_side=not args.name_below_icon,
        iso_size=args.uniform_icon_size,
        wrap_names=args.wrap_names,
        has_chafa=args.has_chafa,
    )
    set_style(table)
    print(table)


if __name__ == '__main__':
    main()
