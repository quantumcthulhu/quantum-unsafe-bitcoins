#!/usr/bin/env python3
input_file = "cs.output"
output_file = "address-utxo.txt"

def main():
    data = {}

    num_lines = sum(1 for line in open(input_file))
    print("utxo: {}".format(num_lines))

    i = 0
    f = open(input_file, "r")
    for line in f:
        tx, output_id, address, money = line.strip().split(";")
        utxo = tx + output_id

        if address in data:
            data[address]["utxo"].append(utxo)
            data[address]["balance"] += int(money)

        else:
            data[address] = {"utxo": [utxo], "balance": int(money)}

        if i % 1000000 == 1:
            print("{}/{}".format(i, num_lines))
        i += 1

    f.close()

    print("saving to {}".format(output_file))

    fout = open(output_file, "w")
    for address in data:

        fout.write("{};{};{}\n".format(
            address,
            data[address]["balance"],
            ','.join(data[address]["utxo"])
        ))

    fout.close()

if __name__ == '__main__':
    main()