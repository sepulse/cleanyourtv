; *** Inno Setup version 6.5.0+ English messages ***
;
; To download user-contributed translations of this file, go to:
;   https://jrsoftware.org/files/istrans/
;
; Note: When translating this text, do not add periods (.) to the end of
; messages that didn't have them already, because on those messages Inno
; Setup adds the periods automatically (appending a period would result in
; two periods being displayed).

[LangOptions]
; The following three entries are very important. Be sure to read and
; understand the '[LangOptions] section' topic in the help file.
LanguageName=Bahasa Melayu
LanguageID=$043E
; LanguageCodePage should always be set if possible, even if this file is Unicode
; For English it's set to zero anyway because English only uses ASCII characters
LanguageCodePage=0
; If the language you are translating to requires special font faces or
; sizes, uncomment any of the following entries and change them accordingly.
;DialogFontName=
;DialogFontSize=9
;DialogFontBaseScaleWidth=7
;DialogFontBaseScaleHeight=15
;WelcomeFontName=Segoe UI
;WelcomeFontSize=14

[Messages]

; *** Application titles
SetupAppTitle=Pemasangan
SetupWindowTitle=Pemasangan - %1
UninstallAppTitle=Nyahpasang
UninstallAppFullTitle=Nyahpasang %1

; *** Misc. common
InformationTitle=Maklumat
ConfirmTitle=Sahkan
ErrorTitle=Ralat

; *** SetupLdr messages
SetupLdrStartupMessage=Tindakan ini akan memasang %1. Adakah anda ingin meneruskannya?
LdrCannotCreateTemp=Tidak dapat mencipta fail sementara. Pemasangan dibatalkan
LdrCannotExecTemp=Tidak dapat melaksanakan fail dalam direktori sementara. Pemasangan dibatalkan
HelpTextNote=

; *** Startup error messages
LastErrorMessage=%1.%n%nRalat %2: %3
SetupFileMissing=Fail %1 tiada dalam direktori pemasangan. Sila betulkan masalah ini atau dapatkan salinan baharu program ini.
SetupFileCorrupt=Fail pemasangan telah rosak. Sila dapatkan salinan baharu program ini.
SetupFileCorruptOrWrongVer=Fail pemasangan telah rosak atau tidak serasi dengan versi Pemasangan ini. Sila betulkan masalah ini atau dapatkan salinan baharu program ini.
InvalidParameter=Parameter tidak sah telah diberikan pada baris arahan:%n%n%1
SetupAlreadyRunning=Pemasangan sedang berjalan.
WindowsVersionNotSupported=Program ini tidak menyokong versi Windows yang dijalankan pada komputer anda.
WindowsServicePackRequired=Program ini memerlukan %1 Service Pack %2 atau yang lebih baharu.
NotOnThisPlatform=Program ini tidak akan berjalan pada %1.
OnlyOnThisPlatform=Program ini mesti dijalankan pada %1.
OnlyOnTheseArchitectures=Program ini hanya boleh dipasang pada versi Windows yang direka untuk seni bina pemproses berikut:%n%n%1
WinVersionTooLowError=Program ini memerlukan %1 versi %2 atau yang lebih baharu.
WinVersionTooHighError=Program ini tidak boleh dipasang pada %1 versi %2 atau yang lebih baharu.
AdminPrivilegesRequired=Anda mesti log masuk sebagai pentadbir semasa memasang program ini.
PowerUserPrivilegesRequired=Anda mesti log masuk sebagai pentadbir atau sebagai ahli kumpulan Power Users semasa memasang program ini.
SetupAppRunningError=Pemasangan mengesan bahawa %1 sedang berjalan.%n%nSila tutup program tersebut sekarang, kemudian klik OK untuk meneruskan, atau Batal untuk keluar.
UninstallAppRunningError=Penyahpasang mengesan bahawa %1 sedang berjalan.%n%nSila tutup program tersebut sekarang, kemudian klik OK untuk meneruskan, atau Batal untuk keluar.

