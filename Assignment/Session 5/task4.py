# -------- SAFE AGENT LOOP --------

# Simple Agent Class
class Agent:

    def __init__(self):
        self.current_step = 0

    def next_step(self):
        self.current_step += 1

        # Stop after 3 steps
        if self.current_step == 3:
            return {"done": True}

        return {"done": False}


# Create agent object
agent = Agent()

done = False
step_count = 0

while not done:

    action = agent.next_step()

    done = action["done"]

    step_count += 1

    print("Step:", step_count)

    # Safety Check
    if step_count >= 5:
        print("Maximum 5 steps reached. Stopping agent.")
        break

# Final message
if done:
    print("Agent completed the task successfully.")






# output
# Step: 1
# Step: 2
# Step: 3
# Agent completed the task successfully.