import os
import uuid

def generate_unique_dir():
    while True:
        unique_uuid = str(uuid.uuid4())
        dir = os.path.join(os.getcwd(), 'tmp', unique_uuid)

        if not os.path.exists(dir):
            os.makedirs(dir)
            break

    return dir