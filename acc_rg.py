from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

# Tên file CSV chứa thông tin đăng ký tài khoản
input_file = "create_rg.csv"

# Đường dẫn tới file chromedriver.exe trên máy tính
chromedriver_path = "chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument('headless')

# Khởi tạo trình duyệt Chrome với đường dẫn tới chromedriver.exe
driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)

# Truy cập trang đăng ký tài khoản
driver.get("http://localhost:8000/account/register/")
data=[]
# Mở file CSV đầu vào để đọc dữ liệu
with open(input_file, mode="r", encoding="utf-8", newline="") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        data.append(row)

    # Bỏ qua tiêu đề
    

    # Đếm số lượng tài khoản được đăng ký thành công
    successful_count = 0

    # Đọc và xử lý từng dòng dữ liệu trong file CSV đầu vào
    for row in data:
        # Lấy các thông tin từ file CSV
        last_name = row['last_name']
        first_name = row['first_name']
        email = row['email']
        password = row['password']
        phone_number = row['phone']

        # Điền thông tin vào form đăng ký
        fields = ["last_name", "first_name", "email", "password", "phone"]
        for field in fields:
            driver.find_element(By.NAME, field).send_keys(row[field])

        # Nhấn nút đăng ký
        driver.find_element(By.NAME, 'login').click()

        # Chờ cho trang đăng ký được load lại hoàn toàn
        driver.implicitly_wait(10)

        # Kiểm tra xem đăng ký thành công hay không
        if "register" not in driver.current_url:
            successful_count += 1
            driver.get("http://localhost:8000/account/register/")
        else:
            print("Đăng ký thất bại!")
            break

        # Xóa giá trị trên các khung nhập liệu để chuẩn bị cho đăng ký tài khoản tiếp theo
        for field in fields:
            driver.find_element(By.NAME, field).clear()

        driver.get("http://localhost:8000/account/register/")

    # Thông báo kết quả đăng ký
    
    if successful_count == len(data):
        print("Đăng ký tất cả các tài khoản thành công!")
    elif successful_count == 0:
        print("Không đăng ký được bất kỳ tài khoản nào!")
    else:
        print(f"Đăng ký thành công {successful_count}/{len(csv_reader)} tài khoản.")
