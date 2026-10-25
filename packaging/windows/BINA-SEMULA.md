# CleanYourTV untuk Windows: cara membina semula

Folder ini membungkus alat asal cleanyourtv menjadi `Output\CleanYourTV-Setup.exe`, iaitu wizard
pemasangan dwibahasa (Bahasa Melayu / English), dengan UI web setempat dan APK launcher disertakan.

## Keperluan

- Windows 10/11 x64
- Python **3.11 64-bit** dalam PATH (`python`); skrip binaan menyemaknya
- Inno Setup 6: `winget install -e --id JRSoftware.InnoSetup`
- Android SDK di `%LOCALAPPDATA%\Android\Sdk` (atau `ANDROID_HOME`) dan JDK 21 dalam PATH atau
  `JAVA_HOME`, jika APK belum dibina. Gunakan platform 34 dan build-tools 34.0.0.
- Internet semasa binaan pertama (PyInstaller, Python embeddable, pakej daripada `tools\requirements.txt`)

## Bina

```powershell
powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
```

Hasilnya `packaging\windows\Output\CleanYourTV-Setup.exe`. Folder `build\` dan `Output\` tidak dimasukkan ke git.

## Apa yang berlaku semasa binaan

1. `app\server.py` dibina dengan PyInstaller menjadi `CleanYourTV.exe`. Fail `app\web\` disalin ke
   `stage\web\`: rupa, font dan panduan persediaan diadaptasi daripada CleanTV milik pemilik yang sama.
2. `tools\` dan `examples\` disalin tanpa perubahan.
3. Python 3.11 embeddable diletakkan di `tools\venv\Scripts\`. Laluan ini memang dicari oleh
   `disable.ps1` dan `restore.ps1`, jadi skrip asal boleh berjalan seperti biasa. Pakej
   `tools\requirements.txt` dipasang ke `Lib\site-packages` di situ.
4. Jika `launcher\app\build\outputs\apk\release\app-release.apk` tiada, bina dengan
   `launcher\gradlew.bat assembleRelease`. APK disalin sebagai `stage\launcher\tvhome.apk`, bersama
   `build-and-install.ps1` dan lesen font Outfit. Binaan ini tidak menyambung ke TV.
5. `CleanYourTV.iss` disusun dengan Inno Setup. Bahagian `[Files]` menyertakan semua fail dalam stage,
   termasuk APK dan fail web, tanpa mengubah wizard sedia ada.

## Fail

| Fail | Kegunaan |
|---|---|
| `app\server.py` | Pelayan HTTP setempat, padanan model dan senarai, kerja skrip serta rekod senarai terakhir bagi setiap TV. |
| `app\web\` | UI dan fail bahasa `i18n\ms.json` / `en.json`, dengan suis bahasa pada header. |
| `app\test_server.py` | Ujian HTTP, token, padanan model dan arahan skrip menggunakan mock, tanpa TV. |
| `CleanYourTV.iss` | Wizard: pilih bahasa, lesen, folder, pintasan, halaman "Sediakan TV anda" (ikut jenama), uninstaller. |
| `Malay.isl` | Mesej Inno Setup 6 dalam Bahasa Melayu. |
| `THIRD_PARTY_NOTICES.txt` | Lesen komponen yang disertakan. Kemas kini versi di sini jika `pip` memasang versi baharu. |
| `_Default-en.isl`, `_Malaysian-2005.isl` | Sumber rujukan untuk terjemahan `Malay.isl`. |

## Nota

- Pemasangan per pengguna (tanpa admin), ke `%LOCALAPPDATA%\Programs\CleanYourTV`.
- Uninstall membuang folder aplikasi, `%LOCALAPPDATA%\CleanYourTV\` (IP dan senarai terakhir) dan
  kunci ADB milik `tv.py` di `tools\adbkey\`. Selepas pasang semula, TV akan bertanya "Benarkan
  penyahpepijatan USB?" sekali lagi. Jika `%USERPROFILE%\.android\adbkey` sudah wujud (pengguna
  Android Studio), `tv.py` menggunakan kunci itu dan uninstall tidak menyentuhnya.
- Uninstall **mengekalkan** `%USERPROFILE%\.cleanyourtv\`, iaitu rekod keadaan TV sebelum perubahan
  yang diperlukan untuk restore.
- Rekod restore terikat pada alamat IP TV dan laluan penuh senarai. Jika IP TV berubah atau
  aplikasi dipasang di folder lain, `restore.ps1` akan memberi amaran dan kembali kepada cara lama
  (enable semua pakej dalam senarai).
- Pengguna tidak memerlukan Android Studio: launcher dipasang melalui `build-and-install.ps1 -Apk`.
- `CleanYourTV.exe` membuka pelayar lalai ke `127.0.0.1` pada port kosong. Setiap POST memerlukan token
  rawak untuk sesi itu; Host dan Origin lain ditolak. Tiada aset dimuatkan daripada internet.
- Butang Keluar menghentikan pelayan. Menutup konsol juga menghentikannya. Tunggu kerja skrip selesai
  sebelum menutup aplikasi.
- Jalankan `python -m unittest discover -s packaging\windows\app -p "test_*.py" -v` untuk ujian tanpa TV.
