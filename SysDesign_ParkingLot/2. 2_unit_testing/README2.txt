Unit Testing:
Definition - Small tests that result from a single unit (such as a function)



Parking Spot Availability: The functions get_car_spots_available and get_cycle_spots_available calculate available spots as (maximum spots minus current count from each table in the SSMS database).

Database Operations in code: 
- When a user submits vehicle details (for a car or cycle), the corresponding function (e.g. insert_car or insert_cycle) inserts the record into the database.
- Calling fetch_car_count and fetch_cycle_count returns the correct number of records stored in the database tables after multiple insertions.

Payment Processing:
- When processing a card payment, the UI first displays a "Processing payment" screen for a defined duration (e.g. 3 seconds) before transitioning to a "Payment Successful" screen.
- In the cash payment process, entering an amount less than $15 triggers a warning; exactly $15 should proceed without dispensing change; and more than $15 should dynamically calculate and display the change due before printing the ticket.

Vehicle Information Submission:
The vehicle detail submission function verifies that all fields (make, model, color) are filled before proceeding.