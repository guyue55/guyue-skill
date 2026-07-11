#!/usr/bin/env python3
"""Render the root showcase GIF without external services."""

from __future__ import annotations

import os
import shutil
import struct
import subprocess
import sys
import tempfile


WIDTH = 720
HEIGHT = 404
FRAME_DELAY = 90

PALETTE = [
    (12, 16, 28),    # 0 background
    (28, 34, 52),    # 1 panel
    (72, 202, 228),  # 2 cyan
    (255, 203, 90),  # 3 yellow
    (79, 222, 140),  # 4 green
    (255, 107, 107), # 5 red
    (245, 247, 250), # 6 white
    (131, 148, 173), # 7 muted
]

FONT = {
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "11100"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def default_output() -> str:
    return os.path.join(repo_root(), "assets", "demo.gif")


def rect(buffer: bytearray, x: int, y: int, w: int, h: int, color: int) -> None:
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    for row in range(y0, y1):
        start = row * WIDTH + x0
        buffer[start : start + (x1 - x0)] = bytes([color]) * (x1 - x0)


def draw_text(buffer: bytearray, x: int, y: int, text: str, color: int, scale: int = 3) -> None:
    cursor = x
    for char in text.upper():
        glyph = FONT.get(char, FONT[" "])
        for row, line in enumerate(glyph):
            for col, bit in enumerate(line):
                if bit == "1":
                    rect(buffer, cursor + col * scale, y + row * scale, scale, scale, color)
        cursor += 6 * scale


def draw_step(buffer: bytearray, index: int, label: str, active: bool, done: bool) -> None:
    x = 56 + index * 158
    color = 4 if done else 2 if active else 7
    rect(buffer, x, 178, 128, 64, 1)
    rect(buffer, x, 178, 128, 4, color)
    rect(buffer, x, 238, 128, 4, color)
    rect(buffer, x, 178, 4, 64, color)
    rect(buffer, x + 124, 178, 4, 64, color)
    draw_text(buffer, x + 18, 202, label, color, 2)


def make_frame(active_index: int, caption: str) -> bytes:
    buffer = bytearray([0] * (WIDTH * HEIGHT))
    rect(buffer, 34, 36, 652, 332, 1)
    rect(buffer, 34, 36, 652, 8, 2)
    rect(buffer, 34, 360, 652, 8, 2)
    rect(buffer, 42, 54, 12, 12, 5)
    rect(buffer, 62, 54, 12, 12, 3)
    rect(buffer, 82, 54, 12, 12, 4)

    draw_text(buffer, 116, 54, "GUYUE SHOWCASE", 6, 3)
    draw_text(buffer, 118, 94, "INPUT  ROUTE  BOUND  PROVE", 7, 2)

    labels = ["INPUT", "ROUTE", "BOUND", "PROVE"]
    for index, label in enumerate(labels):
        draw_step(buffer, index, label, active_index == index, active_index > index)

    for index in range(3):
        x = 184 + index * 158
        rect(buffer, x, 208, 30, 4, 7)
        rect(buffer, x + 30, 208, 30 if active_index > index else 0, 4, 4)

    rect(buffer, 64, 278, 592, 52, 0)
    rect(buffer, 64, 278, 592, 4, 2)
    draw_text(buffer, 90, 296, caption, 6, 2)

    progress_width = 148 * (active_index + 1)
    rect(buffer, 64, 344, 592, 8, 7)
    rect(buffer, 64, 344, progress_width, 8, 4)
    return bytes(buffer)


def make_frames() -> list[bytes]:
    return [
        make_frame(0, "READ INTENT AND BOUNDARY"),
        make_frame(1, "EXPLAIN ROUTE EVIDENCE"),
        make_frame(2, "KEEP PROJECT GATES CLOSED"),
        make_frame(3, "PROVE WITHOUT SIDE EFFECTS"),
    ]


def load_pillow():
    try:
        from PIL import Image
    except Exception:
        return None
    return Image


def flattened_palette() -> list[int]:
    values: list[int] = []
    for rgb in PALETTE:
        values.extend(rgb)
    values.extend([0] * (768 - len(values)))
    return values


def bit_packer():
    output = bytearray()
    current = 0
    bits = 0

    def write(code: int, size: int) -> None:
        nonlocal current, bits
        current |= code << bits
        bits += size
        while bits >= 8:
            output.append(current & 0xFF)
            current >>= 8
            bits -= 8

    def finish() -> bytes:
        if bits:
            output.append(current & 0xFF)
        return bytes(output)

    return write, finish


def lzw_encode(indices: bytes, min_code_size: int = 3) -> bytes:
    clear = 1 << min_code_size
    end = clear + 1

    def reset_dictionary():
        dictionary = {(i,): i for i in range(clear)}
        return dictionary, end + 1, min_code_size + 1

    dictionary, next_code, code_size = reset_dictionary()
    write, finish = bit_packer()
    write(clear, code_size)

    w: tuple[int, ...] = ()
    for value in indices:
        wk = w + (value,)
        if wk in dictionary:
            w = wk
            continue

        write(dictionary[w], code_size)
        if next_code < 4096:
            dictionary[wk] = next_code
            next_code += 1
            if next_code == (1 << code_size) and code_size < 12:
                code_size += 1
        else:
            write(clear, code_size)
            dictionary, next_code, code_size = reset_dictionary()
        w = (value,)

    if w:
        write(dictionary[w], code_size)
    write(end, code_size)
    return finish()


def write_sub_blocks(handle, data: bytes) -> None:
    for index in range(0, len(data), 255):
        chunk = data[index : index + 255]
        handle.write(bytes([len(chunk)]))
        handle.write(chunk)
    handle.write(b"\x00")


def render_with_builtin_gif(output_path: str, frames: list[bytes]) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as handle:
        handle.write(b"GIF89a")
        handle.write(struct.pack("<HH", WIDTH, HEIGHT))
        handle.write(bytes([0b11110010, 0, 0]))
        for rgb in PALETTE:
            handle.write(bytes(rgb))
        handle.write(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

        for frame in frames:
            handle.write(b"\x21\xF9\x04\x04")
            handle.write(struct.pack("<H", FRAME_DELAY))
            handle.write(b"\x00\x00")
            handle.write(b"\x2C")
            handle.write(struct.pack("<HHHH", 0, 0, WIDTH, HEIGHT))
            handle.write(b"\x00")
            handle.write(b"\x03")
            write_sub_blocks(handle, lzw_encode(frame, 3))
        handle.write(b"\x3B")


def render_with_pillow(output_path: str, frames: list[bytes]) -> bool:
    Image = load_pillow()
    if Image is None:
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    images = []
    palette = flattened_palette()
    for frame in frames:
        image = Image.frombytes("P", (WIDTH, HEIGHT), frame)
        image.putpalette(palette)
        images.append(image)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=FRAME_DELAY * 10,
        loop=0,
        disposal=2,
        optimize=False,
    )
    return True


def render_with_ffmpeg(output_path: str, frames: list[bytes]) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        for index, frame in enumerate(frames):
            ppm_path = os.path.join(tmp_dir, f"frame_{index:03d}.ppm")
            with open(ppm_path, "wb") as handle:
                handle.write(f"P6\n{WIDTH} {HEIGHT}\n255\n".encode("ascii"))
                rgb = bytearray()
                for value in frame:
                    rgb.extend(PALETTE[value])
                handle.write(bytes(rgb))

        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-framerate",
                f"{100 / FRAME_DELAY:.6f}",
                "-i",
                os.path.join(tmp_dir, "frame_%03d.ppm"),
                "-loop",
                "0",
                output_path,
            ],
            check=True,
        )
    return True