; *** Startup questions
PrivilegesRequiredOverrideTitle=Pilih Mod Pemasangan
PrivilegesRequiredOverrideInstruction=Pilih mod pemasangan
PrivilegesRequiredOverrideText1=%1 boleh dipasang untuk semua pengguna (memerlukan keistimewaan pentadbir), atau untuk anda sahaja.
PrivilegesRequiredOverrideText2=%1 boleh dipasang untuk anda sahaja, atau untuk semua pengguna (memerlukan keistimewaan pentadbir).
PrivilegesRequiredOverrideAllUsers=Pasang untuk &semua pengguna
PrivilegesRequiredOverrideAllUsersRecommended=Pasang untuk &semua pengguna (disyorkan)
PrivilegesRequiredOverrideCurrentUser=Pasang untuk sa&ya sahaja
PrivilegesRequiredOverrideCurrentUserRecommended=Pasang untuk sa&ya sahaja (disyorkan)

; *** Misc. errors
ErrorCreatingDir=Pemasangan tidak dapat mencipta direktori "%1"
ErrorTooManyFilesInDir=Tidak dapat mencipta fail dalam direktori "%1" kerana direktori tersebut mengandungi terlalu banyak fail

; *** Setup common messages
ExitSetupTitle=Keluar daripada Pemasangan
ExitSetupMessage=Pemasangan belum selesai. Jika anda keluar sekarang, program tidak akan dipasang.%n%nAnda boleh menjalankan Pemasangan semula pada masa lain untuk melengkapkan pemasangan.%n%nKeluar daripada Pemasangan?
AboutSetupMenuItem=&Perihal Pemasangan...
AboutSetupTitle=Perihal Pemasangan
AboutSetupMessage=%1 versi %2%n%3%n%nLaman utama %1:%n%4
AboutSetupNote=
TranslatorNote=

; *** Buttons
ButtonBack=< &Kembali
ButtonNext=&Seterusnya >
ButtonInstall=&Pasang
ButtonOK=OK
ButtonCancel=Batal
ButtonYes=&Ya
ButtonYesToAll=Ya untuk &Semua
ButtonNo=&Tidak
ButtonNoToAll=T&idak untuk Semua
ButtonFinish=&Selesai
ButtonBrowse=&Semak imbas...
ButtonWizardBrowse=S&emak imbas...
ButtonNewFolder=&Cipta Folder Baharu

; *** "Select Language" dialog messages
SelectLanguageTitle=Pilih Bahasa Pemasangan
SelectLanguageLabel=Pilih bahasa yang akan digunakan semasa pemasangan.

; *** Common wizard text
ClickNext=Klik Seterusnya untuk meneruskan, atau Batal untuk keluar daripada Pemasangan.
BeveledLabel=
BrowseDialogTitle=Semak Imbas Folder
BrowseDialogLabel=Pilih folder dalam senarai di bawah, kemudian klik OK.
NewFolderName=Folder Baharu

; *** "Welcome" wizard page
WelcomeLabel1=Selamat datang ke Wizard Pemasangan [name]
WelcomeLabel2=Tindakan ini akan memasang [name/ver] pada komputer anda.%n%nAnda disyorkan untuk menutup semua aplikasi lain sebelum meneruskan.

; *** "Password" wizard page
WizardPassword=Kata Laluan
PasswordLabel1=Pemasangan ini dilindungi dengan kata laluan.
PasswordLabel3=Sila masukkan kata laluan, kemudian klik Seterusnya untuk meneruskan. Kata laluan peka huruf besar/kecil.
PasswordEditLabel=&Kata laluan:
IncorrectPassword=Kata laluan yang anda masukkan tidak betul. Sila cuba lagi.

; *** "License Agreement" wizard page
WizardLicense=Perjanjian Lesen
LicenseLabel=Sila baca maklumat penting berikut sebelum meneruskan.
LicenseLabel3=Sila baca Perjanjian Lesen berikut. Anda mesti menerima syarat perjanjian ini sebelum meneruskan pemasangan.
LicenseAccepted=Saya &menerima perjanjian ini
LicenseNotAccepted=Saya &tidak menerima perjanjian ini

