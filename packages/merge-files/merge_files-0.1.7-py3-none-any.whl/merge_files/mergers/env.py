def env(source: bytes, dest: bytes, update=False) -> bytes:
    """
    Merge two env files together
    """
    # this is a bit hairy, need to refactor

    source_lines = source.decode().splitlines()
    dest_lines = dest.decode().splitlines()

    source_vars = dict(
        line.split("=", maxsplit=1) for line in source_lines if "=" in line
    )

    output = []
    used = set()

    for line in dest_lines:
        # If the line is a comment, just add it to the output
        if "=" not in line:
            output.append(line)
            if line in source_lines:
                used.add(line)
            continue

        var = line.split("=")[0]

        # If the variable is in the source file, add it to the output
        if var in source_vars:
            if update:
                output.append(f"{var}={source_vars[var]}")
            else:
                output.append(line)

            del source_vars[var]
            used.add(var)
            continue

        # If the variable is not in the source file, add it to the output
        output.append(line)

    # Add any lines that were not in the destination file
    for line in source_lines:
        if "=" in line:
            var = line.split("=", maxsplit=1)[0]
            if var not in used:
                output.append(line)
        else:
            if line not in used:
                output.append(line)

    return "\n".join(output).encode()