def render(output_path: str) -> None:
    frames = make_frames()
    if render_with_pillow(output_path, frames):
        return
    if render_with_ffmpeg(output_path, frames):
        return
    render_with_builtin_gif(output_path, frames)


def check(output_path: str) -> bool:
    if not os.path.exists(output_path):
        print(f"missing showcase GIF: {output_path}", file=sys.stderr)
        return False
    with open(output_path, "rb") as handle:
        data = handle.read()
    header = data[:6]
    if header not in {b"GIF87a", b"GIF89a"}:
        print(f"invalid GIF header: {output_path}", file=sys.stderr)
        return False
    if len(data) < 10:
        print(f"truncated showcase GIF: {output_path}", file=sys.stderr)
        return False
    width, height = struct.unpack("<HH", data[6:10])
    if (width, height) != (WIDTH, HEIGHT):
        print(
            f"unexpected GIF dimensions: {width}x{height}, expected {WIDTH}x{HEIGHT}",
            file=sys.stderr,
        )
        return False
    if os.path.getsize(output_path) < 1024:
        print(f"showcase GIF is unexpectedly small: {output_path}", file=sys.stderr)
        return False

    Image = load_pillow()
    if Image is not None:
        try:
            image = Image.open(output_path)
            frame_count = getattr(image, "n_frames", 1)
            if frame_count != len(make_frames()):
                print(
                    f"unexpected GIF frame count: {frame_count}, expected {len(make_frames())}",
                    file=sys.stderr,
                )
                return False
            frame_pixels: set[bytes] = set()
            for index in range(frame_count):
                image.seek(index)
                image.load()
                rgb = image.convert("RGB")
                colors = rgb.getcolors(maxcolors=WIDTH * HEIGHT) or []
                if len(colors) < 6:
                    print(f"showcase GIF frame {index} is visually sparse", file=sys.stderr)
                    return False
                frame_pixels.add(rgb.tobytes())
            if len(frame_pixels) != frame_count:
                print("showcase GIF contains duplicate frames", file=sys.stderr)
                return False
        except Exception as exc:
            print(f"GIF decode failed: {exc}", file=sys.stderr)
            return False
        return True

    frame_count = data.count(b"\x21\xF9\x04")
    if frame_count != len(make_frames()):
        print(
            f"unexpected GIF frame markers: {frame_count}, expected {len(make_frames())}",
            file=sys.stderr,
        )
        return False

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        result = subprocess.run(
            [ffmpeg, "-v", "error", "-i", output_path, "-f", "null", "-"],
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            print(f"GIF decode failed: {result.stderr.strip()}", file=sys.stderr)
            return False
    return True


def main() -> int:
    output_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--output" else default_output()
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        return 0 if check(output_path) else 1
    render(output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