; *** "Information" wizard pages
WizardInfoBefore=Maklumat
InfoBeforeLabel=Sila baca maklumat penting berikut sebelum meneruskan.
InfoBeforeClickLabel=Apabila anda sudah bersedia untuk meneruskan Pemasangan, klik Seterusnya.
WizardInfoAfter=Maklumat
InfoAfterLabel=Sila baca maklumat penting berikut sebelum meneruskan.
InfoAfterClickLabel=Apabila anda sudah bersedia untuk meneruskan Pemasangan, klik Seterusnya.

; *** "User Information" wizard page
WizardUserInfo=Maklumat Pengguna
UserInfoDesc=Sila masukkan maklumat anda.
UserInfoName=&Nama Pengguna:
UserInfoOrg=&Organisasi:
UserInfoSerial=Nombor &Siri:
UserInfoNameRequired=Anda mesti memasukkan nama.

; *** "Select Destination Location" wizard page
WizardSelectDir=Pilih Lokasi Destinasi
SelectDirDesc=Di manakah [name] patut dipasang?
SelectDirLabel3=Pemasangan akan memasang [name] ke dalam folder berikut.
SelectDirBrowseLabel=Untuk meneruskan, klik Seterusnya. Jika anda ingin memilih folder lain, klik Semak Imbas.
DiskSpaceGBLabel=Sekurang-kurangnya [gb] GB ruang cakera kosong diperlukan.
DiskSpaceMBLabel=Sekurang-kurangnya [mb] MB ruang cakera kosong diperlukan.
CannotInstallToNetworkDrive=Pemasangan tidak boleh dipasang ke pemacu rangkaian.
CannotInstallToUNCPath=Pemasangan tidak boleh dipasang ke laluan UNC.
InvalidPath=Anda mesti memasukkan laluan penuh berserta huruf pemacu; contohnya:%n%nC:\APP%n%natau laluan UNC dalam bentuk:%n%n\\pelayan\kongsi
InvalidDrive=Pemacu atau perkongsian UNC yang anda pilih tidak wujud atau tidak boleh diakses. Sila pilih yang lain.
DiskSpaceWarningTitle=Ruang Cakera Tidak Mencukupi
DiskSpaceWarning=Pemasangan memerlukan sekurang-kurangnya %1 KB ruang kosong untuk dipasang, tetapi pemacu yang dipilih hanya mempunyai %2 KB ruang yang tersedia.%n%nAdakah anda mahu meneruskannya juga?
DirNameTooLong=Nama folder atau laluan terlalu panjang.
InvalidDirName=Nama folder tidak sah.
BadDirName32=Nama folder tidak boleh mengandungi mana-mana aksara berikut:%n%n%1
DirExistsTitle=Folder Sudah Wujud
DirExists=Folder:%n%n%1%n%nsudah wujud. Adakah anda mahu memasang ke folder tersebut juga?
DirDoesntExistTitle=Folder Tidak Wujud
DirDoesntExist=Folder:%n%n%1%n%ntidak wujud. Adakah anda mahu folder tersebut dicipta?

; *** "Select Components" wizard page
WizardSelectComponents=Pilih Komponen
SelectComponentsDesc=Komponen manakah yang patut dipasang?
SelectComponentsLabel2=Pilih komponen yang ingin anda pasang; kosongkan komponen yang tidak mahu dipasang. Klik Seterusnya apabila anda sudah bersedia untuk meneruskan.
FullInstallation=Pemasangan penuh
; if possible don't translate 'Compact' as 'Minimal' (I mean 'Minimal' in your language)
CompactInstallation=Pemasangan padat
CustomInstallation=Pemasangan tersuai
NoUninstallWarningTitle=Komponen Sudah Wujud
NoUninstallWarning=Pemasangan telah mengesan bahawa komponen berikut sudah dipasang pada komputer anda:%n%n%1%n%nMenyahpilih komponen ini tidak akan menyahpasangnya.%n%nAdakah anda tetap ingin meneruskannya?
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceGBLabel=Pilihan semasa memerlukan sekurang-kurangnya [gb] GB ruang cakera.
ComponentsDiskSpaceMBLabel=Pilihan semasa memerlukan sekurang-kurangnya [mb] MB ruang cakera.

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=Pilih Tugas Tambahan
SelectTasksDesc=Tugas tambahan manakah yang harus dilakukan?
SelectTasksLabel2=Pilih tugas tambahan yang ingin dilakukan oleh Pemasangan semasa memasang [name], kemudian klik Seterusnya.

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=Pilih Folder Menu Mula
SelectStartMenuFolderDesc=Di manakah Pemasangan patut meletakkan pintasan program?
SelectStartMenuFolderLabel3=Pemasangan akan mencipta pintasan program dalam folder Menu Mula berikut.
SelectStartMenuFolderBrowseLabel=Untuk meneruskan, klik Seterusnya. Jika anda ingin memilih folder lain, klik Semak Imbas.
MustEnterGroupName=Anda mesti memasukkan nama folder.
GroupNameTooLong=Nama folder atau laluan terlalu panjang.
InvalidGroupName=Nama folder tidak sah.
BadGroupName=Nama folder tidak boleh mengandungi mana-mana aksara berikut:%n%n%1
NoProgramGroupCheck2=&Jangan cipta folder Menu Mula

