wscript = WScript.CreateObject('WScript.Shell');
wscript.run("cmd.exe /c \"<malicious powershell>;\"", "0");
