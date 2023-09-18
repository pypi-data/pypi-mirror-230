from src.CSVManager.index import CSV_manager

csv_file = CSV_manager("./tests/write_test.csv")

datas: list[list[any]] = [ [ "Name", "First name", "Birth Year" ], [ "Turing", "Alan", 1912 ], [ "Lovelace", "Ada", 1815 ], [ "Shanon", "Claude", 1916 ], [ "Truong", "André", 1936 ] ]

csv_file.write_csv(datas)

