#!/usr/bin/env python3
import asyncio
from aiorpcx import ClientSession
import operator
import bech32
import hashlib
import binascii

input_file = "address-utxo.txt"
unsorted_output_file = "vulnerable-unsorted.txt"
sorted_output_file = "vulnerable.txt"

electrumx_host = "localhost"
electrumx_port = 50001

def bech32_to_scripthash(address) :
    hrp, data = bech32.bech32_decode(address)
    witver, witprog = bech32.decode(hrp, address)
    script = [witver, len(witprog)] + witprog
    script = ''.join('{:02x}'.format(x) for x in script)
    scripthash = hashlib.sha256(binascii.unhexlify(script)).hexdigest()
    rev = ''
    i = len(scripthash) - 2
    while i >= 0 :
        rev += scripthash[i:i+2]
        i -= 2
    return rev

async def get_tx_history(address):
    async with ClientSession(electrumx_host, electrumx_port) as session:
        if address.find("bc1") == 0 :
            scripthash = bech32_to_scripthash(address)
            await session.send_request("server.version", ["demo", "1.1"], timeout=60)
            response = await session.send_request("blockchain.scripthash.get_history", [scripthash], timeout=60)
            return response
        else :    
            return await session.send_request("blockchain.address.get_history", [address], timeout=60)

def main():
    vulnerable = {}

    num_lines = sum(1 for line in open(input_file))
    print("addresses: {}".format(num_lines))

    i = 0
    f = open(input_file, "r")
    fout_unsorted = open(unsorted_output_file, "w")

    for line in f:
        address, balance, utxo_str = line.strip().split(";")
        balance = int(balance)
        utxo_array = utxo_str.split(",")

        # cut tx output index from utxo
        tx_array = []
        for utxo in utxo_array:
            tx_array.append(utxo[:64])

        loop = asyncio.get_event_loop()
        try:
            tx_history = loop.run_until_complete(get_tx_history(address))
            for record in tx_history:
                if record["tx_hash"] not in tx_array:
                    vulnerable[address] = balance
                    fout_unsorted.write("{};{}\n".format(address, balance))
                    break

        except OSError:
            print('cannot connect')
        except Exception as e:
            if str(e).find("response too large") > -1 :
                vulnerable[address] = balance
                fout_unsorted.write("{};{}\n".format(address, balance))
            else:
                print('error making request for address {}: {}'.format(address, e))
    
        if i % 1000 == 1:
            print("{}/{}".format(i, num_lines))
        i += 1

    fout_unsorted.close()

    print("sorting...")
    vulnerable_sorted = sorted(vulnerable.items(),key = operator.itemgetter(1), reverse = True)

    print("saving sorted to {}".format(sorted_output_file))
    fout_sorted = open(sorted_output_file, "w")
    for record in vulnerable_sorted:
        fout_sorted.write("{};{}\n".format(record[0],record[1]))
    fout_sorted.close()

if __name__ == '__main__':
    main()
