import os
import zipfile
from collections import defaultdict
from datetime import datetime


main_zip_file = r"C:\Users\karin\Work\Moniepoint\mp-hackathon-sample-data.zip"
inner_zip_file = "hackathon-sample-data"
extracted_test_files = "test-cases"

os.makedirs(inner_zip_file, exist_ok=True) 

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

extract_zip(main_zip_file, inner_zip_file)

os.makedirs(extracted_test_files, exist_ok=True) 

for filename in os.listdir(inner_zip_file):
    file_path = os.path.join(inner_zip_file, filename)
    extract_zip(file_path, extracted_test_files)

print("ZIP files are ready!")


target_year = int(input("Enter the year to process transactions for: "))

daily_sale_volume = defaultdict(int)
daily_sale_value = defaultdict(float)
product_sales = defaultdict(int)
staff_sales = defaultdict(dict)
monthly_hourly_sales_volume = defaultdict(dict)  
monthly_hourly_transaction_count = defaultdict(dict) 
monthly_sales_volume = defaultdict(dict) 


def process_transaction_file(file_path):
    print(f"Processing: {file_path}")

    with open(file_path, 'r') as file:
        for line in file:
            print(f"Raw Line: {line}") 
            parts = line.strip().split(',')
            if len(parts) != 4:
                continue  # ignore incomplete data

            try:
                sales_staff_id = int(parts[0])
                timestamp = datetime.fromisoformat(parts[1])

                if timestamp.year != target_year:  # ignore other transactions that are not for required year
                    continue

                product_data = parts[2].strip('[]').split('|')
                sale_amount = float(parts[3])

                date_key = timestamp.date().isoformat()
                hour = timestamp.hour
                month_key = timestamp.strftime('%Y-%m')

                daily_sale_value[date_key] += sale_amount
                
                total_items = 0
                for product in product_data:
                    split_product = product.split(':')
                    product_id = int(split_product[0])
                    quantity = int(split_product[1])
                    product_sales[product_id] += quantity
                    total_items += quantity
                
                daily_sale_volume[date_key] += total_items
            
                if hour not in monthly_hourly_sales_volume[month_key]:
                    monthly_hourly_sales_volume[month_key][hour] = 0
                if hour not in monthly_hourly_transaction_count[month_key]:
                    monthly_hourly_transaction_count[month_key][hour] = 0
                if date_key not in monthly_sales_volume[month_key]:
                    monthly_sales_volume[month_key][date_key] = 0


                monthly_hourly_sales_volume[month_key][hour] += total_items
                monthly_hourly_transaction_count[month_key][hour] += 1
                monthly_sales_volume[month_key][date_key] += total_items


                # update staff sale monthly
                if sales_staff_id not in staff_sales[month_key]: 
                    staff_sales[month_key][sales_staff_id] = 0.0
                staff_sales[month_key][sales_staff_id] += sale_amount

            except ValueError as e:
                print(f"Skipping invalid line in {file_path}: {line.strip()} (Error: {e})")

# file processing
data_dir = extracted_test_files
print(f"Files in directory: {os.listdir(data_dir)}") 

for filename in os.listdir(data_dir):
    if filename.endswith(".txt"):
        process_transaction_file(os.path.join(data_dir, filename))

# Computing the required parameters
# if not daily_sale_volume:
#     print(f"No valid transactions found for {target_year}. No data to compute.")
#     exit()



highest_sales_day = max(daily_sale_volume, key=daily_sale_volume.get, default="N/A")
highest_value_day = max(daily_sale_value, key=daily_sale_value.get, default="N/A")
most_sold_product = max(product_sales, key=product_sales.get, default="N/A")
top_staff_per_month = {month: max(staff, key=staff.get) for month, staff in staff_sales.items() if staff}


# printing the results
print(f"Highest Sales Volume Day: {highest_sales_day} ({daily_sale_volume.get(highest_sales_day, 0)} items)")
print(f"Highest Sales Value Day: {highest_value_day} (${daily_sale_value.get(highest_value_day, 0):.2f})")
print(f"Most Sold Product ID: {most_sold_product} ({product_sales.get(most_sold_product, 0)} units)")

print("Highest sales staff ID for each month:")
for month, staff_id in top_staff_per_month.items():
    print(f"  {month}: Staff ID {staff_id}")

print("\nBusiest Day and Hour per Month:")
for month in busiest_hours_per_month:
    print(f"  {month}: Busiest Day: {busiest_days_per_month[month]}, Busiest Hour: {busiest_hours_per_month[month]}:00")
