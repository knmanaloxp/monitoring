#define MyAppName "Network Agent"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Network Agent"
#define MyAppExeName "network_agent.exe"

[Setup]
AppId={{F8A47954-3E7C-4562-9C73-A10E6A3B376F}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=NetworkAgentSetup
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=dist\{#MyAppExeName}
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Start with Windows"; GroupDescription: "Windows Startup"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "dist\*.pyd"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Dirs]
Name: "{app}\logs"; Flags: uninsalwaysuninstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: "\"{app}\{#MyAppExeName}\""; Flags: uninsdeletevalue; Tasks: startupicon
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1"; ValueType: string; ValueName: "UninstallString"; ValueData: "\"{uninstallexe}\""
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\{#MyAppExeName}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent runhidden

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden

[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.pyd"
Type: files; Name: "{app}\*.dll"
Type: dirifempty; Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usUninstall:
      begin
        // Remove startup entry
        RegDeleteValue(HKEY_LOCAL_MACHINE, 'Software\Microsoft\Windows\CurrentVersion\Run', '{#MyAppName}');
      end;
  end;
end;