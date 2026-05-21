def binary_search_cursor(text: str, relative_x: float, paint) -> int:
    """Binary search for the character index closest to relative_x."""
    if not text:
        return 0
    n = len(text)
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        width = paint.measure_text(text[:mid + 1])[0]
        if width < relative_x:
            lo = mid + 1
        else:
            hi = mid
    if lo == 0:
        width_at_lo = paint.measure_text(text[:1])[0]
        return 0 if relative_x < width_at_lo / 2 else 1
    if lo >= n:
        width_at_prev = paint.measure_text(text[:n])[0]
        return n if relative_x >= width_at_prev / 2 else n - 1
    width_before = paint.measure_text(text[:lo])[0]
    width_after = paint.measure_text(text[:lo + 1])[0]
    return lo if abs(relative_x - width_before) <= abs(relative_x - width_after) else lo + 1


def wrap_lines(text, max_width, measure_text):
    """Wrap text into visual lines that fit within max_width.
    Returns list of (line_text, start_index) tuples where start_index
    is the character offset in the original text.

    Falls back to character-level breaking when a single word exceeds
    max_width — otherwise long unbreakable tokens (file paths, URLs)
    would render past their container and overlap siblings."""
    raw_lines = text.split("\n")
    wrapped = []
    abs_pos = 0

    def split_long_word(word, start_pos):
        """Greedily slice `word` into prefixes that each fit in max_width.
        Returns (finished_chunks, tail_chunk) where finished_chunks are
        completed lines and tail_chunk is the remainder that still fits."""
        finished = []
        remaining = word
        cur_pos = start_pos
        while remaining and measure_text(remaining)[0] > max_width:
            lo, hi, best = 1, len(remaining), 1
            while lo <= hi:
                mid = (lo + hi) // 2
                if measure_text(remaining[:mid])[0] <= max_width:
                    best = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            finished.append((remaining[:best], cur_pos))
            cur_pos += best
            remaining = remaining[best:]
        return finished, (remaining, cur_pos)

    for raw_line in raw_lines:
        if not raw_line:
            wrapped.append(("", abs_pos))
            abs_pos += 1  # skip past \n
            continue

        words = raw_line.split(" ")
        buf = []
        buf_start = abs_pos

        for word in words:
            candidate = " ".join(buf + [word])
            width = measure_text(candidate)[0]

            if buf and width > max_width:
                wrapped.append((" ".join(buf), buf_start))
                buf_start = abs_pos
                buf = [word]
            else:
                buf.append(word)

            # If buf is now a single word that still overflows, fall back
            # to character-level breaking so it doesn't render past the
            # container. Multi-word bufs are skipped — they were already
            # composed from words that individually fit.
            if len(buf) == 1 and measure_text(buf[0])[0] > max_width:
                finished, (tail_text, tail_start) = split_long_word(buf[0], buf_start)
                wrapped.extend(finished)
                buf = [tail_text] if tail_text else []
                buf_start = tail_start

            abs_pos += len(word) + 1

        if buf:
            wrapped.append((" ".join(buf), buf_start))

    return wrapped
