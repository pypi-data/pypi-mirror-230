# gfxls

List files in command-line, with thumbnails.

![gfxls in xterm names on side](shots/side.png)

![gfxls in xterm names below and columns](shots/columns.png)

## Synopsis

	gfxls [--icon-columns COLS] [--icon-size SIZE] [--name-below-icon] [--uniform-icon-size] [path]

## Thumbnails

Thumbnails are supported for a wide range of file formats, with images and
videos, thanks to [vignette](https://pypi.org/project/vignette/).
They follow the FreeDesktop standard and so are reused between different apps.

## Terminal

Thumbnails are shown in 24 bits colors ("truecolor") and Unicode characters.

## Chafa

If [chafa](https://hpjansson.org/chafa/) is installed, it will be used for better image quality rendering.
Note that `--uniform-icon-size` does not work with chafa for now.

## Dependencies

- Python 3.7 at least
- [vignette](https://pypi.org/project/vignette/)
- [python-prettytable](https://pypi.org/project/prettytable/)
- [python-pillow](https://pypi.org/project/Pillow/)
- a truecolor-capable terminal
- optionally, [chafa](https://hpjansson.org/chafa/)
