"""Serialisation helpers."""
from enum import Enum
from io import BytesIO
import struct

from numpy.typing import NDArray


class TextureFormat(Enum):
    """Container for unity texture format types."""

    ARGB32 = 5  # Color with alpha texture format, 8-bits per channel.
    RG16 = 62   # Two color (RG) texture format, 8-bits per channel.
    R8 = 63     # Single channel (R) texture format, 8 bit integer.


def volume_to_bytes(data: NDArray) -> bytes:
    """
    Write a 3D array of ColorLA to bytes.

    Parameters
    ----------
    data : NDArray
        3D array of ColorLA objects

    Returns
    -------
    bytes
        Serialised 3D volume
    """
    volume_header_text = "EarthwaveVolume"
    format_version = 1

    z_size = data.shape[0]  # python z, unity y
    y_size = data.shape[1]   # python y, unity z
    x_size = data.shape[2]   # python x, unity x

    with BytesIO() as writer:

        # Fixed text (asci characters)
        _write_header(writer, volume_header_text, format_version)
        _write_int(writer, TextureFormat.RG16.value)
        _write_int(writer, x_size)
        _write_int(writer, y_size)
        _write_int(writer, z_size)

        for z in range(z_size):
            for y in range(y_size):
                for x in range(x_size):
                    color = data[z, y, x]
                    _write_char(writer, int(color.value))
                    _write_char(writer, color.alpha)

        writer.seek(0)
        return writer.read()


def _write_char(writer: BytesIO, char: str) -> None:
    writer.write(struct.pack('B', char))


def _write_str(writer: BytesIO, text: str) -> None:
    writer.write(struct.pack(f'{len(text)}s', text.encode('ascii')))


def _write_int(writer: BytesIO, number: int) -> None:
    """
    Write an int as bytes.

    Parameters
    ----------
    writer : BytesIO
        Writer instance.
    number : int
        Number to write.
    """
    writer.write(struct.pack('i', number))


def _write_header(writer: BytesIO, header: str, version: int) -> None:
    """
    Write a header to bytes.

    Parameters
    ----------
    writer : BytesIO
        Writer instance.
    header : str
        Text name of the binary object.
    version : int
        Version of the binary encoding.
    """
    _write_int(writer, len(header))
    _write_str(writer, header)
    _write_int(writer, version)
