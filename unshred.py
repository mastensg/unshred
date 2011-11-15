#!/usr/bin/env python

import Image

def unshred(image):
    w, h = image.size

    # Calculate difference between adjacent 1-pixel-wide columns.
    coldiff = []
    for x in range(w - 1):
        diffs = []
        for y in range(h):
            l = sum(image.getpixel((x, y))[:3])
            r = sum(image.getpixel((x + 1, y))[:3])
            diffs.append(abs(r - l))

        coldiff.append(sum(diffs))

    # Calculate column width.
    cumdiffs = {}
    for cw in range(3, w / 2 + 1):
        if w % cw:
            continue

        diffs = []
        for i in range(0, w - 1, cw):
            diffs.append(coldiff[i - 1])

        cumdiffs[cw] = sum(diffs) / len(diffs)

    best = 0
    for cw in cumdiffs:
        if cumdiffs[cw] > best:
            best = cumdiffs[cw]
            best_cw = cw

    cw = best_cw

    # Split image into columns.
    columns = [image.crop((x, 0, x + cw, h)) for x in range(0, w, cw)]

    # Calculate averages of edge pixels for each row in each column.
    colsavgs = []
    for col in columns:
        colavgs = []
        for y in range(h):
            lavg = sum(col.getpixel((0, y))[:3]) / 3.
            ravg = sum(col.getpixel((cw - 1, y))[:3]) / 3.
            colavgs.append((lavg, ravg))

        colsavgs.append(colavgs)

    # Calculate difference between edges.
    cumdiff = {}
    for lcol in range(len(columns)):
        for rcol in range(len(columns)):
            diffs = []
            for y in range(h):
                diffs.append(abs(colsavgs[rcol][y][0] - colsavgs[lcol][y][1]))

            cumdiff[(lcol, rcol)] = sum(diffs)

    # Find pairs of edges with least difference.
    pairs = {}
    for lcol in range(len(columns)):
        best = lcol

        for rcol in range(len(columns)):
            if cumdiff[(lcol, rcol)] < cumdiff[(lcol, best)]:
                best = rcol

        pairs[lcol] = best

    # Create a sequence of columns from the pairs.
    for p in pairs:
        if p == pairs[p]:
            seq = [p]
            break

    while len(seq) < len(columns):
        for p in pairs:
            if pairs[p] == seq[0]:
                seq.insert(0, p)

    # Reassemble the image.
    for c in range(len(seq)):
        image.paste(columns[seq[c]], (c * cw, 0, c * cw + cw, h))

    return image

if __name__ == "__main__":
    import sys

    in_image = Image.open(sys.argv[1])
    out_image = unshred(in_image)
    out_image.show()
