import torch
from math import floor, ceil

def stat(model, howio=print):
    def fmt(info, length, place):
        info = str(info)
        if place == "center":
            return " " * floor((length - len(info)) / 2) + info + " " * ceil((length - len(info)) / 2)
        elif place == "left":
            return " " + info + " " * floor(length - len(info) - 1)
        elif place == "right":
            return " " * floor(length - len(info) - 1) + info + " "
    def elafmt(sz, carry, seq, dig):
        idx = 0
        while sz >= carry and idx < len(seq) - 1:
            sz = sz / carry
            idx = idx + 1
        if idx == 0 and seq[idx] == "":
            return "{:d}".format(int(sz))
        elif idx == 0 or int(sz) == sz:
            return "{:d} {}".format(int(sz), seq[idx])
        elif dig == 2:
            return "{:.2f} {}".format(sz, seq[idx])
        elif dig == 4:
            return "{:.4f} {}".format(sz, seq[idx])
    mem_lookup = {
        torch.uint8: 1,
        torch.ByteTensor: 1,
        torch.int8: 1,
        torch.CharTensor: 1,
        torch.int16: 2,
        torch.short: 2,
        torch.ShortTensor: 2,
        torch.float16: 2,
        torch.half: 2,
        torch.HalfTensor: 2,
        torch.int32: 4,
        torch.int: 4,
        torch.IntTensor: 4,
        torch.float: 4,
        torch.float32: 4,
        torch.FloatTensor: 4,
        torch.float64: 8,
        torch.double: 8,
        torch.DoubleTensor: 8,
        torch.int64: 8,
        torch.long: 8,
        torch.LongTensor: 8
    }

    info = ""
    model_info, model_params, model_memsz, row_width = [], 0, 0, (5, 6, 7, 8, 8)
    for idx, (name, w_variable) in enumerate(model.named_parameters()):
        shape = str(w_variable.shape)
        params = 1
        for dim_size in w_variable.shape:
            params = params * dim_size
        model_params = model_params + params
        model_memsz = model_memsz + mem_lookup[w_variable.dtype] * params
        row_width = (max(row_width[0], len(str(idx)) + 2),
                     max(row_width[1], len(str(name)) + 2),
                     max(row_width[2], len(str(shape)) + 2),
                     max(row_width[3], len(elafmt(params, 1000, ["", "K", "M", "B", "T"], 2)) + 2),
                     max(row_width[4], len(elafmt(mem_lookup[w_variable.dtype] * params, 1024, ["Bytes", "KBytes", "MBytes", "GBytes", "TBytes"], 2)) + 2))
        model_info.append((idx, name, shape, elafmt(params, 1000, ["", "K", "M", "B", "T"], 2), elafmt(mem_lookup[w_variable.dtype] * params, 1024, ["Bytes", "KBytes", "MBytes", "GBytes", "TBytes"], 2)))

    info = info + "-" * (row_width[0] + row_width[1] + row_width[2] + row_width[3] + row_width[4] + 6) + "\n"
    info = info + "|{}|{}|{}|{}|{}|\n".format(fmt("idx", row_width[0], "center"), fmt("Name", row_width[1], "center"), fmt("Shape", row_width[2], "center"), fmt("Params", row_width[3], "center"), fmt("Memory", row_width[4], "center"))
    info = info + "-" * (row_width[0] + row_width[1] + row_width[2] + row_width[3] + row_width[4] + 6) + "\n"
    for item in model_info:
        info = info + "|{}|{}|{}|{}|{}|\n".format(fmt(item[0], row_width[0], "right"), fmt(item[1], row_width[1], "left"), fmt(item[2], row_width[2], "left"), fmt(item[3], row_width[3], "left"), fmt(item[4], row_width[4], "left"))
    info = info + "-" * (row_width[0] + row_width[1] + row_width[2] + row_width[3] + row_width[4] + 6) + "\n"
    info = info + "|{}|\n".format(fmt("Model params: {}".format(elafmt(model_params, 1000, ["", "K", "M", "B", "T"], 4)), row_width[0] + row_width[1] + row_width[2] + row_width[3] + row_width[4] + 4, "left"))
    info = info + "|{}|\n".format(fmt("Model memory: {}".format(elafmt(model_memsz, 1024, ["Bytes", "KBytes", "MBytes", "GBytes", "TBytes"], 4)), row_width[0] + row_width[1] + row_width[2] + row_width[3] + row_width[4] + 4, "left"))
    info = info + "-" * (row_width[0] + row_width[1] + row_width[2] + row_width[3] + row_width[4] + 6)
    if howio == "str":
        return info
    elif callable(howio):
        howio(info)