; *** "Ready to Install" wizard page
WizardReady=Sedia untuk Memasang
ReadyLabel1=Pemasangan kini bersedia untuk mula memasang [name] pada komputer anda.
ReadyLabel2a=Klik Pasang untuk meneruskan pemasangan, atau klik Kembali jika anda ingin menyemak atau menukar sebarang tetapan.
ReadyLabel2b=Klik Pasang untuk meneruskan pemasangan.
ReadyMemoUserInfo=Maklumat pengguna:
ReadyMemoDir=Lokasi destinasi:
ReadyMemoType=Jenis pemasangan:
ReadyMemoComponents=Komponen yang dipilih:
ReadyMemoGroup=Folder Menu Mula:
ReadyMemoTasks=Tugas tambahan:

; *** TDownloadWizardPage wizard page and DownloadTemporaryFile
DownloadingLabel2=Memuat turun fail...
ButtonStopDownload=&Hentikan muat turun
StopDownload=Adakah anda pasti ingin menghentikan muat turun?
ErrorDownloadAborted=Muat turun dibatalkan
ErrorDownloadFailed=Muat turun gagal: %1 %2
ErrorDownloadSizeFailed=Gagal mendapatkan saiz: %1 %2
ErrorProgress=Kemajuan tidak sah: %1 daripada %2
ErrorFileSize=Saiz fail tidak sah: dijangka %1, ditemui %2

; *** TExtractionWizardPage wizard page and ExtractArchive
ExtractingLabel=Mengekstrak fail...
ButtonStopExtraction=&Hentikan pengekstrakan
StopExtraction=Adakah anda pasti ingin menghentikan pengekstrakan?
ErrorExtractionAborted=Pengekstrakan dibatalkan
ErrorExtractionFailed=Pengekstrakan gagal: %1

; *** Archive extraction failure details
ArchiveIncorrectPassword=Kata laluan tidak betul
ArchiveIsCorrupted=Arkib telah rosak
ArchiveUnsupportedFormat=Format arkib tidak disokong

; *** "Preparing to Install" wizard page
WizardPreparing=Bersedia untuk Memasang
PreparingDesc=Pemasangan sedang bersedia untuk memasang [name] pada komputer anda.
PreviousInstallNotCompleted=Pemasangan/penyahpasangan program terdahulu belum selesai. Anda perlu memulakan semula komputer anda untuk melengkapkan pemasangan tersebut.%n%nSelepas memulakan semula komputer, jalankan Pemasangan sekali lagi untuk melengkapkan pemasangan [name].
CannotContinue=Pemasangan tidak boleh diteruskan. Sila klik Batal untuk keluar.
ApplicationsFound=Aplikasi berikut sedang menggunakan fail yang perlu dikemas kini oleh Pemasangan. Anda disyorkan untuk membenarkan Pemasangan menutup aplikasi ini secara automatik.
ApplicationsFound2=Aplikasi berikut sedang menggunakan fail yang perlu dikemas kini oleh Pemasangan. Anda disyorkan untuk membenarkan Pemasangan menutup aplikasi ini secara automatik. Selepas pemasangan selesai, Pemasangan akan cuba memulakan semula aplikasi tersebut.
CloseApplications=Tutup aplikasi secara &automatik
DontCloseApplications=&Jangan tutup aplikasi
ErrorCloseApplications=Pemasangan tidak dapat menutup semua aplikasi secara automatik. Anda disyorkan untuk menutup semua aplikasi yang menggunakan fail yang perlu dikemas kini oleh Pemasangan sebelum meneruskan.
PrepareToInstallNeedsRestart=Pemasangan mesti memulakan semula komputer anda. Selepas memulakan semula komputer, jalankan Pemasangan sekali lagi untuk melengkapkan pemasangan [name].%n%nAdakah anda ingin memulakan semula sekarang?

