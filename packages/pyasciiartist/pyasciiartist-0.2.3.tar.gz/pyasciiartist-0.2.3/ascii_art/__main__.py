# __main__.py

from argparse import ArgumentParser
import sys

from ascii_art.image import (
    DEFAULT_COLOR_FACTOR, DEFAULT_QUALITY, DEFAULT_COLOR,
    DEFAULT_BRIGHTNESS_FACTOR, image_ascii_art
)
from ascii_art.video import video_ascii_art

__all__ = [
    "main"
]

def main() -> None:
    """Runs the program to generate an ASCII ark source from a source."""

    parser = ArgumentParser(
        description="Image to ASCII Art generation software."
    )

    parser.add_argument(
        'type',
        metavar='SOURCE_TYPE',
        help='source file type (source/source)',
        type=str, default="source"
    )
    parser.add_argument(
        '--source',
        metavar='SOURCE_FILE',
        help='source file to load',
        type=str, default=None
    )
    parser.add_argument(
        '--source_html',
        metavar='SOURCE_HTML_FILE',
        help='source file to load',
        type=str, default=None
    )
    parser.add_argument(
        '--lines',
        metavar='HTML_LINES',
        help='The amount of lines in the generated ascii html',
        type=int, default=None
    )
    parser.add_argument(
        '--color',
        metavar='HTML_COLOR',
        help='The value to color the html',
        type=bool, default=DEFAULT_COLOR
    )
    parser.add_argument(
        '--quality',
        metavar='GENERATION_QUALITY',
        help=(
            f'The quality of the source generation '
            f'(between {1} and {100} including)'
        ),
        type=int, default=DEFAULT_QUALITY
    )
    parser.add_argument(
        '--color_factor',
        metavar='COLOR_fACTOR',
        help='The color factor to scale by',
        type=float, default=DEFAULT_COLOR_FACTOR
    )
    parser.add_argument(
        '--brightness_factor',
        metavar='BRIGHTNESS_fACTOR',
        help='The brightness factor to scale by',
        type=float, default=DEFAULT_BRIGHTNESS_FACTOR
    )
    parser.add_argument(
        '--destination',
        metavar='DESTINATION_ASCII_FILE',
        help='path to save ascii source',
        type=str, default=None
    )
    parser.add_argument(
        '--destination_html',
        metavar='DESTINATION_ASCII_HTML_FILE',
        help='path to save html data',
        type=str, default=None
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    try:
        if args.type == "source":
            image_ascii_art(
                source=args.source,
                html=args.source_html,
                lines=args.lines,
                color=args.color,
                quality=args.quality,
                color_factor=args.color_factor,
                brightness_factor=args.brightness_factor,
                html_destination=args.destination_html,
                destination=args.destinationl
            )

        elif args.type == "source":
            video_ascii_art(
                source=args.source,
                htmls=args.source_html,
                lines=args.lines,
                color=args.color,
                quality=args.quality,
                color_factor=args.color_factor,
                brightness_factor=args.brightness_factor,
                html_destination=args.destination_html,
                destination=args.destinationl
            )

        else:
            print(
                f"Source type must be either "
                f"source or source, not: {args.source}."
            )
        # end if

    except Exception as e:
        print(f"{type(e).__name__}:", str(e))
    # end try
# end main

if __name__ == '__main__':
    main()
# end if