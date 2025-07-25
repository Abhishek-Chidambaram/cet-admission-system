# Known Bugs in our CET Admission System

## Bug #1: Course Preference Validation Issue
**Location**: student/views.py (ApplicationView.get_context_data())

**Description**: The system doesn't properly validate if selected course preferences are still available or if the institution/course combination exists in the database.

**Impact**: Students may select course preferences that are no longer valid, potentially causing complications during the counseling process.
**Code Reference**: 
```python
current_prefs = [
    pref for pref in self.object.course_preferences 
    if pref and isinstance(pref, str) and '_' in pref and len(pref) > 3
]
```

**Steps to reproduce the Bug**: 
1. Add a course preference
2. Delete that course from admin panel
3. The preference will still show in student's list but won't work during counseling

## Bug #2: Document Upload File Size Validation Missing
**Location**: student/models.py and student/views.py (DocumentUploadView)

**Description**: No proper file size validation for document uploads, which could lead to server storage issues.

**Impact**: Users could upload very large files, potentially consuming excessive server storage and causing performance issues.

**Steps to reproduce the Bug**: 
1. Try uploading a very large file (>10MB)
2. System will accept it without any size restrictions

## Bug #3: Counseling Algorithm Tie-Breaking Issue
**Location**: admission/views.py (RunSpecificRoundView)

**Description**: When students have identical CET ranks, the seat allocation algorithm doesn't have a proper tie-breaking mechanism.

**Impact**: Students with same ranks might get unpredictable or inconsistent seat allocation order.

**Code Reference**:
```python
eligible_students = StudentProfile.objects.filter(
    cet_score__isnull=False
).order_by('cet_score__overall_rank')
```

**Steps to reproduce the Bug**: 
1. Create multiple students with identical CET ranks
2. Run counseling round
3. The allocation order might be inconsistent between runs

## Bug #4: Category Handling Edge Case
**Location**: Multiple files in counseling logic

**Description**: The system uses `student.category or 'GENERAL'` which could cause issues if category is an empty string rather than None.

**Impact**: Students with empty string category might not get proper category-based seat allocation.

**Code Reference**:
```python
student_category = student.category or 'GENERAL'
```

**Problem**: Empty string "" would still be truthy, but None would default to 'GENERAL'

**Steps to reproduce the Bug**: 
1. Set a student's category to empty string ""
2. Run counseling - the student won't get GENERAL category treatment

## How we are planning to Fix it:
1. **Course Validation**: Add real-time validation to check if selected courses still exist in database
2. **File Size Limit**: Implement MAX_UPLOAD_SIZE validation in document upload
3. **Tie-breaking**: Add secondary sorting criteria like application submission time or student ID
4. **Category Handling**: Use proper null checking: `student.category if student.category else 'GENERAL'`
