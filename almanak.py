import streamlit as st
import pandas as pd
import re
from datetime import date

# Excel dosyasını oku
df = pd.read_excel("almanak.xlsx")

# Tarih temizleme
df["TarihTemiz"] = df["Tarih"].astype(str)

df["TarihTemiz"] = df["TarihTemiz"].str.replace(
    r"(Pazartesi|Salı|Çarşamba|Perşembe|Cuma|Cumartesi|Pazar)",
    "",
    regex=True
)

df["TarihTemiz"] = df["TarihTemiz"].str.strip()

aylar = {
    "Ocak":"01","Şubat":"02","Mart":"03","Nisan":"04",
    "Mayıs":"05","Haziran":"06","Temmuz":"07","Ağustos":"08",
    "Eylül":"09","Ekim":"10","Kasım":"11","Aralık":"12"
}

for ay,num in aylar.items():
    df["TarihTemiz"] = df["TarihTemiz"].str.replace(ay,num)

df["TarihTemiz"] = pd.to_datetime(df["TarihTemiz"], dayfirst=True, errors="coerce")

st.title("2018 Haber Almanak")

default_start = date(2018,1,1)
default_end = date(2018,12,31)

start = st.date_input("Başlangıç Tarihi", value=default_start)
end = st.date_input("Bitiş Tarihi", value=default_end)

# -------------------
# KATEGORİ FİLTRELERİ
# -------------------

k1 = st.selectbox("Kategori 1",["Tümü"]+sorted(df["Kategori1"].dropna().unique()))

if k1=="Tümü":
    k2_options=sorted(df["Kategori2"].dropna().unique())
else:
    k2_options=sorted(df[df["Kategori1"]==k1]["Kategori2"].dropna().unique())

k2=st.selectbox("Kategori 2",["Tümü"]+k2_options)

if k2=="Tümü":
    k3_options=sorted(df["Kategori3"].dropna().unique())
else:
    k3_options=sorted(df[df["Kategori2"]==k2]["Kategori3"].dropna().unique())

k3=st.selectbox("Kategori 3",["Tümü"]+k3_options)

if k3=="Tümü":
    k4_options=sorted(df["Kategori4"].dropna().unique())
else:
    k4_options=sorted(df[df["Kategori3"]==k3]["Kategori4"].dropna().unique())

k4=st.selectbox("Kategori 4",["Tümü"]+k4_options)

# -------------------
# ARAMA KUTUSU
# -------------------

search_text = st.text_input("Haberlerde ara")

# -------------------
# FİLTRE UYGULA
# -------------------

if st.button("Uygula"):

    filtre=df.copy()

    filtre=filtre[
        (
            (filtre["TarihTemiz"]>=pd.to_datetime(start)) &
            (filtre["TarihTemiz"]<=pd.to_datetime(end))
        )
        |
        (filtre["TarihTemiz"].isna())
    ]

    if k1!="Tümü":
        filtre=filtre[filtre["Kategori1"]==k1]

    if k2!="Tümü":
        filtre=filtre[filtre["Kategori2"]==k2]

    if k3!="Tümü":
        filtre=filtre[filtre["Kategori3"]==k3]

    if k4!="Tümü":
        filtre=filtre[filtre["Kategori4"]==k4]

    # -------------------
    # ARAMA MOTORU
    # -------------------

    if search_text.strip()!="":

        phrase_matches=re.findall(r'"([^"]+)"',search_text)
        remaining=re.sub(r'"[^"]+"',"",search_text).split()

        mask=pd.Series(True,index=filtre.index)

        for phrase in phrase_matches:
            mask &= filtre["Baslik"].str.contains(phrase,case=False,na=False)

        for word in remaining:
            mask &= filtre["Baslik"].str.contains(word,case=False,na=False)

        filtre=filtre[mask]

    filtre=filtre.sort_values("TarihTemiz")

    st.write(f"Toplam {len(filtre)} haber bulundu")
    st.write("---")

    for _,row in filtre.iterrows():
        st.markdown(
            f"**{row['Tarih']}**  \n[{row['Baslik']}]({row['Link']})"
        )