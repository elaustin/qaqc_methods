###########################################
# RCurlTest.R
#
# Basic curl implementaiton for downloading Kairos data
#
# Graeme Carvlin
# 4/4/2016
#
# Elena Austin
# 4/15/2016
###########################################

#Download data
library(curl)
h <- new_handle()
data = "{\"start_absolute\": 1452297600000, \"end_absolute\": 1456790400000,\"metrics\" : [
{\"name\": Dylos25, \"tags\": {\"Bin\":\"bin1\"}, \"aggregators\": [{\"name\": \"avg\", \"align_sampling\": \"true\", \"sampling\": {\"value\": 1, \"unit\": \"hours\"}}]}, 
{\"name\": Dylos25, \"tags\": {\"Bin\":\"bin2\"}, \"aggregators\": [{\"name\": \"avg\", \"align_sampling\": \"true\", \"sampling\": {\"value\": 1, \"unit\": \"hours\"}}]},
{\"name\": Dylos25, \"tags\": {\"Bin\":\"bin3\"}, \"aggregators\": [{\"name\": \"avg\", \"align_sampling\": \"true\", \"sampling\": {\"value\": 1, \"unit\": \"hours\"}}]},
{\"name\": Dylos25, \"tags\": {\"Bin\":\"bin4\"}, \"aggregators\": [{\"name\": \"avg\", \"align_sampling\": \"true\", \"sampling\": {\"value\": 1, \"unit\": \"hours\"}}]},
{\"name\": Dylos25, \"tags\": {\"Temp\":\"temp\"}, \"aggregators\": [{\"name\": \"avg\", \"align_sampling\": \"true\", \"sampling\": {\"value\": 1, \"unit\": \"hours\"}}]},
{\"name\": Dylos25, \"tags\": {\"RH\":\"rh\"}, \"aggregators\": [{\"name\": \"avg\", \"align_sampling\": \"true\", \"sampling\": {\"value\": 1, \"unit\": \"hours\"}}]}]}"
handle_setopt(h, URL = "https://replicant.deohs.washington.edu/api/v1/datapoints/query")
handle_setopt(h, CAINFO = "C://Users//Elena//OneDrive//Documents//UW Postdoc//KairosScripts//cacert4.pem")
handle_setopt(h, USERPWD = "")
handle_setopt(h, POSTFIELDS = data)
handle_setopt(h, POST = 1)
req <- curl_fetch_memory("https://replicant.deohs.washington.edu/api/v1/datapoints/query", handle = h)

cat(rawToChar(req$content),file="output.txt")

dkairos<-read.table("output.txt",header=F)

#find "[[" pattern in data to seperate into bins:
ind.start<-as.vector(gregexpr("\\[\\[",unlist(dkairos))[[1]])
ind.end<-as.vector(gregexpr("\\]\\]",unlist(dkairos))[[1]])

results<-list()

#seperate different bins into seperate data frames
for (i in 1:(length(ind.start))) {
  
  #select chunks
  temp<-substring(unlist(dkairos), ind.start[1]+1,ind.end[i])
  #remove [ and ] characters
  temp<-gsub("\\["," ", temp)
  temp<-gsub("\\]"," ", temp)
  
  temp<-data.frame(as.vector(as.data.frame(unlist(temp))))
  head(temp[1,]
  
}
  

substring(unlist(dkairos), 1,1)

substring("apples are good",c(1,8),c(1,8))


