This file was written by Jacob Goldverg with UB number 50218299, for CSE 460 project under team Sona.

1. The DataSource used for the project

    The data was provided by John Hopkins University. The school manages this Github repository containing data revolving cases of COVID-19.
    The Github link: https://github.com/CSSEGISandData/COVID-19.

    For my project I decided to write a python cli called importer.py that helps manage the data inside of my local deployed of postgresql.
    To deploy postgres locally I use Docker with the following command: 
                docker run --name sona460-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres -p 5432:5432
    This deploys a local instance of postgres on your machine consuming port 5432. Password and database are created at runtime and not on db start.
    