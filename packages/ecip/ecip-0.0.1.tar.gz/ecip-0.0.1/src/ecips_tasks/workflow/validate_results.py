def gen_cksum(barcode, modulus=10):
    return (modulus - (3 * sum(barcode[::2]) + sum(barcode[1::2])) % modulus)


def validate_barcode(barcode):
    if len(barcode) != 22:
        status = False
    else:
        dig_list = [int(i) for i in barcode]
        status = (dig_list[-1] == gen_cksum(dig_list[:-1]))

    return status
