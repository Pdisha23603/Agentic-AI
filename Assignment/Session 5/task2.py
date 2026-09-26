# -------- IPL TICKET BOOKING STATE MACHINE --------

transitions = {
    "Start": "Select Match",
    "Select Match": "Choose Seats",
    "Choose Seats": "Payment",
    "Payment": "Confirmation"
}

current_state = "Start"

print("Current State:", current_state)

while current_state != "Confirmation":

    input("\nPress Enter to continue...")

    current_state = transitions[current_state]

    print("Current State:", current_state)

print("\nIPL Ticket Booking Completed Successfully!")




# output:
# Current State: Start

# Press Enter to continue...
# Current State: Select Match

# Press Enter to continue...
# Current State: Choose Seats

# Press Enter to continue...
# Current State: Payment

# Press Enter to continue...
# Current State: Confirmation

# IPL Ticket Booking Completed Successfully!