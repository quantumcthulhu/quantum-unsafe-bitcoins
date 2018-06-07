#!/usr/bin/env python3
all_money = 0
f = open("cs.output", "r")
for line in f:
    tx, output_id, address, money = line.strip().split(";")
    all_money += int(money)
f.close()

vuln_money = 0
f = open("vulnerable.txt", "r")
for line in f:
    address, money = line.strip().split(";")
    vuln_money += int(money)
f.close()

print("all={}, vuln={}".format(all_money, vuln_money))