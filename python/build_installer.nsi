# NSIS script for creating the Windows installer file.
#
# Installs the following:
#   .py scripts and requisite button icons and graphics
#   pdf document
#   path
#   uninstaller
#   uninstaller shurtcut
#   start menu shortcut for GUI tool and pdf document
#   registry information including uninstaller information

# Assign VERSION externally with -DVERSION=<ver>
!ifndef VERSION
	!echo "VERSION is required."
	!echo "example usage: makensis -DVERSION=1.0.0 build_installer.nsi"
	!error "Invalid usage"
!endif

!define APPNAME "MP_Gryphon_GUI ${VERSION}"
!define REG_SUB_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
!define COMPANYNAME "Naval Postgraduate School"
!define DESCRIPTION "MP Gryphon GUI Tool"

# These will be displayed by the "Click here for support information" link in "Add/Remove Programs"
# It is possible to use "mailto:" links here to open the email client
!define HELPURL "//https://gitlab.nps.edu/bdallen/MP_Gryphon_GUI" # "Support Information" link
!define UPDATEURL "//https://gitlab.nps.edu/bdallen/MP_Gryphon_GUI" # "Product Updates" link
!define ABOUTURL "//https://gitlab.nps.edu/bdallen/MP_Gryphon_GUI" # "Publisher" link

SetCompressor lzma
 
RequestExecutionLevel admin
 
InstallDir "$PROGRAMFILES64\${APPNAME}"
 
Name "${APPNAME}"
	outFile "MP_Gryphon_GUI-${VERSION}-windowsinstaller.exe"
 
!include LogicLib.nsh
 
page components
Page instfiles
UninstPage instfiles
 
!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
	messageBox mb_iconstop "Administrator rights required!"
	setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
	quit
${EndIf}
!macroend

Section "MP_Gryphon_GUI"
        # establish out path
        setOutPath "$INSTDIR"

	# install Registry information
	WriteRegStr HKLM "${REG_SUB_KEY}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
	WriteRegStr HKLM "${REG_SUB_KEY}" "QuietUninstallString" "$INSTDIR\uninstall.exe /S"
	WriteRegStr HKLM "${REG_SUB_KEY}" "InstallLocation" "$INSTDIR"
	WriteRegStr HKLM "${REG_SUB_KEY}" "Publisher" "${COMPANYNAME}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "HelpLink" "${HELPURL}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "URLUpdateInfo" "${UPDATEURL}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "URLInfoAbout" "${ABOUTURL}"
	WriteRegStr HKLM "${REG_SUB_KEY}" "DisplayVersion" "${VERSION}"
	# There is no option for modifying or repairing the install
	WriteRegDWORD HKLM "${REG_SUB_KEY}" "NoModify" 1
	WriteRegDWORD HKLM "${REG_SUB_KEY}" "NoRepair" 1

	# install the uninstaller
	# create the uninstaller
	writeUninstaller "$INSTDIR\uninstall.exe"
 
        # install all .py files
        file "*.py"

        # install the launcher
        file "MP_Gryphon_GUI.bat"

        # install examples
        setOutPath "$INSTDIR\examples"
        file "examples/*.mp"

        # install examples/tests
        setOutPath "$INSTDIR\examples\tests"
        file "examples/tests/*.mp"

        # install icons
        setOutPath "$INSTDIR\icons"
        file "icons/*.png"

        # install html
        setOutPath "$INSTDIR\html"
        file "html/*.html"

        # install logos
        setOutPath "$INSTDIR\images"
        file "images/*.png"
        file "images/*.jpg"
        file "images/*.jpeg"
        file "images/*.gif"

        # install the PDF doc
        setOutPath "$INSTDIR\pdf"
        file "../doc/mp_py_um/mp_py_um.pdf"

        # restore outpath
        setOutPath "$INSTDIR"

	# create the start menu for shortcuts
	createDirectory "$SMPROGRAMS\${APPNAME}"

#	# link the GUI tool to the start menu
#	createShortCut "$SMPROGRAMS\${APPNAME}\MP_Gryphon_GUI.lnk" "$INSTDIR\mp.py"

	# link the launcher to the start menu
	createShortCut "$SMPROGRAMS\${APPNAME}\MP_Gryphon_GUI.lnk" "$INSTDIR\MP_Gryphon_GUI.bat"

        # link the PDF doc to the start menu
        createShortCut "$SMPROGRAMS\${APPNAME}\MP_Gryphon_GUI Users Manual.lnk" "$INSTDIR\pdf\mp_py_um.pdf"

	# link the uninstaller to the start menu
	createShortCut "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\uninstall.exe"

sectionEnd

function .onInit
        # require admin
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

function un.onInit
	SetShellVarContext all
 
	#Verify the uninstaller - last chance to back out
	MessageBox MB_OKCANCEL "Permanantly remove ${APPNAME}?" IDOK next
		Abort
	next:
	!insertmacro VerifyUserIsAdmin
functionEnd
 
Function un.FailableDelete
	Start:
	delete "$0"
	IfFileExists "$0" FileStillPresent Continue

	FileStillPresent:
	DetailPrint "Unable to delete file $0, likely because it is in use.  Please close the MP_Gryphon_GUI application and try again."
	MessageBox MB_ICONQUESTION|MB_RETRYCANCEL \
		"Unable to delete file $0, \
		likely because it is in use.  \
		Please close the MP_Gryphon_GUI and try again." \
 		/SD IDABORT IDRETRY Start IDABORT InstDirAbort

	# abort
	InstDirAbort:
	DetailPrint "Uninstall started but did not complete."
	Abort

	# continue
	Continue:
FunctionEnd

section "uninstall"
	# manage uninstalling openable files
	StrCpy $0 "$INSTDIR\MP_Gryphon_GUI.bat"
	Call un.FailableDelete
	StrCpy $0 "$INSTDIR\mp.py"
	Call un.FailableDelete
	StrCpy $0 "$INSTDIR\pdf\mp_py_um.pdf"
	Call un.FailableDelete

        # uninstall all support code
        delete "$INSTDIR\*.py"

        # uninstall examples/tests
        delete "$INSTDIR\examples\tests\*.mp"
        rmdir "$INSTDIR\examples\tests"

        # uninstall examples
        delete "$INSTDIR\examples\*.mp"
        rmdir "$INSTDIR\examples"

        # uninstall the button icons
        delete "$INSTDIR\icons\*.png"
        rmdir "$INSTDIR\icons"

        # uninstall HTML
        delete "$INSTDIR\html\*.html"
        rmdir "$INSTDIR\html"

        # uninstall logos
        delete "$INSTDIR\images\*.png"
        delete "$INSTDIR\images\*.jpg"
        delete "$INSTDIR\images\*.jpeg"
        delete "$INSTDIR\images\*.gif"
        rmdir "$INSTDIR\images"

        # uninstall the pdf directory
        rmdir "$INSTDIR\pdf"

	# uninstall Start Menu launcher shortcuts
	delete "$SMPROGRAMS\${APPNAME}\MP_Gryphon_GUI.lnk"
	delete "$SMPROGRAMS\${APPNAME}\MP_Gryphon_GUI Users Manual.lnk"
	delete "$SMPROGRAMS\${APPNAME}\uninstall ${APPNAME}.lnk"
	rmDir "$SMPROGRAMS\${APPNAME}"

	# delete the uninstaller
	delete "$INSTDIR\uninstall.exe"
 
	# Try to remove the install directory
	rmDir "$INSTDIR"
 
	# Remove uninstaller information from the registry
	DeleteRegKey HKLM "${REG_SUB_KEY}"
sectionEnd

