# TLDR
A Semi Auto Utility to do Import & Tidy Up Shopee Exported Data (Order.all & Income) into specifically designed Notion data tables.

# Installation
1. Make sure you have python installed.
2. Clone the repository.
3. Dive the dir:
    ```
    cd shopee/scripts/csv_splitter
    ```
4. Install dependencies by following this command:
    ```
    pip3 install -r requirements.txt
    ```

# How to Use (once every 10 days)
1. Export Order.all.***.xlsx within 10 days period e.g (1-10 January 2026)
2. Export Income.\*\*\*.xlsx within \<Order.All.\*\*\*.xlsx\> period + 4 days e.g (if Order.all.\*\*\*.xlsx period is 1-10 January 2026; then it should be: 1-14 January 2026)
3. Put the 2 exported files in a safe directory.
4. Run the script in this specific manner:
    ```
    python3 split_xlsx.py <Notion Integration Token> <Path to Order.***.xlsx> <Path to Income.***.xlsx>
    ```
5. Wait the script to finish.