; *** "Installing" wizard page
WizardInstalling=Memasang
InstallingLabel=Sila tunggu sementara Pemasangan memasang [name] pada komputer anda.

; *** "Setup Completed" wizard page
FinishedHeadingLabel=Menyelesaikan Wizard Pemasangan [name]
FinishedLabelNoIcons=Pemasangan telah selesai memasang [name] pada komputer anda.
FinishedLabel=Pemasangan telah selesai memasang [name] pada komputer anda. Aplikasi ini boleh dilancarkan dengan memilih pintasan yang dipasang.
ClickFinish=Klik Selesai untuk keluar daripada Pemasangan.
FinishedRestartLabel=Untuk melengkapkan pemasangan [name], Pemasangan mesti memulakan semula komputer anda. Adakah anda ingin memulakan semula sekarang?
FinishedRestartMessage=Untuk melengkapkan pemasangan [name], Pemasangan mesti memulakan semula komputer anda.%n%nAdakah anda ingin memulakan semula sekarang?
ShowReadmeCheck=Ya, saya ingin melihat fail README
YesRadio=&Ya, mulakan semula komputer sekarang
NoRadio=&Tidak, saya akan memulakan semula komputer kemudian
; used for example as 'Run MyProg.exe'
RunEntryExec=Jalankan %1
; used for example as 'View Readme.txt'
RunEntryShellExec=Lihat %1

; *** "Setup Needs the Next Disk" stuff
ChangeDiskTitle=Pemasangan Memerlukan Cakera Seterusnya
SelectDiskLabel2=Sila masukkan Cakera %1 dan klik OK.%n%nJika fail pada cakera ini boleh didapati dalam folder selain daripada yang dipaparkan di bawah, masukkan laluan yang betul atau klik Semak Imbas.
PathLabel=&Laluan:
FileNotInDir2=Fail "%1" tidak dapat ditemui dalam "%2". Sila masukkan cakera yang betul atau pilih folder lain.
SelectDirectoryLabel=Sila nyatakan lokasi cakera seterusnya.

; *** Installation phase messages
SetupAborted=Pemasangan belum selesai.%n%nSila betulkan masalah ini dan jalankan Pemasangan sekali lagi.
AbortRetryIgnoreSelectAction=Pilih tindakan
AbortRetryIgnoreRetry=&Cuba lagi
AbortRetryIgnoreIgnore=&Abaikan ralat dan teruskan
AbortRetryIgnoreCancel=Batalkan pemasangan
RetryCancelSelectAction=Pilih tindakan
RetryCancelRetry=&Cuba lagi
RetryCancelCancel=Batal

; *** Installation status messages
StatusClosingApplications=Menutup aplikasi...
StatusCreateDirs=Mencipta direktori...
StatusExtractFiles=Mengekstrak fail...
StatusDownloadFiles=Memuat turun fail...
StatusCreateIcons=Mencipta pintasan...
StatusCreateIniEntries=Mencipta entri INI...
StatusCreateRegistryEntries=Mencipta entri pendaftaran...
StatusRegisterFiles=Mendaftarkan fail...
StatusSavingUninstall=Menyimpan maklumat nyahpasang...
StatusRunProgram=Menyelesaikan pemasangan...
StatusRestartingApplications=Memulakan semula aplikasi...
StatusRollback=Mengundurkan perubahan...

