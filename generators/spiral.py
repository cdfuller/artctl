"""Sample spiral generator writing a placeholder PNG image."""

import argparse
import base64

PLACEHOLDER_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAOklEQVR4nO3BAQEAAACCIP+vbkcKBQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AADwGgAB9gABNDBthQAAAABJRU5ErkJggg=="
)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a sample spiral PNG.")
    parser.add_argument("--output", required=True, help="Output file path.")
    parser.add_argument("--turns", type=int, default=20, help="Number of turns.")
    parser.add_argument("--radius", type=int, default=400, help="Radius value.")
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.output, "wb") as handle:
        handle.write(PLACEHOLDER_PNG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
