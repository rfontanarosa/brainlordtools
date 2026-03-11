import argparse
import sys
from dataclasses import dataclass
from typing import BinaryIO, Iterable, List, Optional

COMPRESSION_TYPES = {
    0: 0x1F,
    1: 0x0F,
    2: 0x07,
    3: 0x03,
    4: 0x01,
    5: 0x00,
}

COMPRESSION_KEYS = {value: key for key, value in COMPRESSION_TYPES.items()}


@dataclass
class CLIOptions:
    input_path: str
    output_path: str
    base_offset: int
    compress: bool
    compression_type: Optional[int]
    compression_key: Optional[int]


def parse_args(arguments: List[str]) -> CLIOptions:
    parser = argparse.ArgumentParser(
        prog="decomp.py",
        description="Secret of Mana graphic decompressor/compressor.",
    )
    parser.add_argument("input_path", help="Input file path.")
    parser.add_argument("output_path", help="Output file path.")
    parser.add_argument(
        "--base-offset",
        type=lambda value: int(value, 16),
        default=0,
        help="Optional base offset to seek to before decompression (default: 0).",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress the input file instead of decompressing.",
    )
    parser.add_argument(
        "--compression-type",
        type=lambda value: int(value, 0),
        help="Compression mask to use when compressing (e.g. 0x03).",
    )
    parser.add_argument(
        "--compression-key",
        type=lambda value: int(value, 0),
        help="Compression header key to use when compressing (0-5).",
    )

    args = parser.parse_args(arguments[1:])

    if args.base_offset < 0:
        parser.error("--base-offset must be non-negative.")

    if args.compress and args.base_offset:
        parser.error("--base-offset is only valid when decompressing.")

    return CLIOptions(
        input_path=args.input_path,
        output_path=args.output_path,
        base_offset=args.base_offset,
        compress=args.compress,
        compression_type=args.compression_type,
        compression_key=args.compression_key,
    )


def read_compression_header(handle: BinaryIO) -> tuple[int, int]:
    header = handle.read(2)
    if len(header) != 2:
        raise ValueError("Missing compression type header.")

    compression_key = header[1] << 8 | header[0]
    if compression_key not in COMPRESSION_TYPES:
        raise ValueError(f"Unsupported compression type: {compression_key}")

    size_bytes = handle.read(2)
    if len(size_bytes) != 2:
        raise ValueError("Missing uncompressed size header.")

    uncompressed_size = size_bytes[0] << 8 | size_bytes[1]

    return COMPRESSION_TYPES[compression_key], uncompressed_size


