import re
import zlib
from collections import Counter

TOK_RE = re.compile(rb"-?(?:\d+\.?\d*|\.\d+)|[A-Za-z*'\"]+")
BUILD_OPS = {b"m", b"l", b"c", b"v", b"y", b"h", b"re"}
PAINT_OPS = {b"f", b"F", b"f*", b"S", b"s", b"B", b"B*", b"b", b"b*"}


def fmt_exact(v):
    if abs(v) < 1e-8:
        return b"0"
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return s.encode("ascii")


def fmt_key(v):
    if abs(v) < 1e-5:
        return b"0"
    return f"{v:.3f}".rstrip("0").rstrip(".").encode("ascii")


def is_num(tok):
    c = tok[0]
    return (48 <= c <= 57) or c in (43, 45, 46)


def compress_pdf(input_path: str, output_path: str) -> int:
    with open(input_path, "rb") as f:
        data = f.read()

    # استخراج رقم الـ Root الحقيقي من التذييل الأصلي للملف
    root_match = re.search(rb"/Root\s+(\d+\s+\d+\s+R)", data)
    root_ref = root_match.group(1) if root_match else b"1 0 R"

    objs = {}
    max_id = 0
    for m in re.finditer(rb"(?m)^(\d+)\s+0\s+obj\r?\n(.*?)\r?\nendobj(?=\r?\n|$)", data, re.DOTALL):
        oid = int(m.group(1))
        objs[oid] = m.group(2)
        if oid > max_id:
            max_id = oid

    streams, stream_paths, freq = {}, {}, Counter()

    for oid, body in list(objs.items()):
        sm = re.match(rb"^(<<.*?>>)\s*stream\r?\n(.*?)\r?\nendstream$", body, re.DOTALL)
        if not sm:
            continue
        hdr, raw_st = sm.group(1), sm.group(2)
        if any(k in hdr for k in (b"/Image", b"/FontFile", b"/Metadata")):
            continue

        # فك ضغط الـ Stream إذا كان مضغوطاً بـ FlateDecode
        is_flate = b"/FlateDecode" in hdr
        if is_flate:
            try:
                st = zlib.decompress(raw_st)
            except Exception:
                continue
        else:
            st = raw_st

        if len(st) < 60 or not all(b < 128 for b in st[:300]):
            continue
        streams[oid] = (hdr, st, is_flate)

        tokens = [(m.start(), m.end(), m.group(0)) for m in TOK_RE.finditer(st)]
        paths, in_path, num_stack, cur_ops, start_pos = [], False, [], [], 0

        for ts, te, tok in tokens:
            if is_num(tok):
                if not in_path and not num_stack:
                    start_pos = ts
                num_stack.append((ts, float(tok)))
                if len(num_stack) > 8:
                    num_stack.pop(0)
            elif tok in BUILD_OPS:
                if tok == b"m" and len(num_stack) >= 2:
                    if not in_path:
                        in_path = True
                        start_pos = num_stack[-2][0]
                        cur_ops = []
                    cur_ops.append((b"m", [num_stack[-2][1], num_stack[-1][1]]))
                    num_stack.clear()
                elif in_path:
                    need = {b"l": 2, b"c": 6, b"v": 4, b"y": 4, b"re": 4, b"h": 0}[tok]
                    if len(num_stack) >= need:
                        vals = [x[1] for x in num_stack[-need:]] if need else []
                        cur_ops.append((tok, vals))
                        num_stack.clear()
                    else:
                        in_path = False
                        num_stack.clear()
                else:
                    num_stack.clear()
            elif tok in PAINT_OPS and in_path and len(cur_ops) >= 2:
                x0, y0 = cur_ops[0][1]
                key_parts, exact_parts, xs, ys = [], [], [0.0], [0.0]
                for op, vals in cur_ops:
                    if op == b"re":
                        rx, ry, rw, rh = vals[0] - x0, vals[1] - y0, vals[2], vals[3]
                        xs.extend([rx, rx + rw])
                        ys.extend([ry, ry + rh])
                        key_parts.append(b" ".join([fmt_key(rx), fmt_key(ry), fmt_key(rw), fmt_key(rh), b"re"]))
                        exact_parts.append(b" ".join([fmt_exact(rx), fmt_exact(ry), fmt_exact(rw), fmt_exact(rh), b"re"]))
                    elif vals:
                        kvals, evals = [], []
                        for idx in range(0, len(vals), 2):
                            nx, ny = vals[idx] - x0, vals[idx + 1] - y0
                            xs.append(nx)
                            ys.append(ny)
                            kvals.extend([fmt_key(nx), fmt_key(ny)])
                            evals.extend([fmt_exact(nx), fmt_exact(ny)])
                        key_parts.append(b" ".join(kvals + [op]))
                        exact_parts.append(b" ".join(evals + [op]))
                    else:
                        key_parts.append(op)
                        exact_parts.append(op)
                key_parts.append(tok)
                exact_parts.append(tok)
                key = b" ".join(key_parts)
                exact_body = b" ".join(exact_parts)
                if len(exact_body) >= 32:
                    bbox = (min(xs) - 2, min(ys) - 2, max(xs) + 2, max(ys) + 2)
                    paths.append((start_pos, te, x0, y0, key, exact_body, bbox))
                    freq[key] += 1
                in_path = False
                num_stack.clear()
            else:
                in_path = False
                num_stack.clear()

        if paths:
            stream_paths[oid] = paths

    key_to_form, form_defs, form_idx = {}, {}, 1
    for key, cnt in freq.items():
        if cnt >= 3:
            key_to_form[key] = f"F{form_idx}".encode("ascii")
            form_idx += 1

    for paths in stream_paths.values():
        for _, _, _, _, key, exact_body, bbox in paths:
            if key in key_to_form and key_to_form[key] not in form_defs:
                form_defs[key_to_form[key]] = (exact_body, bbox)

    form_obj_ids = {}
    for fname, (exact_body, bbox) in form_defs.items():
        max_id += 1
        fid = max_id
        form_obj_ids[fname] = fid
        bx0, by0, bx1, by1 = bbox
        comp_form = zlib.compress(exact_body, level=9)
        fdict = (
            f"<< /Type /XObject /Subtype /Form /FormType 1 "
            f"/BBox [{fmt_exact(bx0).decode()} {fmt_exact(by0).decode()} {fmt_exact(bx1).decode()} {fmt_exact(by1).decode()}] "
            f"/Filter /FlateDecode /Length {len(comp_form)} >>"
        ).encode("ascii")
        objs[fid] = fdict + b"\nstream\n" + comp_form + b"\nendstream"

    used_in_stream = {}
    for oid, paths in stream_paths.items():
        hdr, st, is_flate = streams[oid]
        out_st, pos, used = bytearray(), 0, set()
        for sp, ep, x0, y0, key, _, _ in paths:
            fname = key_to_form.get(key)
            if fname:
                out_st.extend(st[pos:sp])
                out_st.extend(b"q 1 0 0 1 " + fmt_exact(x0) + b" " + fmt_exact(y0) + b" cm /" + fname + b" Do Q")
                pos = ep
                used.add(fname)
        if used:
            out_st.extend(st[pos:])
            clean_st = bytes(out_st)
            final_st = zlib.compress(clean_st, level=9)
            new_hdr = re.sub(rb"/Length\s+\d+", f"/Length {len(final_st)}".encode("ascii"), hdr)
            if not is_flate:
                new_hdr = re.sub(rb"^<<", b"<< /Filter /FlateDecode ", new_hdr, count=1)
            objs[oid] = new_hdr + b"\nstream\n" + final_st + b"\nendstream"
            used_in_stream[oid] = used

    stream_owners = {}
    for oid, body in objs.items():
        cm = re.search(rb"/Contents\s+(?:(\d+)\s+0\s+R|\[([^\]]+)\])", body)
        if cm:
            refs = [int(cm.group(1))] if cm.group(1) else [int(x) for x in re.findall(rb"(\d+)\s+0\s+R", cm.group(2))]
            for r in refs:
                stream_owners.setdefault(r, []).append(oid)

    owner_forms = {}
    for sid, fnames in used_in_stream.items():
        for ow in stream_owners.get(sid, [sid]):
            owner_forms.setdefault(ow, set()).update(fnames)

    for ow, fnames in owner_forms.items():
        body = objs[ow]
        xobj_entries = b" ".join(b"/" + fn + f" {form_obj_ids[fn]} 0 R".encode("ascii") for fn in sorted(fnames))
        rm = re.search(rb"/Resources\s+(\d+)\s+0\s+R", body)
        target_id = int(rm.group(1)) if rm else ow
        tbody = objs[target_id]
        xm = re.search(rb"/XObject\s+(\d+)\s+0\s+R", tbody)
        if xm:
            xid = int(xm.group(1))
            objs[xid] = re.sub(rb"^<<", b"<< " + xobj_entries + b" ", objs[xid], count=1)
        elif re.search(rb"/XObject\s*<<", tbody):
            objs[target_id] = re.sub(rb"/XObject\s*<<", b"/XObject << " + xobj_entries + b" ", tbody, count=1)
        elif re.search(rb"/Resources\s*<<", tbody):
            objs[target_id] = re.sub(rb"/Resources\s*<<", b"/Resources << /XObject << " + xobj_entries + b" >> ", tbody, count=1)
        else:
            objs[target_id] = re.sub(rb"^<<", b"<< /Resources << /XObject << " + xobj_entries + b" >> >> ", tbody, count=1)

    with open(output_path, "wb") as out:
        out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = {}
        for oid in sorted(objs.keys()):
            offsets[oid] = out.tell()
            out.write(f"{oid} 0 obj\n".encode("ascii") + objs[oid] + b"\nendobj\n")
        xref_pos = out.tell()
        sz = max_id + 1
        out.write(f"xref\n0 {sz}\n0000000000 65535 f\r\n".encode("ascii"))
        for oid in range(1, sz):
            out.write((f"{offsets[oid]:010d} 00000 n\r\n" if oid in offsets else "0000000000 65535 f\r\n").encode("ascii"))
        out.write(b"trailer\n<< /Size " + f"{sz}".encode("ascii") + b" /Root " + root_ref + b" >>\nstartxref\n" + f"{xref_pos}".encode("ascii") + b"\n%%EOF\n")

    return len(form_obj_ids)