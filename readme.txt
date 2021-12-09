This file was written by Jacob Goldverg with UB number 50218299, for CSE 460 project under team Sona.

1. The DataSource used for the project

    The data was provided by John Hopkins University. The school manages this Github repository containing data revolving cases of COVID-19.
    The Github link: https://github.com/CSSEGISandData/COVID-19.

    For my project I decided to write a python cli called importer.py that helps manage the data inside of my local deployed of postgresql.
    To deploy postgres locally I use Docker with the following command: 
                docker run --name sona460-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres -p 5432:5432
    This deploys a local instance of postgres on your machine consuming port 5432. Password and database are created at runtime and not on db start.

2. The cli is POSIX style, here are the example usages of the cli:
Usage:
    importer.py load_csv <file_path>
    importer.py get_date [--year=year_covid --month=month_covid --day=day_covid [default: --year=0, --month=0, --day=0]]
    importer.py drop_table <tablename>
    importer.py drop_column <tablename> <columnname>
    importer.py alter_covid_table
    importer.py stats <state> <column_name>
    importer.py print_table_stats [--table_name=table_name] 
    importer.py sign_up --username=username --password=password
    importer.py sign_in --username=username --password=password

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --year=year_covid         The year you are searching for [default: 2020]
  --day=day_covid           The day [default: 0]
  --month=month_covid       The month [default: 0]
  --table_name=table_name   The name of the table you wish to use [default: coviddays]
  start-date                Is of form "year-month-day hr:min:sec"
  end-date                  Is of form "year-month-day hr:min:sec"
  year                      The year you want to aggregate results from
  file_path                 An absolute path to the csv file from John Hopkins you wish to read into postgres

  Steps to run:
  1) First please make sure you have postgresql running on localhost:5432 or please go into the code and in the main method swap the host and port appropriately
  For this project I used this docker command:
                docker run --name sona460-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres -p 5432:5432
  2) Download the csv files from and please make sure you know the absolute path. I am not sure how to run on Windows btw only for Linux as far as I can tell:
                 https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports_us
  3) Now that postgres is running lets first load in a file. Replace the path for the files from step 2.
                python3 importer.py load_csv /Users/jacobgoldverg/covidata/csse_covid_19_daily_reports_us/02-09-2021.csv
  4) Lets look at what kind of table we have(I will cover the sign in process below):
                python3 importer.py print_table_stats
  5) Using the date of the file you loaded into the database. Feel free to load in anymore files.
                python3 importer.py get_date --year 2021 --month 2 --day 10 
  6) Lets say you would like to view the  
   Login Example:
    1)Once postgres is running with the proper host and port in the cli. Try this to create a user in the DB.
            python3 importer.py sign_up --username jacob --password hello
    2)The user you just made already has the proper permissions so there is nothing extra to do.
            python3 importer.py sign_in --username jacob --password hello 