def decompress(
    compressed_data: Iterable[int], compression_type: int, uncompressed_size: int
) -> bytes:
    data = list(compressed_data)
    output = bytearray()
    index = 0

    while index < len(data) and len(output) < uncompressed_size:
        byte = data[index]

        if byte < 0x80:
            length = byte + 1
            start = index + 1
            chunk = data[start : start + length]
            remaining = uncompressed_size - len(output)
            output.extend(chunk[:remaining])
            index = start + length
        else:
            if index + 1 >= len(data):
                break

            displacement = (((byte - 0x80) & compression_type) * 0x100) + (
                data[index + 1] + 1
            )
            read_from = len(output) - displacement
            read_length = ((byte - 0x80) // (compression_type + 1)) + 3

            for _ in range(read_length):
                if len(output) >= uncompressed_size:
                    break

                if 0 <= read_from < len(output):
                    value = output[read_from]
                else:
                    value = 0

                output.append(value)
                read_from += 1

            index += 2

    return bytes(output)


def compress(uncompressed: bytes, compression_type: int) -> bytes:
    if compression_type not in COMPRESSION_KEYS:
        raise ValueError(f"Unsupported compression type: {compression_type}")

    mask = compression_type
    divisor = mask + 1
    max_match_length = (127 // divisor) + 3
    max_offset = 0x100 * divisor
    data = bytes(uncompressed)
    length = len(data)
    max_literal = 0x80

    best_cost = [float("inf")] * (length + 1)
    choice: List[tuple[str, int, Optional[int]]] = [("", 0, None)] * (length + 1)
    best_cost[length] = 0
    choice[length] = ("end", 0, None)

    for index in range(length - 1, -1, -1):
        remaining = length - index
        max_literal_len = min(max_literal, remaining)

        for literal_len in range(max_literal_len, 0, -1):
            cost = 1 + literal_len + best_cost[index + literal_len]
            if cost < best_cost[index]:
                best_cost[index] = cost
                choice[index] = ("lit", literal_len, None)

        window_start = max(0, index - max_offset)
        max_search = min(max_match_length, remaining)

        for candidate in range(index - 1, window_start - 1, -1):
            offset = index - candidate
            high = (offset - 1) // 0x100
            if high > mask:
                continue

            match_len = 0
            while (
                match_len < max_search
                and data[candidate + match_len] == data[index + match_len]
            ):
                match_len += 1
                if match_len < 3:
                    continue

                length_code = match_len - 3
                token_val = 0x80 + length_code * divisor + high
                if token_val > 0xFF:
                    break

                cost = 2 + best_cost[index + match_len]
                if cost < best_cost[index]:
                    best_cost[index] = cost
                    choice[index] = ("match", match_len, offset)

    if best_cost[0] == float("inf"):
        raise ValueError("Unable to compress input with the given parameters.")

    payload = bytearray()
    index = 0

    while index < length:
        action, value, extra = choice[index]
        if action == "lit":
            literal_len = value
            payload.append(literal_len - 1)
            payload.extend(data[index : index + literal_len])
            index += literal_len
        elif action == "match":
            match_len = value
            offset = extra if extra is not None else 0
            length_code = match_len - 3
            high = (offset - 1) // 0x100
            low = (offset - 1) & 0xFF
            token = 0x80 + length_code * divisor + high
            payload.append(token)
            payload.append(low)
            index += match_len
        else:
            raise ValueError(f"Unexpected action {action!r} during reconstruction.")

    return bytes(payload)


def resolve_compression_values(options: CLIOptions) -> tuple[int, int]:
    mask = options.compression_type
    key = options.compression_key

    if mask is not None and mask not in COMPRESSION_KEYS:
        supported = ", ".join(hex(value) for value in sorted(COMPRESSION_KEYS))
        raise ValueError(
            f"Unsupported compression mask: {hex(mask)}. "
            f"Supported masks: {supported}."
        )

    if key is not None and key not in COMPRESSION_TYPES:
        supported = ", ".join(str(value) for value in sorted(COMPRESSION_TYPES))
        raise ValueError(
            f"Unsupported compression key: {key}. Supported keys: {supported}."
        )

    if mask is None and key is None:
        raise ValueError(
            "Compression requires --compression-type or --compression-key."
        )

    if mask is None and key is not None:
        mask = COMPRESSION_TYPES[key]

    if key is None and mask is not None:
        key = COMPRESSION_KEYS[mask]

    if mask is None or key is None:
        raise ValueError("Unable to resolve compression parameters.")

    expected_key = COMPRESSION_KEYS[mask]
    if key != expected_key:
        raise ValueError(
            f"Compression key {key} does not match mask {hex(mask)} "
            f"(expected key {expected_key})."
        )

    return mask, key


def main() -> int:
    try:
        options = parse_args(sys.argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    try:
        if options.compress:
            mask, key = resolve_compression_values(options)

            with open(options.input_path, "rb") as source:
                uncompressed = source.read()

            if len(uncompressed) > 0xFFFF:
                raise ValueError(
                    "Uncompressed size exceeds 65535 bytes, which cannot be encoded."
                )

            payload = compress(uncompressed, mask)
            header = bytes(
                [
                    key & 0xFF,
                    (key >> 8) & 0xFF,
                    (len(uncompressed) >> 8) & 0xFF,
                    len(uncompressed) & 0xFF,
                ]
            )

            with open(options.output_path, "wb") as target:
                target.write(header + payload)
        else:
            with open(options.input_path, "rb") as source:
                if options.base_offset > 0:
                    source.seek(options.base_offset)

                compression_type, uncompressed_size = read_compression_header(source)
                compressed_payload = source.read()

            result = decompress(
                compressed_payload, compression_type, uncompressed_size
            )

            with open(options.output_path, "wb") as target:
                target.write(result)
    except ValueError as exc:
        print(exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
