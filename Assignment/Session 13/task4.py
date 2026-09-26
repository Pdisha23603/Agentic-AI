# ============================================
# Task 4: Task Completion Rate
# ============================================

total_tasks = 20
completed_tasks = 15
partially_completed = 2

# Half credit for partial completion
completed_score = completed_tasks + (partially_completed * 0.5)

completion_rate = (completed_score / total_tasks) * 100

print("========== Task Completion Report ==========")
print("Total Tasks            :", total_tasks)
print("Completed Tasks        :", completed_tasks)
print("Partially Completed    :", partially_completed)
print("Completion Score       :", completed_score)
print(f"Task Completion Rate   : {completion_rate:.2f}%")