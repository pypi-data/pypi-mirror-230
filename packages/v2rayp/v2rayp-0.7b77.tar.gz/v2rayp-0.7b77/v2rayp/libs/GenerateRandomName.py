import os
import random
import string
import uuid


def generate_random_alphanumeric(length=5):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def generate_random_filename():
    random_uuid = uuid.uuid4()
    filename = str(random_uuid)
    return filename[0:5]


if __name__ == "__main__":
    random_filename = generate_random_filename()
    print("Random Filename:", random_filename[0:5])
    # Generate a random 5-digit alphanumeric string
    random_5_digit_alphanumeric = generate_random_alphanumeric()
    print("Random 5-digit Alphanumeric:", random_5_digit_alphanumeric)
