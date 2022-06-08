library(mondrian)
library(lubridate)

seed <- now()
seed
seed8601 <- format_ISO8601(seed)
audrey8601 <- "2022-04-06 11:10:54 UTC"
seedDT <- ymd_hms(audrey8601)
audrey <- seedDT
audrey
compose(seed = audrey)
