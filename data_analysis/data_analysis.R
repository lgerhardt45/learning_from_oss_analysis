# install.packages("data.table") # uncomment if needed
# install.packages("rjson")
# install.packages("jtools")

library(data.table)
library(rjson)
library(jtools)

config <- fromJSON(file = "config.json")
observations_file_path = config$output_file_path

# import data
full_observations_file_path <- paste(getwd(), observations_file_path ,sep = "/")
observations <- read.csv(full_observations_file_path, header=TRUE, sep = ";", dec = ",")
observations_dt <- as.data.table(observations)

# add total number of stars
observations_dt[, total_nr_stars := average_stars*nr_projects_in_domain]
# add ratio of domain to non-domain projects of contributors
observations_dt[, domain_repo_ratio := nr_projects_in_domain/nr_of_projects_in_total]
mean(observations_dt[, domain_repo_ratio]) # ~0,292

# summary of data set
summary(observations_dt)


# number of observations
nrow(observations_dt) # 839
# number of observations by domain
observations_by_domain <- observations_dt[, .N, by = domain]
observations_by_domain[order(-N)]
# number of domains
nrow(observations_by_domain)  # 26
# number of company sponsored projects
company_sponsored_projects = observations_dt[domain_owner != '---']
domain_contributions_non_employed_contributions = company_sponsored_projects[employed_at_domain_owner == 0]
summary(domain_contributions_non_employed_contributions)
nrow(company_sponsored_projects[, .N,by = domain_owner])

# number of contributors working at domain owner by domains (keep in mind not all projects are sponsored)
employed_at_domain_owner <- observations_dt[employed_at_domain_owner == 1, .N, by = domain_owner]
employed_at_domain_owner[order(-N)]

# employed at domain owner strongly, significantly increases domain contribution
summary(lm(domain_contribution ~ employed_at_domain_owner, data = observations_dt))

# correlation matrix
vars <- observations_dt[,.(total_nr_stars, domain_contribution, nr_projects_in_domain, nr_of_projects_in_total, employed_at_domain_owner)]
round(cor(vars),5)

# plot
# remove total stars outliers
stars_to_domain_contribution_no_outliers <- observations_dt[total_nr_stars < 300 & domain_contribution < 4000, .(total_nr_stars, domain_contribution)]
plot(stars_to_domain_contribution_no_outliers)

### LINEAR MODELS ###
# total stars
limited_lm_total_nr_of_stars = lm(total_nr_stars ~ domain_contribution, data=observations_dt)
summary(limited_lm_total_nr_of_stars)
summ(limited_lm_total_nr_of_stars, digits = 4)
lm_total_nr_of_stars = lm(total_nr_stars ~
                            domain_contribution +
                            nr_projects_in_domain + 
                            nr_of_projects_in_total + 
                            employed_at_domain_owner,
                          data=observations_dt)
summary(lm_total_nr_of_stars) # domain contribution positive but not significant
 summ(lm_total_nr_of_stars, digits = 4)

# total
# average stars
lm_avg_stars = lm(average_stars ~
                    domain_contribution +
                    nr_projects_in_domain + 
                    nr_of_projects_in_total + 
                    employed_at_domain_owner,
                  data=observations_dt)
summary(lm_avg_stars) #!! domain contribution positive but not significant

# domain repo ration
lm_domain_repo_ratio = lm(domain_repo_ratio ~
                            domain_contribution +
                            total_nr_stars +
                            employed_at_domain_owner,
                          data=observations_dt)
summary(lm_domain_repo_ratio) # domain contribution significantly increases the domain repo ratio (domain repos to total repos)
summ(lm_domain_repo_ratio, digits = 5)
# nr projects in domain
lm_nr_projects_in_domain = lm(nr_projects_in_domain ~
                                domain_contribution + 
                                nr_of_projects_in_total +
                                employed_at_domain_owner,
                              data=observations_dt)
summary(lm_nr_projects_in_domain) # domain contribution influences nr of projects in domain positively, significantly
summ(lm_nr_projects_in_domain, digits = 5)
