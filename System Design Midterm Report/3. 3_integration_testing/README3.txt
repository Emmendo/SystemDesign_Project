Integration Testing:
Definition - Tests that aggregate results from various parts and sources.

- Inbox: The inbox is dynamic for each user, connected to the database which stores all messages (Message_ID) and threads (Thread_ID). The user can compose a new message as well to another user within the campus directory. All messages are recorded back in the database table for Inbox_Messages.

- Quick Chat: A feature exclusive to students, which works as an IM system without having to go through all the steps of answering an inbox message. Allows for more collaborative work on whichever screen the student is on. For example, the student could be looking at assignment instructions and be able to use the Quick Chat feature, without having to open up an additional tab for their inbox. All messages are recorded back in the database table for Inbox_Messages, with the subject of "Quick Chat".

- Assignment Uploading: A student can submit an assignment (opens to their Downloads folder automatically) if the submission due date has not passed yet, which will be saved by the system and app until the teacher is able to leave a grade and feedback. (See in the folder the attached pdf that I will use for testing in the demo).

- Assignment Grading: A teacher will receive a notification if a student in their class has submitted an assignment before the due date (the status being updated). In which, they can click on it to download the student submission and a new screen pops up to leave feedback and a grade. This will be documented in the database automatically once the grade/feedback goes through.