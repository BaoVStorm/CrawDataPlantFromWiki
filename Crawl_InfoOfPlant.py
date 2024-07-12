import requests
import pandas as pd
from bs4 import BeautifulSoup

dic_style = {
    "name" : "padding:12px;text-align:center;vertical-align:middle;line-height:1.1em;font-size:135%;font-weight:bold;color:black;background: rgb(180,250,180);",
    "picture" : "text-align:center",
    "title" : "text-align:center;padding:5px;background: rgb(180,250,180);"
}
dic_title = {
    "ttbt" : "Tình trạng bảo tồn",
    "plkh" : "Phân loại khoa học"
}

def save_to_txt(content, file_path, name):
    try:
        with open(file_path + name, 'a+', encoding='utf-8') as file_write:    
            file_read = open(file_path + name, 'r', encoding='utf-8')
            read = file_read.read().split("\n")
            
            if read.count(content) == 0:
                file_write.write(content + "\n")
                print(f"*Thêm thành công: {file_path + name}")
        
    except IOError:
        print(f"*Lỗi: Không thể ghi vào file {name}!")

def Get_InfoOfPlant(url, file_path):
    response = requests.get(url)

    if response.status_code != 200:
        print("Không thể truy cập web!")
        return
    
    soup = BeautifulSoup(response.content, "html.parser")

    if not soup.find("table", class_="infobox taxobox"):
        print("Wiki Không có Bảng Thông tin về cây")
        return
    
    table = soup.find("table", class_="infobox taxobox").find("tbody")
    rows = table.find_all("tr")

    # 
    name_index = -1
    pic_index = -1
    ttbt_index = -1 # Trình trạng bảo tồn
    plkh_index = -1 # Phân loại khoa học

    for i, row in enumerate(rows):
        data = row.find("th", style = dic_style["name"])
        if data:
            name_index = i
            continue
            
        data = row.find("td", style = dic_style["picture"])
        if data:
            if data.find("span", typeof="mw:File"):
                pic_index = i
            continue
            
        data = row.find("th", style = dic_style["title"])
        if data:
            if data.text.strip() == dic_title["plkh"]:
                plkh_index = i + 1
            elif data.text.strip() == dic_title["ttbt"]:
                ttbt_index = i + 1
    
    # 
    name = ""
    pic_plant = ""
    pic_ttbt = ""
    name_ttbt = ""
    out = ""

    if not name_index == -1:
        name = rows[name_index].text.strip()
        save_to_txt(name, file_path, "name.txt")

        out = f"Name: {name}\n"
    
    if not pic_index == -1:
        pic_plant = rows[pic_index].find("td").find("span").find("a").find("img").get("srcset")
        if not pic_plant:
            pic_plant = rows[pic_index].find("td").find("span").find("a").find("img").get("src")
        else:
            pic_plant = pic_plant.split(" 2x")[0]
            default = pic_plant
            pic_plant = pic_plant.split("1.5x, ")
            if 1 < len(pic_plant):
                pic_plant = pic_plant[1]
            else:
                pic_plant = default.split("1.5x")[0]

        save_to_txt(pic_plant, file_path, "pic_wiki.txt")

        out += f"source_pic: {pic_plant}\n"
    
    if not ttbt_index == -1:
        data = rows[ttbt_index].find("td").find("div")
        name_ttbt = data.find("a").text.strip()

        pic_ttbt = data.find("span").find("span").find("img").get("srcset")
        if not pic_ttbt:
            pic_ttbt = data.find("span").find("span").find("img").get("src")
        else:
            pic_ttbt = pic_ttbt.split(" 2x")[0]
            pic_ttbt = pic_ttbt.split("1.5x, ")[1]

        save_to_txt(f"{pic_ttbt}\n{name_ttbt}", file_path, "ttbt.txt")

        out += f"source_ttbt_pic: {pic_ttbt}\
            \nname_ttbt_pic: {name_ttbt + " (IUCN 2.3)"}\n"
    
    Gioi = []
    Bo = ""
    Ho = ""
    Chi = ""
    Loai = ""

    if not plkh_index == -1:
        for i in range(plkh_index, len(rows)):
            row = rows[i]
            if row.find("th", scope="row"):
                # if row.find("th").find("a").text.strip() == "Giới" or row.find("th").find("span").text.strip() == "(không phân hạng)":
                #     Gioi.append(row.find("td").find("a").text.strip())
                if row.find("th").text.strip() == "(không phân hạng)":
                    Gioi.append(row.find("td").find("a").text.strip())
                elif row.find("th").find("a").text.strip() == "Bộ":
                    Bo = row.find("td").find("a").text.strip()
                elif row.find("th").find("a").text.strip() == "Họ":
                    Ho = row.find("td").find("a").text.strip()
                elif row.find("th").find("a").text.strip() == "Chi":
                    if row.find("td").find("a"):
                        Chi = row.find("td").find("a").text.strip()
                    elif row.find("td").find("i"):
                        Chi = row.find("td").find("i").text.strip()
                elif row.find("th").find("a").text.strip() == "Loài":
                    Loai = row.find("td").find("i").text.strip()    
            else:
                break
    
    if not len(Gioi) == 0:
        for Gioi_Row in Gioi:
            save_to_txt(Gioi_Row, file_path, "Gioi.txt")
            save_to_txt(Gioi_Row, "", "Gioi.txt")
        out += f"Gioi: {", ".join(Gioi)}\n"
    if not Bo == "":
        save_to_txt(Bo, file_path, "Bo.txt")
        save_to_txt(Bo, "", "Bo.txt")
        out += f"Bo: {Bo}\n"
    if not Ho == "":
        save_to_txt(Ho, file_path, "Ho.txt")
        save_to_txt(Ho, "", "Ho.txt")
        out += f"Ho: {Ho}\n"
    if not Chi == "":
        save_to_txt(Chi, file_path, "Chi.txt")
        save_to_txt(Chi, "", "Chi.txt")
        out += f"Chi: {Chi}\n"
    if not Loai == "":
        save_to_txt(Loai, file_path, "Loai.txt")
        save_to_txt(Loai, "", "Loai.txt")
        out += f"Loai: {Loai}\n"
   
    out += "\n"
    print(out)

readfile = r"D:\Homework\NC\Task1_FindImageFromScienceName\science-name-for-plant.csv"

data = pd.read_csv(readfile)

DefaultUrl_ViWiki = r"https://vi.wikipedia.org/wiki/"

for i in range(622, len(data), 2):
    Name_Plant = data.loc[i, 'Science name'].replace(" ", "_")

    url = DefaultUrl_ViWiki + Name_Plant
    
    print(f"--Đang duyệt cây có STT: {i + 1} -----")
    Get_InfoOfPlant(url, f'.\\images\\{Name_Plant}\\')

