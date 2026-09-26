# ============================================
# Task 5: Flipkart Review Agent Event Loop
# ============================================

# Step 1: Read new Flipkart product reviews
reviews = read_new_reviews()

delivery_complaints = []

# Step 2: Process each review
for review in reviews:

    # Step 3: Check if review mentions delivery issues
    if is_delivery_issue(review):

        # Step 4: Save complaint
        log_delivery_complaint(review)

        delivery_complaints.append(review)

# Step 5: Generate summary report
print("Delivery Complaint Report")
print("Total Reviews:", len(reviews))
print("Delivery Complaints:", len(delivery_complaints))

for complaint in delivery_complaints:
    print("-", complaint)