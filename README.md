# validusrm
Deposit and withdrawal site for investments

First navigate to the root directory.

Run these commands to use the server:
source venv/bin/activate
python manage.py migrate
python manage.py migrate --run-syncdb
python manage.py runserver

Using a web browser, navigate to http://127.0.0.1:8000/investments
Now you can deposit using the supplied fields to add to the database.
Do this multiple times until you're happy your funds and investments are recorded well; the investments page should refresh with updated data as you add it.

Now you can withdraw from a particular investment.  It should take your investments from the relevant funds and commitments within that investment in date order in 
the form of FIFO (First In First Out).

Enjoy!

PS to run the test cases you need the following command:
python manage.py test validusrm.test_cases
