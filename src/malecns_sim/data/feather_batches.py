"""Experimental bounded Feather V2 access, with metadata-only size admission."""
from contextlib import contextmanager
from pathlib import Path
import struct

EDGE_COLUMNS = ("body_pre", "body_post", "weight")
DEFAULT_BATCH_ROWS = 65536


def _field(data, table, index):
    vtable = table - struct.unpack_from("<i", data, table)[0]
    length = struct.unpack_from("<H", data, vtable)[0]
    offset = 4 + 2 * index
    return table + struct.unpack_from("<H", data, vtable + offset)[0] if offset < length else table


def feather_layout(path):
    """Read only footer and message metadata; never read record-batch bodies."""
    with Path(path).open("rb") as stream:
        if stream.read(6) != b"ARROW1":
            raise ValueError("bounded access requires Feather V2 / Arrow IPC file")
        stream.seek(-10, 2)
        tail = stream.read(10)
        if tail[4:] != b"ARROW1":
            raise ValueError("invalid Arrow IPC footer")
        size = struct.unpack_from("<I", tail)[0]
        stream.seek(-10 - size, 2)
        footer = stream.read(size)
        root = struct.unpack_from("<I", footer)[0]
        field = _field(footer, root, 3)
        vector = field + struct.unpack_from("<I", footer, field)[0]
        count = struct.unpack_from("<I", footer, vector)[0]
        rows = []
        codecs = set()
        for index in range(count):
            offset, metadata_size, body_size = struct.unpack_from("<qi4xq", footer, vector + 4 + index * 24)
            stream.seek(offset)
            metadata = stream.read(metadata_size)
            prefix = 8 if metadata[:4] == b"\xff\xff\xff\xff" else 4
            message = metadata[prefix:]
            table = struct.unpack_from("<I", message)[0]
            header_field = _field(message, table, 2)
            header = header_field + struct.unpack_from("<I", message, header_field)[0]
            rows.append(struct.unpack_from("<q", message, _field(message, header, 0))[0])
            compression_field = _field(message, header, 3)
            if compression_field == header or not struct.unpack_from("<I", message, compression_field)[0]:
                codecs.add("uncompressed")
            else:
                compression = compression_field + struct.unpack_from("<I", message, compression_field)[0]
                codec_field = _field(message, compression, 0)
                codec = 0 if codec_field == compression else message[codec_field]
                codecs.add({0: "LZ4_FRAME", 1: "ZSTD"}.get(codec, "unknown"))
        return {"format": "Feather V2 / Arrow IPC", "physical_rows": rows,
                "physical_batches": count, "compression": sorted(codecs),
                "ipc_metadata_version": struct.unpack_from("<h", footer, _field(footer, root, 0))[0] + 1}


@contextmanager
def edge_batches(path, columns=EDGE_COLUMNS, max_rows_per_batch=DEFAULT_BATCH_ROWS):
    """Yield projected batches in file order; close even on interrupted iteration.

    Admission rejects physical batches above the limit before payload access.
    Slicing a larger physical batch would not bound decompression ownership.
    Consumers must release their previous batch before requesting the next.
    """
    import pyarrow as pa
    import pyarrow.ipc as ipc
    if max_rows_per_batch <= 0 or len(columns) != 3 or len(set(columns)) != 3:
        raise ValueError("three distinct columns and a positive batch limit required")
    layout = feather_layout(path)
    if max(layout["physical_rows"], default=0) > max_rows_per_batch:
        raise ValueError("physical record batch exceeds bounded admission limit")
    with pa.OSFile(str(path), "rb") as source:
        schema = ipc.open_file(source).schema
        indices = [schema.get_field_index(name) for name in columns]
        if min(indices) < 0:
            raise ValueError("required configured column is missing")
        for name in columns:
            if not pa.types.is_integer(schema.field(name).type):
                raise ValueError(f"configured integer column is not an integer: {name!r}")
        reader = ipc.open_file(source, options=ipc.IpcReadOptions(included_fields=indices, use_threads=False))
        def iterate():
            for index in range(reader.num_record_batches):
                batch = reader.get_batch(index)
                yield pa.Table.from_batches([batch]).select(list(columns))
                del batch
        iterator = iterate()
        try:
            yield iterator
        finally:
            iterator.close()
            del reader
