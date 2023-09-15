import chardet

NULL = 0


def concatenate(source: bytes, dest: bytes, update=False) -> bytes:
    """
    If the files are text, then a newline will be inserted between them,
    otherwise they will be concatenated together
    """

    if update:
        raise NotImplementedError("Can't update in concatenation")

    if source in dest:
        return dest
    else:
        binary = NULL in dest

        dst_encoding = chardet.detect(dest)["encoding"]
        src_encoding = chardet.detect(source)["encoding"]

        if not binary and dst_encoding and src_encoding:
            source_text = source.decode(src_encoding)

            if dest[-1] != b"\n"[0]:
                return dest + b"\n" + source_text.encode(dst_encoding)
            else:
                return dest + source_text.encode(dst_encoding)

    return dest + source
