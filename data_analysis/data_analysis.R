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
summary(observations_dt)

# number of observations
nrow(observations_dt)

# add total number of stars
observations_dt[, total_nr_stars := average_stars*nr_projects_in_domain]
observations_dt[, ln_total_nr_stars := log(average_stars*nr_projects_in_domain)]

hist(observations_dt[, ln_total_nr_stars])

# above 0 average stars
observations_above_0_stars_dt <- observations_dt[average_stars > 0]
observations_above_0_stars_dt[, ln_average_stars := log(average_stars)]
nrow(observations_above_0_stars_dt)
# linear model here
lm_avg_stars_log = lm(ln_average_stars ~ 
                    domain_contribution +
                    nr_projects_in_domain + 
                    nr_of_projects_in_total + 
                    employed_at_domain_owner,
                  data=observations_above_0_stars_dt)
summary(lm_avg_stars)

#
lm_total_number_of_stars = lm(total_nr_stars ~ 
                        domain_contribution +
                        nr_projects_in_domain + 
                        nr_of_projects_in_total + 
                        employed_at_domain_owner,
                      data=observations_dt)
summary(lm_total_number_of_stars)

# ln the average stars
observations_dt[, ln_average_stars := log(average_stars)]
hist(observations_dt[, ln_average_stars])

# ratio of domain to non-domain projects of contributors
observations_dt[, domain_repo_ratio := nr_projects_in_domain/nr_of_projects_in_total]
mean(observations_dt[, domain_repo_ratio]) # ~0,254

# number of contributors working at domain owner sorted by domains (keep in mind not all projects are sponsored)
employed_at_domain_owner <- observations_dt[employed_at_domain_owner == 1, .N, by = domain_owner]
employed_at_domain_owner[order(-N)]

# correlation matrix
vars <- observations_dt[,.(average_stars, domain_contribution, nr_projects_in_domain, nr_of_projects_in_total)]
round(cor(vars),5)

# plot
# remove avgerage_stars outliers
stars_domain_contr_no_outliers = observations_dt[average_stars < 300, .(average_stars, domain_contribution)]
plot(stars_domain_contr_no_outliers[, .(average_stars, domain_contribution)])

# linear models
# average stars
lm_avg_stars = lm(average_stars ~ 
                    domain_contribution +
                    nr_projects_in_domain + 
                    nr_of_projects_in_total, # + 
                    #employed_at_domain_owner,
                  data=observations_dt)
summary(lm_avg_stars) #!! domain contribution positive but not significant

lm_avg_stars_limited = lm(average_stars ~ 
                        domain_contribution,
                      data=observations_dt)
summary(lm_avg_stars_limited) # domain contribution negatively, not significant

# total stars

# nr projects in domain
lm_nr_projects_in_domain = lm(nr_projects_in_domain ~
                                domain_contribution + 
                                nr_of_projects_in_total +
                                employed_at_domain_owner,
                              data=observations_dt)
summary(lm_nr_projects_in_domain) #!! this way round: domain contribution influences nr of projects in domain positively, significantly

lm_domain_repo_ratio = lm(domain_repo_ratio ~
                                domain_contribution + 
                                employed_at_domain_owner,
                              data=observations_dt)
summary(lm_domain_repo_ratio) # being employed at domain owner significantly increases the domain repo ratio (domain repos to total repos)
