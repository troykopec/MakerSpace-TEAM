# MakerSpace-TEAM
#
# After downloading, to set up the app you must create a virtual enviroment shown in the link:
#      https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/
#
# After doing this you can now run the command 'venv\Scripts\activate' in the console of the 
# MakerSpace Folder. This will start your virtual environment.
#
# After this you can install all of our required dependencies in requirements.txt by    #performing the command "pip install -r requirements.txt"
#
# Once this is set, you need to get MySQL and create a local instance. Then point your code in app.py to this MySQL Server in the line : app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://#root:Maker_Space_Password687737!@localhost/our_users'
#
# This will create your database. Now you need to upgrade your database with all of the db Models. If you havent already run 'flask run' in the console, make sure you already performed the command to start the virtual server.
#
# After this press Ctrl+C to exit out of the flask run. Now type the command 'flask db init', then 'flask db migrate -m "Initial Migration"', and finnally 'flask db upgrade'. This should add all of the needed Database Tables to the MySQL Server that is connected.
#
# Now you may think everything will work as planned but you must add your google calendar API. This may take a lot of steps so follow googles documentation here : https://developers.google.com/drive/api/quickstart/python
#
# After this you should have the working app up and running. Great Job!
#
# At first you may think "Hey! how do I create an account if no users are in the database!". Dont worry, to create the first account, allowing you to create others, go to the signup page. Enter 'admin' for the username, your email for the email and whatever password you want. The code is set to allow the username admin to be created without authentication if there is no other user named admin! so dont change the 'admin' username or you may give access for another to create an admin account!
#
#
#
