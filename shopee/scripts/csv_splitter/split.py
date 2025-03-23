#!/usr/bin/env python

import sys
import os
import pandas as pd
import csv

def parseArgs():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <input_file>.csv")
        sys.exit(1)
    fname = sys.argv[1]
    return fname

def loadCSV(fname):
    df = pd.read_csv(fname, delimiter=';', dtype=str)
    return df

def produceCSV(df, fout):
    df.to_csv(fout, sep=';', index=False, quoting=csv.QUOTE_ALL)
    print(f"Output saved to {fout}")
    return

def produceSelectiveCSV(data, keys, fout, dedupe=False):
    df = pd.DataFrame(data, columns=keys)
    if dedupe:
        df = df.drop_duplicates()
    produceCSV(df, fout)
    return

def renameKeys(df, keymap):
    df = df.rename(columns=keymap)
    return df

def main():
    fname = parseArgs()
    df = loadCSV(fname)
    # make new dir based on input filename
    dirname = os.path.splitext(fname)[0]
    os.makedirs(dirname, exist_ok=True)
    os.chdir(dirname)

    # produce customer data    
    # Rename Customer Keys
    customerData = renameKeys(df, {
        "Alamat Pengiriman": "Alamat",
        "Kota/Kabupaten": "Kota",
    })
    produceSelectiveCSV(customerData, ["Username (Pembeli)", "Nama Penerima", "No. Telepon", "Kota", "Alamat", "Provinsi"], "customer.csv", dedupe=True)

    # produce transaction order data
    # Rename Transaction Order Group Keys
    transactionOrderGroupData = renameKeys(df, {
        "No. Pesanan": "Transaction Code",
        "Waktu Pesanan Dibuat": "Transaction Date",
        "Username (Pembeli)": "Customer",
    })
    transactionOrderGroupData["Name"] = transactionOrderGroupData["Transaction Code"]
    transactionOrderGroupData["Marketplace"] = "Shopee"
    produceSelectiveCSV(transactionOrderGroupData, ["Name", "Transaction Code", "Marketplace", "Customer", "Transaction Date"], "transaction_order_group.csv", dedupe=True)
    
    # produce transaction order list data
    # Rename Transaction Order List Keys
    transactionOrderListData = renameKeys(df, {
        "No. Pesanan": "Transaction Code",
        "Waktu Pesanan Dibuat": "Transaction Date",
        "Nomor Referensi SKU": "Product",
        "Harga Setelah Diskon": "Price (unit)",
        "Jumlah": "Qty",
    })

    transactionOrderListData['Name'] = transactionOrderListData["Transaction Code"]
    transactionOrderListData["Price (unit)"] = transactionOrderListData["Price (unit)"].str.replace(".", "")
    produceSelectiveCSV(transactionOrderListData, ["Name", "Transaction Code", "Transaction Date", "Product", "Price (unit)", "Qty"], "transaction_order_list.csv", dedupe=True)

if __name__ == "__main__":
    main()