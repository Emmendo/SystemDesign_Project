You will need to download Anaconda (https://www.anaconda.com/download)
Do not make an account

You will also need a driver for SSMS - Download ODBC Driver 17 for SQL Server (not ODBC Driver 18!) (https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)

Once that is installed, please install SSMS (using SQL Express - https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16#download-ssms)


Restart computer once all three are downloaded

Now open SSMS
See the 'Connecting to SQL Server.txt'
You should be able to see the ParkingLot database now.

In the Code folder there is a .yaml file which contains the environment needed for anaconda, make sure it is in your Downloads folder.

Now open up 'Anaconda Prompt' from the Search Menu
Type in: cd %USERPROFILE%\Downloads
The above will navigate it to your Downloads folder

Then enter this: conda env create -f SysDesign_SMS.yaml
This will find the .yaml file and create a new environment in Anaconda

Then type: conda activate SysDesign_SMS

Download the .py file in the Code folder

Now search for 'Anaconda Navigator', now open it up and on the Home screen at the top it will say 'All Applications on ____" choose the second drop down and choose SysDesign_SMS. This lets you choose the environment, let it load then select Spyder.


Once Spyder opens, go to file and open, then click the .py file from your downloads. Then click run. 