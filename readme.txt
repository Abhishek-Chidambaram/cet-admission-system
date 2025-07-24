Known Bugs in Our CET Admission System
Bug #1: Invalid Course Preferences Not Caught
Where it happens: student/views.py (in ApplicationView.get_context_data())
What’s wrong: The system doesn’t check whether the course or institution a student selected still exists in the database.
Why it’s a problem: Students can end up selecting course options that no longer exist. This leads to issues during the counseling rounds when the system tries to allocate those non-existent preferences.
Code Snippet:

current_prefs = [
    pref for pref in self.object.course_preferences 
    if pref and isinstance(pref, str) and '_' in pref and len(pref) > 3
]
Steps to see the bug:

A student adds a course preference.

An admin later deletes that course from the backend.

The preference still appears on the student’s dashboard, but it breaks the counseling process later.

Bug #2: No File Size Check on Document Uploads
Where it happens: student/models.py and student/views.py (DocumentUploadView)
What’s wrong: There's no limit on how large the uploaded files can be.
Why it’s a problem: Students can upload massive files (like >10MB), which can clog up server space and slow things down.
Steps to see the bug:

Go to the document upload section.

Try uploading a huge file.

You’ll see the system accepts it with no complaints — but it shouldn’t.

Bug #3: Tie-Breaking in Counseling Algorithm
Where it happens: admission/views.py (RunSpecificRoundView)
What’s wrong: When multiple students have the exact same CET rank, the algorithm doesn’t clearly decide who should get the seat first.
Why it’s a problem: Seat allocation becomes unpredictable and inconsistent between runs.
Code Snippet:

eligible_students = StudentProfile.objects.filter(
    cet_score__isnull=False
).order_by('cet_score__overall_rank')
Steps to see the bug:

Create two or more students with identical CET ranks.

Run a counseling round.

The results might randomly differ every time.

Bug #4: Category Handling Glitch
Where it happens: Several files in the counseling logic
What’s wrong: The logic uses student.category or 'GENERAL', which works fine unless the category is an empty string ("").
Why it’s a problem: An empty string isn’t None, so it bypasses the fallback and students might miss out on proper category-based seat allocation.
Code Snippet:

student_category = student.category or 'GENERAL'
Steps to see the bug:

Set a student’s category field to an empty string.

Run a counseling round.

The system won't treat them as GENERAL — they’ll be skipped from category-based rules.

How we are planning to Fix it:
Course Preference Validation: Add a check to ensure selected courses still exist in the database before submission.

File Upload Limit: Introduce a max file size limit (e.g., 2MB or 5MB) to prevent oversized uploads.

Tie-Breaker Logic: Add a secondary sort — like application submission time or student ID — to ensure fairness when ranks are the same.

Category Fix: Improve the fallback logic to correctly handle empty strings using:

student.category if student.category else 'GENERAL'
