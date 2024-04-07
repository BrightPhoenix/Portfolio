# install.packages("remotes")
# remotes::install_github("mstrimas/ebppackages")

## Set the working directory
setwd("/Users/kimberlyadams/Documents/Bellevue Masters in Data Science/3 Statistics and R/Project/AUKPractice/")

# set ebd path
auk::auk_set_ebd_path("/data/ebird")

library(auk)
library(lubridate)
library(sf)
library(gridExtra)
library(tidyverse)
# resolve namespace conflicts
select <- dplyr::select

# setup data directory
dir.create("data", showWarnings = FALSE)

ebd <- auk_ebd("ebd_woothr_june_bcr27.txt", 
               file_sampling = "ebd_checklists_june_bcr27.txt")

# Next, define the filters that you want to apply to the EBD. Each field that you can filter on has an associated function. For example, we’ll filter to Wood Thrush observations with auk_species(), from BCR 27 with auk_bcr(), in June of any year with auk_date(), restrict observations to those from either Stationary or Traveling protocols with auk_protocol(), and only keep complete checklists with auk_complete() since we intend to zero-fill the data.

ebd_filters <- ebd %>% 
    auk_species("Wood Thrush") %>% 
    # southeastern coastal plain bcr
    auk_bcr(bcr = 27) %>% 
    # june, use * to get data from any year
    auk_date(date = c("*-06-01", "*-06-30")) %>% 
    # restrict to the standard traveling and stationary count protocols
    auk_protocol(protocol = c("Stationary", "Traveling")) %>% 
    auk_complete()
# Double check the filters you have defined
ebd_filters

# Note that printing the object ebd_filters shows what filters have been set. At this point, we’ve only defined the filters, not applied them to the EBD. The last step is to use auk_filter() to compile the filters into an AWK script and run it to produce two output files: one for the EBD and one for the SED. This step typically takes several hours to run since the files are so large. As a result, it’s wise to wrap this in an if statement, so it’s only run once.

# output files
data_dir <- "data"
if (!dir.exists(data_dir)) {
    dir.create(data_dir)
}
f_ebd <- file.path(data_dir, "ebd_woothr_june_bcr27.txt")
f_sampling <- file.path(data_dir, "ebd_checklists_june_bcr27.txt")

# only run if the files don't already exist
if (!file.exists(f_ebd)) {
    auk_filter(ebd_filters, file = f_ebd, file_sampling = f_sampling)
}

# The previous step left us with two tab separated text files, one for the EBD and one for the SED. Next, we’ll use auk_zerofill() to read these two files into R and combine them together to produce zero-filled, detection/non-detection data (also called presence/absence data). To just read the EBD or SED, but not combine them, use read_ebd() or read_sampling(), respectively.

ebd_zf <- auk_zerofill(f_ebd, f_sampling, collapse = TRUE)

# When any of the read functions from auk are used, two important processing steps occur by default behind the scenes. First, eBird observations can be made at levels below species (e.g. subspecies) or above species (e.g. a bird that was only identified as Duck sp.); however, for most uses we’ll want observations at the species level. auk_rollup() is applied by default when auk_zerofill() is used, and it drops all observations not identifiable to a species and rolls up all observations reported below species to the species level. eBird also allows for group checklists, those shared by multiple users. These checklists lead to duplication or near duplication of records within the dataset and the function auk_unique(), applied by default by auk_zerofill(), addresses this by only keeping one independent copy of each checklist. Finally, by default auk_zerofill() returns a compact representation of the data, consisting of a list of two data frames, one with checklist data and the other with observation data; the use of collapse = TRUE combines these into a single data frame, which will be easier to work with.

# Before continuing, we’ll transform some of the variables to a more useful form for modelling. We convert time to a decimal value between 0 and 24, and we force the distance travelled to 0 for stationary checklists. Notably, eBirders have the option of entering an “X” rather than a count for a species, to indicate that the species was present, but they didn’t keep track of how many individuals were observed. During the modeling stage, we’ll want the observation_count variable stored as an integer and we’ll convert “X” to NA to allow for this.

# function to convert time observation to hours since midnight
time_to_decimal <- function(x) {
    x <- hms(x, quiet = TRUE)
    hour(x) + minute(x) / 60 + second(x) / 3600
}

# clean up variables
ebd_zf <- ebd_zf %>% 
    mutate(
        # convert X to NA
        observation_count = if_else(observation_count == "X", 
                                    NA_character_, observation_count),
        observation_count = as.integer(observation_count),
        # effort_distance_km to 0 for non-travelling counts
        effort_distance_km = if_else(protocol_type != "Traveling", 
                                     0, effort_distance_km),
        # convert time to decimal hours since midnight
        time_observations_started = time_to_decimal(time_observations_started),
        # split date into year and day of year
        year = year(observation_date),
        day_of_year = yday(observation_date)
    )

# As discussed in the Introduction, variation in effort between checklists makes inference challenging, because it is associated with variation in detectability. When working with semi-structured datasets like eBird, one approach to dealing with this variation is to impose some more consistent structure on the data by filtering observations on the effort variables. This reduces the variation in detectability between checklists. Based on our experience working with these data, we suggest restricting checklists to less than 5 hours long and 5 km in length, and with 10 or fewer observers. Furthermore, we’ll only consider data from the past 10 years (2010-2019).

# As discussed in the Introduction, variation in effort between checklists makes inference challenging, because it is associated with variation in detectability. When working with semi-structured datasets like eBird, one approach to dealing with this variation is to impose some more consistent structure on the data by filtering observations on the effort variables. This reduces the variation in detectability between checklists. Based on our experience working with these data, we suggest restricting checklists to less than 5 hours long and 5 km in length, and with 10 or fewer observers. Furthermore, we’ll only consider data from the past 10 years (2010-2019).

ebd_zf_filtered <- ebd_zf %>% 
    filter(
        # effort filters
        duration_minutes <= 5 * 60,
        effort_distance_km <= 5,
        # last 10 years of data
        year >= 2010,
        # 10 or fewer observers
        number_observers <= 10)

# Finally, there are a large number of variables in the EBD that are redundant (e.g. both state names and codes are present) or unnecessary for most modeling exercises (e.g. checklist comments and Important Bird Area codes). These can be removed at this point, keeping only the variables we want for modelling. Then we’ll save the resulting zero-filled observations for use in later chapters.

ebird <- ebd_zf_filtered %>% 
    select(checklist_id, observer_id, sampling_event_identifier,
           scientific_name,
           observation_count, species_observed, 
           state_code, locality_id, latitude, longitude,
           protocol_type, all_species_reported,
           observation_date, year, day_of_year,
           time_observations_started, 
           duration_minutes, effort_distance_km,
           number_observers)
write_csv(ebird, "data/ebd_woothr_june_bcr27_zf.csv", na = "")

sampleData <- read.csv("data/ebd_woothr_june_bcr27_zf.csv")
View(sampleData)