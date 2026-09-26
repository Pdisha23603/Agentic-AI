# ============================================
# Task 5: Extract BookMyShow Ticket Details
# ============================================

import PyPDF2
import re


def extract_ticket_details(pdf_path):
    """
    Extract Movie Name, Seat Number, and Showtime
    from a BookMyShow-style PDF ticket.
    """

    reader = PyPDF2.PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Regular Expressions
    movie = re.search(r"Movie Name:\s*(.*)", text)
    seat = re.search(r"Seat Number:\s*(.*)", text)
    showtime = re.search(r"Show Time:\s*(.*)", text)

    ticket_info = {
        "movie_name": movie.group(1).strip() if movie else "Not Found",
        "seat_number": seat.group(1).strip() if seat else "Not Found",
        "show_time": showtime.group(1).strip() if showtime else "Not Found"
    }

    return ticket_info


# Example
ticket = extract_ticket_details("BookMyShow_Ticket_Sample.pdf")

print("===== BookMyShow Ticket Details =====")

for key, value in ticket.items():
    print(f"{key} : {value}")