; *** Misc. errors
ErrorInternal2=Ralat dalaman: %1
ErrorFunctionFailedNoCode=%1 gagal
ErrorFunctionFailed=%1 gagal; kod %2
ErrorFunctionFailedWithMessage=%1 gagal; kod %2.%n%3
ErrorExecutingProgram=Tidak dapat melaksanakan fail:%n%1

; *** Registry errors
ErrorRegOpenKey=Ralat membuka kunci pendaftaran:%n%1\%2
ErrorRegCreateKey=Ralat mencipta kunci pendaftaran:%n%1\%2
ErrorRegWriteKey=Ralat menulis pada kunci pendaftaran:%n%1\%2

; *** INI errors
ErrorIniEntry=Ralat mencipta entri INI dalam fail "%1".

; *** File copying errors
FileAbortRetryIgnoreSkipNotRecommended=&Langkau fail ini (tidak disyorkan)
FileAbortRetryIgnoreIgnoreNotRecommended=&Abaikan ralat dan teruskan (tidak disyorkan)
SourceIsCorrupted=Fail sumber telah rosak
SourceDoesntExist=Fail sumber "%1" tidak wujud
SourceVerificationFailed=Pengesahan fail sumber gagal: %1
VerificationSignatureDoesntExist=Fail tandatangan "%1" tidak wujud
VerificationSignatureInvalid=Fail tandatangan "%1" tidak sah
VerificationKeyNotFound=Fail tandatangan "%1" menggunakan kunci yang tidak diketahui
VerificationFileNameIncorrect=Nama fail tidak betul
VerificationFileTagIncorrect=Tag fail tidak betul
VerificationFileSizeIncorrect=Saiz fail tidak betul
VerificationFileHashIncorrect=Hash fail tidak betul
ExistingFileReadOnly2=Fail sedia ada tidak dapat digantikan kerana ia ditandakan sebagai baca sahaja.
ExistingFileReadOnlyRetry=&Buang atribut baca sahaja dan cuba lagi
ExistingFileReadOnlyKeepExisting=&Kekalkan fail sedia ada
ErrorReadingExistingDest=Ralat berlaku semasa cuba membaca fail sedia ada:
FileExistsSelectAction=Pilih tindakan
FileExists2=Fail sudah wujud.
FileExistsOverwriteExisting=&Tulis ganti fail sedia ada
FileExistsKeepExisting=&Kekalkan fail sedia ada
FileExistsOverwriteOrKeepAll=&Lakukan ini untuk konflik seterusnya
ExistingFileNewerSelectAction=Pilih tindakan
ExistingFileNewer2=Fail sedia ada lebih baharu daripada fail yang sedang cuba dipasang oleh Pemasangan.
ExistingFileNewerOverwriteExisting=&Tulis ganti fail sedia ada
ExistingFileNewerKeepExisting=&Kekalkan fail sedia ada (disyorkan)
ExistingFileNewerOverwriteOrKeepAll=&Lakukan ini untuk konflik seterusnya
ErrorChangingAttr=Ralat berlaku semasa cuba menukar atribut fail sedia ada:
ErrorCreatingTemp=Ralat berlaku semasa cuba mencipta fail dalam direktori destinasi:
ErrorReadingSource=Ralat berlaku semasa cuba membaca fail sumber:
ErrorCopying=Ralat berlaku semasa cuba menyalin fail:
ErrorDownloading=Ralat berlaku semasa cuba memuat turun fail:
ErrorExtracting=Ralat berlaku semasa cuba mengekstrak arkib:
ErrorReplacingExistingFile=Ralat berlaku semasa cuba menggantikan fail sedia ada:
ErrorRestartReplace=RestartReplace gagal:
ErrorRenamingTemp=Ralat berlaku semasa cuba menamakan semula fail dalam direktori destinasi:
ErrorRegisterServer=Tidak dapat mendaftarkan DLL/OCX: %1
ErrorRegSvr32Failed=RegSvr32 gagal dengan kod keluar %1
ErrorRegisterTypeLib=Tidak dapat mendaftarkan pustaka jenis: %1

