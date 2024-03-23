import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Set tema seaborn
sns.set_theme(style='dark')

# Fungsi untuk menghitung total penggunaan sepeda per jam
def get_total_count_by_hour_df(hour_df):
    hour_count_df = hour_df.groupby(by="hours").agg({"count_cr": ["sum"]})
    return hour_count_df

# Fungsi untuk menghitung total penggunaan sepeda per hari dalam rentang tahun 2011
def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query('dteday >= "2011-01-01" and dteday < "2012-12-31"')
    return day_df_count_2011

# Fungsi untuk menghitung total penggunaan sepeda terdaftar per hari
def total_registered_df(day_df):
    reg_df = day_df.groupby(by="dteday").agg({
        "registered": "sum"
    })
    reg_df = reg_df.reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

# Fungsi untuk menghitung total penggunaan sepeda tidak terdaftar per hari
def total_casual_df(day_df):
    cas_df = day_df.groupby(by="dteday").agg({
        "casual": ["sum"]
    })
    cas_df = cas_df.reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

# Fungsi untuk menghitung jumlah pesanan per jam
def sum_order(hour_df):
    sum_order_items_df = hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# Fungsi untuk menghitung penggunaan sepeda berdasarkan musim
def macem_season(day_df):
    season_df = day_df.groupby(by="season").count_cr.sum().reset_index()
    return season_df

# Menggunakan try-except untuk membaca file CSV
try:
    days_df = pd.read_csv("dashboard/dashboard/day_clean.csv")
    hours_df = pd.read_csv("dashboard/dashboard/hour_clean.csv")
    
    # Mengubah kolom tanggal menjadi tipe data datetime
    datetime_columns = ["dteday"]
    days_df[datetime_columns] = days_df[datetime_columns].apply(pd.to_datetime)
    hours_df[datetime_columns] = hours_df[datetime_columns].apply(pd.to_datetime)
    
    # Menentukan rentang tanggal minimum dan maksimum
    min_date_days = days_df["dteday"].min()
    max_date_days = days_df["dteday"].max()
    
except FileNotFoundError:
    st.error("File CSV tidak ditemukan.")
except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    
# Menampilkan rentang tanggal pada sidebar
with st.sidebar:
    st.image("https://www.bmbike.sk/wp-content/uploads/2021/08/be07e51f-d358-4ae1-9352-a26e9b09ff07-1024x576.jpg?is-pending-load=1")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days]
    )

# Mengkonversi start_date dan end_date menjadi tipe data datetime64[ns]
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Memfilter dataframe berdasarkan rentang tanggal
main_df_days = days_df[(days_df["dteday"] >= start_date) & (days_df["dteday"] <= end_date)]
main_df_hour = hours_df[(hours_df["dteday"] >= start_date) & (hours_df["dteday"] <= end_date)]

# Menghitung metrik total sharing bike, total registered, dan total casual
total_orders = main_df_days["count_cr"].sum()
total_registered = total_registered_df(main_df_days)["register_sum"].sum()
total_casual = total_casual_df(main_df_days)["casual_sum"].sum()

# Menampilkan metrik pada dashboard
st.header('Bike Sharing :sparkles:')
st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sharing Bike", value=total_orders)

with col2:
    st.metric("Total Registered", value=total_registered)

with col3:
    st.metric("Total Casual", value=total_casual)

# Menghitung dan menampilkan grafik jam paling banyak dan paling sedikit disewa
    
sum_order_items_df = sum_order(main_df_hour)

st.subheader("Pada jam berapa yang paling banyak dan paling sedikit disewa?")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Pemanggilan sns.barplot() untuk subplot pertama
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.head(5), palette="viridis", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Hours (PM)", fontsize=30)
ax[0].set_title("Jam dengan banyak penyewa sepeda", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# Pemanggilan sns.barplot() untuk subplot kedua
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.sort_values(by="hours", ascending=True).head(5), palette="viridis", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Hours (AM)",  fontsize=30)
ax[1].set_title("Jam dengan sedikit penyewa sepeda", loc="center", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)
st.markdown("**Berdasarkan hasil gambar yang diatas bahwa sewa sepeda yang paling banyak di jam 17:00 (PM) dan pada jam 04:00 (AM) merupakan yang paling sedikit disewa**")


# Menghitung dan menampilkan grafik musim apa yang paling banyak disewa
season_df = macem_season(main_df_days)

st.subheader("Musim apa yang paling banyak disewa?")

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(

    x="season",
    y="count_cr",  # Ganti "sum" jika diperlukan
    data=season_df.sort_values(by="season", ascending=False),
    palette="viridis",  # Atur palet warna sesuai kebutuhan
    ax=ax
)
ax.set_title("Grafik Antar Musim", loc="center", fontsize=50)
ax.set_ylabel("Total Penggunaan Sepeda", fontsize=30)  # Sesuaikan label sumbu y
ax.set_xlabel("Musim", fontsize=30)  # Sesuaikan label sumbu x
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)

st.pyplot(fig)
st.markdown("**Sewa sepeda yang paling banyak jatuh kepada season Fall atau Musim Gugur**")