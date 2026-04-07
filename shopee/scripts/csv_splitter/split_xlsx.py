#!/usr/bin/env python
import sys
import os
import pandas as pd
import csv
from csv2notion_neo import cli as csv2notionCLI
from datetime import datetime


def parseArgs():
    if len(sys.argv) != 4:
        print(
            f"Usage: python3 {sys.argv[0]} <Notion Integration Token> <Order>.xlsx <Income>.xlsx"
        )
        sys.exit(1)
    notionToken = sys.argv[1]
    forder = sys.argv[2]
    fincome = sys.argv[3]
    return notionToken, forder, fincome


def loadXLSX(fname, sheet_name, header=0):
    df = pd.read_excel(fname, dtype=str, sheet_name=sheet_name, header=header)
    return df


def produceCSV(df, fout):
    df.to_csv(fout, sep=";", index=False, quoting=csv.QUOTE_ALL)
    print(f"Output saved to {fout}")
    return


def produceSelectiveCSV(data, keys, fout, dedupe=False):
    df = pd.DataFrame(data, columns=keys)
    if dedupe:
        df = df.drop_duplicates()
    produceCSV(df, fout)
    return fout


def renameKeys(df, keymap):
    df = df.rename(columns=keymap)
    return df


def filtersOut(df, keys, cb):
    for key in keys:
        if key in df.columns:
            df = df[df[key].apply(cb)]
    return df


def dataPrep(forder, fincome):
    dforder = loadXLSX(forder, "orders")
    dfincome = loadXLSX(fincome, "Income", 5)

    dfmerged = pd.merge(dforder, dfincome, on="No. Pesanan", how="left")

    dirname = os.path.splitext(forder)[0]
    os.makedirs(dirname, exist_ok=True)

    df = filtersOut(dfmerged, ["Status Pesanan"], lambda x: x != "Batal")

    # pull kecamatan
    def pullKecamatanFromAlamat(alamat: str):
        kecamatan = alamat.split(",")[-4].strip()
        return kecamatan

    df["Kecamatan"] = df["Alamat Pengiriman"].apply(pullKecamatanFromAlamat)

    def dateIsoFormat(date: str):
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M")
        iso = dt.astimezone().isoformat()
        return iso

    df["Waktu Pesanan Dibuat_x"] = df["Waktu Pesanan Dibuat_x"].apply(dateIsoFormat)
    df["Waktu Pesanan Selesai"] = df["Waktu Pesanan Selesai"].apply(dateIsoFormat)

    # Absolute Value
    def absoluteValue(x):
        try:
            return str(abs(float(x)))
        except:
            return x

    df["Biaya Komisi AMS"] = df["Biaya Komisi AMS"].apply(absoluteValue)
    df["Biaya Administrasi"] = df["Biaya Administrasi"].apply(absoluteValue)
    df["Biaya Layanan"] = df["Biaya Layanan"].apply(absoluteValue)
    df["Biaya Proses Pesanan"] = df["Biaya Proses Pesanan"].apply(absoluteValue)

    customerData = renameKeys(
        df,
        {
            "Username (Pembeli)_x": "Username (Pembeli)",
            "Alamat Pengiriman": "Alamat",
            "Kota/Kabupaten": "Kota",
        },
    )
    fcustomer = produceSelectiveCSV(
        customerData,
        ["Username (Pembeli)", "Kota", "Kecamatan", "Alamat", "Provinsi"],
        f"{dirname}{os.sep}customer.csv",
        dedupe=True,
    )

    transactionOrderGroupData = renameKeys(
        df,
        {
            "No. Pesanan": "Transaction Code",
            "Waktu Pesanan Dibuat_x": "Transaction Date",
            "Username (Pembeli)_x": "Customer",
            "Waktu Pesanan Selesai": "Completed Date",
            "Biaya Komisi AMS": "Affiliate Fee",
            "Biaya Administrasi": "Admin Fee",
            "Biaya Layanan": "Platform Fee",
            "Biaya Proses Pesanan": "Order Fee",
        },
    )
    transactionOrderGroupData["Name"] = transactionOrderGroupData["Transaction Code"]
    transactionOrderGroupData["Marketplace"] = "Shopee"
    ftog = produceSelectiveCSV(
        transactionOrderGroupData,
        [
            "Name",
            "Transaction Code",
            "Marketplace",
            "Customer",
            "Transaction Date",
            "Completed Date",
            "Affiliate Fee",
            "Admin Fee",
            "Platform Fee",
            "Order Fee",
        ],
        f"{dirname}{os.sep}transaction_order_group.csv",
        dedupe=True,
    )

    transactionOrderListData = renameKeys(
        df,
        {
            "No. Pesanan": "Transaction Group",
            "Waktu Pesanan Dibuat_x": "Transaction Date",
            "Nomor Referensi SKU": "Product",
            "Harga Setelah Diskon": "Price @",
            "Jumlah": "Qty",
        },
    )
    transactionOrderListData["Name"] = transactionOrderListData["Transaction Group"]
    transactionOrderListData["Price @"] = transactionOrderListData[
        "Price @"
    ].str.replace(".", "")
    transactionOrderListData["Product Code"] = transactionOrderListData["Product"]
    ftol = produceSelectiveCSV(
        transactionOrderListData,
        [
            "Name",
            "Transaction Group",
            "Transaction Date",
            "Product Code",
            "Price @",
            "Qty",
        ],
        f"{dirname}{os.sep}transaction_order_list.csv",
        dedupe=True,
    )

    return fcustomer, ftog, ftol