; *** Uninstall display name markings
; used for example as 'My Program (32-bit)'
UninstallDisplayNameMark=%1 (%2)
; used for example as 'My Program (32-bit, All users)'
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32-bit
UninstallDisplayNameMark64Bit=64-bit
UninstallDisplayNameMarkAllUsers=Semua pengguna
UninstallDisplayNameMarkCurrentUser=Pengguna semasa

; *** Post-installation errors
ErrorOpeningReadme=Ralat berlaku semasa cuba membuka fail README.
ErrorRestartingComputer=Pemasangan tidak dapat memulakan semula komputer. Sila lakukan ini secara manual.

; *** Uninstaller messages
UninstallNotFound=Fail "%1" tidak wujud. Tidak dapat menyahpasang.
UninstallOpenError=Fail "%1" tidak dapat dibuka. Tidak dapat menyahpasang
UninstallUnsupportedVer=Fail log nyahpasang "%1" berada dalam format yang tidak dikenali oleh versi penyahpasang ini. Tidak dapat menyahpasang
UninstallUnknownEntry=Entri yang tidak diketahui (%1) ditemui dalam log nyahpasang
ConfirmUninstall=Adakah anda pasti ingin membuang %1 dan semua komponennya sepenuhnya?
UninstallOnlyOnWin64=Pemasangan ini hanya boleh dinyahpasang pada Windows 64-bit.
OnlyAdminCanUninstall=Pemasangan ini hanya boleh dinyahpasang oleh pengguna yang mempunyai keistimewaan pentadbir.
UninstallStatusLabel=Sila tunggu sementara %1 dibuang daripada komputer anda.
UninstalledAll=%1 telah berjaya dibuang daripada komputer anda.
UninstalledMost=Penyahpasangan %1 selesai.%n%nBeberapa item tidak dapat dibuang. Item ini boleh dibuang secara manual.
UninstalledAndNeedsRestart=Untuk melengkapkan penyahpasangan %1, komputer anda mesti dimulakan semula.%n%nAdakah anda ingin memulakan semula sekarang?
UninstallDataCorrupted=Fail "%1" telah rosak. Tidak dapat menyahpasang

; *** Uninstallation phase messages
ConfirmDeleteSharedFileTitle=Buang Fail Kongsi?
ConfirmDeleteSharedFile2=Sistem menunjukkan bahawa fail kongsi berikut tidak lagi digunakan oleh mana-mana program. Adakah anda ingin Penyahpasang membuang fail kongsi ini?%n%nJika ada program yang masih menggunakan fail ini dan fail tersebut dibuang, program tersebut mungkin tidak berfungsi dengan betul. Jika anda tidak pasti, pilih Tidak. Membiarkan fail ini dalam sistem anda tidak akan mendatangkan sebarang masalah.
SharedFileNameLabel=Nama fail:
SharedFileLocationLabel=Lokasi:
WizardUninstalling=Status Penyahpasangan
StatusUninstalling=Menyahpasang %1...

; *** Shutdown block reasons
ShutdownBlockReasonInstallingApp=Memasang %1.
ShutdownBlockReasonUninstallingApp=Menyahpasang %1.

; The custom messages below aren't used by Setup itself, but if you make
; use of them in your scripts, you'll want to translate them.

[CustomMessages]

NameAndVersion=%1 versi %2
AdditionalIcons=Pintasan tambahan:
CreateDesktopIcon=Cipta pintasan &desktop
CreateQuickLaunchIcon=Cipta pintasan &Pelancaran Pantas
ProgramOnTheWeb=%1 di Web
UninstallProgram=Nyahpasang %1
LaunchProgram=Lancarkan %1
AssocFileExtension=&Kaitkan %1 dengan sambungan fail %2
AssocingFileExtension=Mengaitkan %1 dengan sambungan fail %2...
AutoStartProgramGroupDescription=Permulaan:
AutoStartProgram=Mulakan %1 secara automatik
AddonHostProgramNotFound=%1 tidak dapat ditemui dalam folder yang anda pilih.%n%nAdakah anda mahu meneruskannya juga?
