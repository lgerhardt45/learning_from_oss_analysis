# install.packages("data.table") # uncomment if needed
# install.packages("rjson")      # uncomment if needed
library(data.table)
library(rjson)

config <- fromJSON(file = "config.json")
observations_file_path = config$output_file_path
