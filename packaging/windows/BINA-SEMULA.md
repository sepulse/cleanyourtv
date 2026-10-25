# CleanYourTV untuk Windows: cara membina semula

Folder ini membungkus alat asal cleanyourtv menjadi `Output\CleanYourTV-Setup.exe`, iaitu wizard
pemasangan dwibahasa (Bahasa Melayu / English). Tiada fail asal repo yang diubah.

## Keperluan

- Windows 10/11 x64
- Python **3.11 64-bit** dalam PATH (`python`); skrip binaan menyemaknya
- Inno Setup 6: `winget install -e --id JRSoftware.InnoSetup`
- Internet semasa binaan pertama (PyInstaller, Python embeddable, pakej daripada `tools\requirements.txt`)

## Bina

```powershell
powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
```

Hasilnya `packaging\windows\Output\CleanYourTV-Setup.exe`. Folder `build\` dan `Output\` tidak dimasukkan ke git.

## Apa yang berlaku semasa binaan

1. `cleanyourtv_menu.py` dibina dengan PyInstaller menjadi `CleanYourTV.exe` (menu konsol).
2. `tools\` dan `examples\` disalin tanpa perubahan.
3. Python 3.11 embeddable diletakkan di `tools\venv\Scripts\`. Laluan ini memang dicari oleh
   `disable.ps1` dan `restore.ps1`, jadi skrip asal boleh berjalan seperti biasa. Pakej
   `tools\requirements.txt` dipasang ke `Lib\site-packages` di situ.
4. `CleanYourTV.iss` disusun dengan Inno Setup.

## Fail

| Fail | Kegunaan |
|---|---|
| `cleanyourtv_menu.py` | Menu: semak sambungan, buang bloatware (`disable.ps1`), pulihkan (`restore.ps1`). Bahasa ikut pilihan semasa pemasangan. |
| `CleanYourTV.iss` | Wizard: pilih bahasa, lesen, folder, pintasan, halaman "Sediakan TV anda" (ikut jenama), uninstaller. |
| `Malay.isl` | Mesej Inno Setup 6 dalam Bahasa Melayu. |
| `THIRD_PARTY_NOTICES.txt` | Lesen komponen yang disertakan. Kemas kini versi di sini jika `pip` memasang versi baharu. |
| `_Default-en.isl`, `_Malaysian-2005.isl` | Sumber rujukan untuk terjemahan `Malay.isl`. |

## Nota

- Pemasangan per pengguna (tanpa admin), ke `%LOCALAPPDATA%\Programs\CleanYourTV`.
- Uninstall membuang folder aplikasi tetapi **mengekalkan** `%USERPROFILE%\.cleanyourtv\` (rekod
  keadaan TV sebelum perubahan, yang diperlukan untuk restore) dan `%USERPROFILE%\.android\adbkey`.
- Rekod restore terikat pada alamat IP TV dan laluan penuh senarai. Jika IP TV berubah atau
  aplikasi dipasang di folder lain, `restore.ps1` akan memberi amaran dan kembali kepada cara lama
  (enable semua pakej dalam senarai).
- Launcher (APK) tidak disertakan. Ia memerlukan Android SDK untuk dibina.
