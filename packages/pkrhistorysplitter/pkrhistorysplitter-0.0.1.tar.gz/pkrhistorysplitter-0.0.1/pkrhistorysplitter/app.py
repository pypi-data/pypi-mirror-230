from splitter import FileSplitter
fs = FileSplitter()
history_objects = fs.downloader.get_raw_histories_by_month_of_year(2016, 3)
print(len(history_objects))
fs.divide_raw_history_files(history_objects)