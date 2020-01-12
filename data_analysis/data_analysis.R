# install.packages("data.table") # uncomment if needed
# install.packages("rjson")      # uncomment if needed
library(data.table)
library(rjson)

config <- fromJSON(file = "config.json")
observations_file_path = config$output_file_path

# import data
full_observations_file_path <- paste(getwd(), observations_file_path ,sep = "/")
observations <- read.csv(full_observations_file_path, header=TRUE, sep = ";", dec = ",")
observations_dt <- as.data.table(observations)
class(observations_dt)
summary(observations_dt)