def doImports(notionToken, fcustomer, ftog, ftol):

    # # DUMMIES
    # # customer
    # csv2notionCLI.cli(
    #     "--workspace",
    #     "Snapp Mart",
    #     "--token",
    #     notionToken,
    #     "--url",
    #     "https://www.notion.so/f7479d160eed822f89dd010ef1bf5695?v=c9279d160eed830480840873295671af",
    #     "--delimiter",
    #     ";",
    #     "--merge",
    #     fcustomer,
    # )

    # # tog
    # csv2notionCLI.cli(
    #     "--workspace",
    #     "Snapp Mart",
    #     "--token",
    #     notionToken,
    #     "--url",
    #     "https://www.notion.so/14179d160eed8217bffa8133e7785f66?v=33b79d160eed804a997c000c303700fa",
    #     "--delimiter",
    #     ";",
    #     "--merge",
    #     ftog,
    # )

    # # tol
    # csv2notionCLI.cli(
    #     "--workspace",
    #     "Snapp Mart",
    #     "--token",
    #     notionToken,
    #     "--url",
    #     "https://www.notion.so/33b79d160eed8055bcd8df6bad48074b?v=33b79d160eed81f49259000c1ad5a0f5",
    #     "--delimiter",
    #     ";",
    #     "--merge",
    #     ftol,
    # )

    # PROD
    # customer
    csv2notionCLI.cli(
        "--workspace",
        "Snapp Mart",
        "--token",
        notionToken,
        "--url",
        "https://www.notion.so/20b97959342b4566bf317b626c2e152e?v=1a779d160eed809999a5000c045ec8f2",
        "--delimiter",
        ";",
        "--merge",
        fcustomer,
    )

    # tog
    csv2notionCLI.cli(
        "--workspace",
        "Snapp Mart",
        "--token",
        notionToken,
        "--url",
        "https://www.notion.so/2e279d160eed80c4b475e90d829a2b2c?v=33b79d160eed8085a42b000c734e67b2",
        "--delimiter",
        ";",
        "--merge",
        ftog,
    )

    # tol
    csv2notionCLI.cli(
        "--workspace",
        "Snapp Mart",
        "--token",
        notionToken,
        "--url",
        "https://www.notion.so/2ef79d160eed80f5b3fbd311ff4cfbd5?v=2ef79d160eed813b89d7000c2011e6d8",
        "--delimiter",
        ";",
        "--merge",
        ftol,
    )


def main():
    notionToken, forder, fincome = parseArgs()
    fcustomer, ftog, ftol = dataPrep(forder, fincome)
    doImports(notionToken, fcustomer, ftog, ftol)


if __name__ == "__main__":
    main()
