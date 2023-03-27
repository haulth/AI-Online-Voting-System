import csv
import random
from unidecode import unidecode
# Tên file CSV ban đầu chứa họ và tên người dùng
input_file = "data.csv"

# Tên file CSV mới chứa thông tin đầy đủ người dùng
output_file = "create_rg.csv"

# Mở file CSV đầu vào để đọc dữ liệu
with open(input_file, mode="r", encoding="utf-8", newline="") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    
    # Mở file CSV đầu ra để ghi dữ liệu
    with open(output_file, mode="w", encoding="utf-8", newline="") as new_file:
        fieldnames = [
            "last_name","first_name", "email","password","phone"
        ]
        writer = csv.DictWriter(new_file, fieldnames=["last_name", "first_name", "email", "password", "phone"])
        
        # # Ghi phần header cho file CSV đầu ra
        writer.writeheader()
        
        # Đọc và xử lý từng dòng dữ liệu trong file CSV đầu vào
        for row in csv_reader:
            # Tách họ và tên từ dòng dữ liệu
            full_name = row[0]
            first_name, last_name = full_name.split(maxsplit=1)
            last_name = last_name.split()[-1]
            
            # Random email
            email = unidecode(first_name.lower()) + '@gmail.com'

            # Random phone
            prefix = random.choice(['09', '03', '08'])
            suffix = ''.join(random.choice('0123456789') for _ in range(8))
            phone = prefix + suffix
            
            # Ghi thông tin người dùng mới vào file CSV đầu ra
            writer.writerow({
               
                "last_name": last_name,
                "first_name": first_name,
                "email": email,
                "password": "123456",
                "phone":phone,

             
            })
