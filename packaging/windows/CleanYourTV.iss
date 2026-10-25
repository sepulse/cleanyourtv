; CleanYourTV for Windows: bilingual (Bahasa Melayu / English) wizard around build\stage.
; Built by build.ps1; compile alone with: ISCC.exe CleanYourTV.iss

#define AppName "CleanYourTV"
#define AppVersion "2.7.0.1"

[Setup]
AppId={{086B984C-5EA3-4425-949A-797A31458B44}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Gathin (github.com/Gathin23/cleanyourtv)
AppPublisherURL=https://github.com/Gathin23/cleanyourtv
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
ShowLanguageDialog=yes
LicenseFile=build\stage\LICENSE.txt
OutputDir=Output
OutputBaseFilename=CleanYourTV-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Room for every step on the "Prepare your TV" page in Malay, the longer language (modern defaults to 120).
WizardSizePercent=140
UninstallDisplayIcon={app}\CleanYourTV.exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "ms"; MessagesFile: "Malay.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "build\stage\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[INI]
Filename: "{app}\cleanyourtv.ini"; Section: "Settings"; Key: "Lang"; String: "{language}"; Flags: uninsdeletesection

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\CleanYourTV.exe"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\CleanYourTV.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\CleanYourTV.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Python writes these when the tools run; recovery records in %USERPROFILE%\.cleanyourtv are kept on purpose.
Type: files; Name: "{app}\cleanyourtv.ini"
Type: filesandordirs; Name: "{app}\tools\__pycache__"
Type: filesandordirs; Name: "{app}\tools\venv"

[CustomMessages]
ms.TvTitle=Sediakan TV anda
ms.TvIntro=CleanYourTV menyambung ke TV melalui Wi-Fi. Pastikan alat kawalan jauh TV anda berada berhampiran. Pilih jenama TV anda dan ikuti langkah ini.
ms.TvOther=Lain-lain
ms.TvOpen=Buka
ms.TvPress=Tekan
ms.TvSeven=7 kali untuk membuka kunci
ms.TvEnable=hidupkan
ms.TvOr=atau
ms.TvThen=kemudian
ms.TvSettings=Tetapan
ms.TvSystem=Sistem
ms.TvDevicePrefs=Pilihan Peranti
ms.TvAbout=Perihal
ms.TvBuild=Binaan Android TV OS
ms.TvDevOptions=Pilihan pembangun
ms.TvUsbDebug=Penyahpepijatan USB
ms.TvNetDebug=Penyahpepijatan rangkaian
ms.TvNote=Sesetengah TV hanya memaparkan Penyahpepijatan USB. Biarkan pilihan ini dihidupkan semasa menyambung melalui Wi-Fi.
ms.TvAllow=Apabila CleanYourTV menyambung buat kali pertama, perhatikan skrin TV. Gunakan alat kawalan jauh anda untuk memilih "Sentiasa benarkan daripada komputer ini" (Always allow from this computer), kemudian "Benarkan" (Allow).
ms.TvLater=Anda boleh melakukan langkah ini sekarang atau selepas pemasangan.
en.TvTitle=Prepare your TV
en.TvIntro=CleanYourTV connects to the TV over Wi-Fi. Keep your TV remote nearby. Choose your TV brand and follow these steps.
en.TvOther=Other
en.TvOpen=Open
en.TvPress=Press
en.TvSeven=7 times to unlock
en.TvEnable=turn on
en.TvOr=or
en.TvThen=then
en.TvSettings=Settings
en.TvSystem=System
en.TvDevicePrefs=Device Preferences
en.TvAbout=About
en.TvBuild=Android TV OS build
en.TvDevOptions=Developer options
en.TvUsbDebug=USB debugging
en.TvNetDebug=Network debugging
en.TvNote=Some TVs only show USB debugging. Keep it turned on while connecting over Wi-Fi.
en.TvAllow=The first time CleanYourTV connects, look at the TV screen. Use your remote to select "Always allow from this computer", then "Allow".
en.TvLater=You can do these steps now or after installing.

[Code]
var
  TvPage: TInputOptionWizardPage;
  Steps: TNewStaticText;

{ Menu names as the TV shows them: in Malay the English name follows in brackets, as in CleanTV. }
function Menu(const Name, English: String): String;
begin
  if ActiveLanguage = 'ms' then
    Result := Name + ' (' + English + ')'
  else
    Result := Name;
end;

procedure ShowSteps(Sender: TObject);
var
  Branch, Path: String;
  Brand: Integer;
begin
  Brand := TvPage.SelectedValueIndex;
  { Xiaomi and Hisense keep About under Device Preferences; the others under System. }
  if (Brand = 1) or (Brand = 4) then
    Branch := Menu(CustomMessage('TvDevicePrefs'), 'Device Preferences')
  else
    Branch := Menu(CustomMessage('TvSystem'), 'System');
  Path := Menu(CustomMessage('TvSettings'), 'Settings') + ' → ' + Branch;
  Steps.Caption :=
    '1.  ' + CustomMessage('TvOpen') + ' ' + Path + ' → ' + Menu(CustomMessage('TvAbout'), 'About') + '.' + #13#10 +
    '2.  ' + CustomMessage('TvPress') + ' ' + Menu(CustomMessage('TvBuild'), 'Android TV OS build') + ' ' +
      CustomMessage('TvSeven') + ' ' + Menu(CustomMessage('TvDevOptions'), 'Developer options') + '.' + #13#10 +
    '3.  ' + CustomMessage('TvOpen') + ' ' + Path + ' → ' + Menu(CustomMessage('TvDevOptions'), 'Developer options') +
      ', ' + CustomMessage('TvThen') + ' ' + CustomMessage('TvEnable') + ' ' + Menu(CustomMessage('TvUsbDebug'), 'USB debugging') +
      ' ' + CustomMessage('TvOr') + ' ' + Menu(CustomMessage('TvNetDebug'), 'Network debugging') + '.' + #13#10 +
    '4.  ' + CustomMessage('TvAllow') + #13#10#13#10 +
    CustomMessage('TvNote') + ' ' + CustomMessage('TvLater');
end;

procedure InitializeWizard;
begin
  { The intro goes in the header so the brand list and all the steps fit on the page. }
  TvPage := CreateInputOptionPage(wpSelectTasks, CustomMessage('TvTitle'), CustomMessage('TvIntro'), '', True, True);
  TvPage.Add('Google TV');
  TvPage.Add('Xiaomi');
  TvPage.Add('TCL');
  TvPage.Add('Sony');
  TvPage.Add('Hisense');
  TvPage.Add(CustomMessage('TvOther'));
  TvPage.SelectedValueIndex := 0;
  TvPage.CheckListBox.Height := ScaleY(100);
  TvPage.CheckListBox.OnClickCheck := @ShowSteps;

  Steps := TNewStaticText.Create(TvPage);
  Steps.Parent := TvPage.Surface;
  Steps.Top := TvPage.CheckListBox.Top + TvPage.CheckListBox.Height + ScaleY(8);
  Steps.Width := TvPage.SurfaceWidth;
  Steps.AutoSize := False;
  Steps.WordWrap := True;
  Steps.Height := TvPage.SurfaceHeight - Steps.Top;
  ShowSteps(nil);
end;
