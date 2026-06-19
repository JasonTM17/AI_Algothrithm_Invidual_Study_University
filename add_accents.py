import sys
import re

file_path = r'd:\Trí tuệ nhân tạo AI lỏ\thu_duc_graph_coloring.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'Linh Xuan': 'Linh Xuân',
    'Binh Chieu': 'Bình Chiểu',
    'Linh Trung': 'Linh Trung',
    'Tam Binh': 'Tam Bình',
    'Tam Phu': 'Tam Phú',
    'Hiep Binh Phuoc': 'Hiệp Bình Phước',
    'Hiep Binh Chanh': 'Hiệp Bình Chánh',
    'Linh Dong': 'Linh Đông',
    'Linh Tay': 'Linh Tây',
    'Linh Chieu': 'Linh Chiểu',
    'Truong Tho': 'Trường Thọ',
    'Binh Tho': 'Bình Thọ',
    'An Binh': 'An Bình',
    'Phuoc Long A': 'Phước Long A',
    'Phuoc Long B': 'Phước Long B',
    'Tang Nhon Phu B': 'Tăng Nhơn Phú B',
    'Tang Nhon Phu A': 'Tăng Nhơn Phú A',
    'Hiep Phu': 'Hiệp Phú',
    'Phuoc Binh': 'Phước Bình',
    'Phu Huu': 'Phú Hữu',
    'Long Truong': 'Long Trường',
    'Truong Thanh': 'Trường Thạnh',
    'Long Phuoc': 'Long Phước',
    'Long Binh': 'Long Bình',
    'Xanh ngoc': 'Xanh ngọc',
    'Vang dat': 'Vàng đất',
    'Do gach': 'Đỏ gạch',
    'Tim than': 'Tím than',
    'Xanh troi': 'Xanh trời',
    'Hong sen': 'Hồng sen'
}

for k, v in replacements.items():
    content = content.replace(f'"{k}"', f'"{v}"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
