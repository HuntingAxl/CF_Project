#!/bin/bash

# Use cURL
mkdir 'Data'
cd 'Data'

start_date=`date -d 01-Jan-2000 '+%Y%m%d'`
final_date=`date -d 25-Oct-2018 '+%Y%m%d'`

for mf in 39 3 50 1 53 4 36 59 46 32 60 31 38 58 6 47 54 40 51 27 8 49 9 37 20 57 48 68 62 11 65 63 14 42 70 16 43 17 56 18 69 45 19 55 44 34 64 10 13 41 21 35 22 52 67 66 2 24 33 25 26 61 28 29
do
    result=`mkdir $mf`
    
    current_date=`date -d $start_date '+%Y%m%d'` 
    end_date=`date -d $current_date'+90 days' '+%Y%m%d'`

    echo $mf' is being Downloaded...'
    
    while [ $current_date -lt $final_date ];
    do
        if [ $end_date -gt $final_date ]
        then 
            end_date=$final_date
        fi
        
        data_file_name=$current_date'_'$end_date
        frmdt=`date -d $current_date '+%d-%b-%Y'`
        todt=`date -d $end_date '+%d-%b-%Y'`
        
        echo $data_file_name' is being downloaded...'

        for i in 1 2
        do
            echo `curl 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf='+$mf+'&tp='+$i+'&frmdt='+$frmdt+'&todt='+$todt -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' -H 'Upgrade-Insecure-Requests: 1' -H 'DNT: 1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/69.0.3497.100 Chrome/69.0.3497.100 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7' -H 'Cookie: ASP.NET_SessionId=n0kw0n55o2a1rljykoqnuwik' --compressed` > $mf'/'$data_file_name'_'$i
        done

        current_date=`date -d $end_date'+ 1 day' '+%Y%m%d'` 
        end_date=`date -d $current_date'+90 days' '+%Y%m%d'`
    done
done
