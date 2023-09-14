from sapgui import sapgui


def zmpua25(session, *args) -> None:
    """
    Function to run zmpua25 code.
    :param session: parameter obtained from sapgui.
    :param args: variant:str, product_id: DataFrame
    :return: None.
    """
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "ZMPUA25"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/tbar[1]/btn[17]").press()
    session.findById("wnd[1]/usr/txtV-LOW").text = args[0]
    session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
    session.findById("wnd[1]/usr/txtV-LOW").caretPosition = 6
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    args[1].to_clipboard(index=False, header=None)
    session.findById(r"wnd[0]/usr/btn%_R_MATNR_%_APP_%-VALU_PUSH").press()
    session.findById("wnd[1]/tbar[0]/btn[16]").press()
    session.findById("wnd[1]/tbar[0]/btn[24]").press()
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[0]").sendVKey(8)
    session.findById("wnd[0]/tbar[1]/btn[45]").press()
    session.findById(r"wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    sapgui.sap_download_tmp_file_del()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = sapgui.SAP_TMP_PATH
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = sapgui.SAP_TMP_FILE
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = "0000"
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[0]").sendVKey(3)
    session.findById("wnd[0]").sendVKey(3)


def rrp4(session, *args) -> None:
    """
    Function to run rrp4 code.
    :param session: parameter obtained from sapgui.
    :param args: variant:str, dateFrom:str, dateTo:str,
                 product_id: DataFrame, layout: str
    :return: None
    """
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "/n/sapapo/RRP4"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/tbar[1]/btn[17]").press()
    session.findById("wnd[1]/usr/txtV-LOW").text = args[0]
    session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
    session.findById("wnd[1]").sendVKey(8)
    session.findById("wnd[0]/usr/ctxtSV_DTSTA").text = args[1]
    session.findById("wnd[0]/usr/ctxtSV_DTEND").text = args[2]
    args[3].to_clipboard(index=False, header=None)
    session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSELSCR1/ssub%_SUBSCREEN_SELBLOCK:/SAPAPO/SAPLRRP_PT_ENTRY:2010/btn%_SO_MATNR_%_APP_%-VALU_PUSH").press()
    session.findById("wnd[1]/tbar[0]/btn[16]").press()
    session.findById("wnd[1]/tbar[0]/btn[24]").press()
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[0]").sendVKey(8)
    try:
        session.findById("wnd[0]/usr/subREQMTS:/SAPAPO/SAPLRRP_REQMTS:3000/cntlALV_GRID_REQMTS/shellcont/shell").pressToolbarButton("ORGRID_TOOLBAR_EXPAND")
    except Exception as e:
        print(e)
    session.findById("wnd[0]/usr/subREQMTS:/SAPAPO/SAPLRRP_REQMTS:3000/cntlALV_GRID_REQMTS/shellcont/shell").pressToolbarButton("&MB_VARIANT")
    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").contextMenu()
    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").selectContextMenuItem("&FIND")
    session.findById("wnd[2]/usr/chkGS_SEARCH-EXACT_WORD").Selected = True
    session.findById("wnd[2]/usr/txtGS_SEARCH-VALUE").text = args[4]
    session.findById("wnd[2]/tbar[0]/btn[0]").press()
    session.findById("wnd[2]/tbar[0]/btn[12]").press()
    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").clickCurrentCell()
    session.findById("wnd[0]/usr/subREQMTS:/SAPAPO/SAPLRRP_REQMTS:3000/cntlALV_GRID_REQMTS/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
    session.findById("wnd[0]/usr/subREQMTS:/SAPAPO/SAPLRRP_REQMTS:3000/cntlALV_GRID_REQMTS/shellcont/shell").selectContextMenuItem("&PC")
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").Select()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    sapgui.sap_download_tmp_file_del()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = sapgui.SAP_TMP_PATH
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = sapgui.SAP_TMP_FILE
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = "0000"
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[0]").sendVKey(3)
    session.findById("wnd[0]").sendVKey(3)


def rrp1(session, *args) -> None:
    """
    Function to run rrp1 code.
    :param session: parameter obtained from sapgui.
    :param args: variant:str, dateFrom:str, dateTo:str,
                 product_id: DataFrame, layout: str
    :return: None
    """
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "/n/sapapo/RRP1"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/tbar[1]/btn[17]").press()
    session.findById("wnd[1]/usr/txtV-LOW").text = args[0]
    session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
    session.findById("wnd[1]").sendVKey(8)
    session.findById("wnd[0]/usr/ctxtSV_DTSTA").text = args[1]
    session.findById("wnd[0]/usr/ctxtSV_DTEND").text = args[2]
    args[3].to_clipboard(index=False, header=None)
    session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSELSCR1/ssub%_SUBSCREEN_SELBLOCK:/SAPAPO/SAPLRRP_PT_ENTRY:2010/btn%_SO_MATNR_%_APP_%-VALU_PUSH").press()
    session.findById("wnd[1]/tbar[0]/btn[16]").press()
    session.findById("wnd[1]/tbar[0]/btn[24]").press()
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[0]").sendVKey(8)
    try:
        session.findById("wnd[0]/usr/subREQMTS:/SAPAPO/SAPLRRP_REQMTS:3000/cntlALV_GRID_REQMTS/shellcont/shell").pressToolbarButton("ORGRID_TOOLBAR_EXPAND")
    except Exception as e:
        print(e)
    session.findById("wnd[0]/usr/subREQMTS:/SAPAPO/SAPLRRP_REQMTS:3000/cntlALV_GRID_REQMTS/shellcont/shell").pressToolbarButton("&MB_VARIANT")
    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").contextMenu()
    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").selectContextMenuItem("&FIND")
    session.findById("wnd[2]/usr/chkGS_SEARCH-EXACT_WORD").Selected = True
    session.findById("wnd[2]/usr/txtGS_SEARCH-VALUE").text = args[4]
    session.findById("wnd[2]/tbar[0]/btn[0]").press()
    session.findById("wnd[2]/tbar[0]/btn[12]").press()
    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").clickCurrentCell()
    session.findById("wnd[0]/usr/subREQMTS:/SAPAPO/SAPLRRP_REQMTS:3000/cntlALV_GRID_REQMTS/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
    session.findById("wnd[0]/usr/subREQMTS:/SAPAPO/SAPLRRP_REQMTS:3000/cntlALV_GRID_REQMTS/shellcont/shell").selectContextMenuItem("&PC")
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").Select()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    sapgui.sap_download_tmp_file_del()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = sapgui.SAP_TMP_PATH
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = sapgui.SAP_TMP_FILE
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = "0000"
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[0]").sendVKey(3)
    session.findById("wnd[0]").sendVKey(3)


def zpp_mat(session, *args, **kwargs) -> None:
    """
    Function to run zpp_mat code.
    :param session: parameter obtained from sapgui.
    :param args: variant:str, variable: DataFrame according to option
    :param kwargs: option:str, to change function behaviour
    :return: None
    """
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "zpp_mat"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/tbar[1]/btn[17]").press()
    session.findById("wnd[1]/usr/txtV-LOW").text = args[0]
    session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
    session.findById("wnd[1]").sendVKey(8)
    if 'option' not in kwargs or kwargs['option'] == 'ID':
        args[1].to_clipboard(index=False, header=None)
        session.findById("wnd[0]/usr/btn%_SO_MATNR_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/tbar[0]/btn[24]").press()
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[0]").sendVKey(8)
    session.findById("wnd[0]/tbar[1]/btn[45]").press()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").Select()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    sapgui.sap_download_tmp_file_del()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = sapgui.SAP_TMP_PATH
    if 'file_name' in kwargs:
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = kwargs['file_name']
    else:
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = sapgui.SAP_TMP_FILE
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = "0000"
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").caretPosition = 4
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[0]").sendVKey(3)
    session.findById("wnd[0]").sendVKey(3)


def mb52(session, *args, **kwargs) -> None:
    """
    Function to run mb52 code.
    :param session: parameter obtained from sapgui.
    :param args: variant:str, variable: DataFrame according to option
    :param kwargs: option:str, to change function behaviour
    :return: None
    """
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "mb52"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/tbar[1]/btn[17]").press()
    session.findById("wnd[1]/usr/txtV-LOW").text = args[0]
    session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    if 'option' in kwargs and kwargs['option'] == 'ID':
        args[1].to_clipboard(index=False, header=None)
        session.findById("wnd[0]/usr/btn%_MATNR_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/tbar[0]/btn[24]").press()
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[0]").sendVKey(8)
    session.findById("wnd[0]/tbar[1]/btn[45]").press()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").Select()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").SetFocus()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = sapgui.SAP_TMP_PATH
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = sapgui.SAP_TMP_FILE
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = "0000"
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").SetFocus()
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").caretPosition = 4
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[0]").sendVKey(3)
    session.findById("wnd[0]").sendVKey(3)


def me2m(session, *args, **kwargs) -> None:
    """
    Function to run me2m code.
    :param session: parameter obtained from sapgui.
    :param args: variant:str
    :param kwargs: optional variables: date_from, date_to in format %Y-%m-%d
    :return: None
    """
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "me2m"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/tbar[1]/btn[17]").press()
    session.findById("wnd[1]/usr/txtV-LOW").text = args[0]
    session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
    session.findById("wnd[1]").sendVKey(8)
    if 'date_from' in kwargs:
        session.findById("wnd[0]/usr/ctxtS_EINDT-LOW").text = kwargs['date_from']
    if 'date_to' in kwargs:
        session.findById("wnd[0]/usr/ctxtS_EINDT-HIGH").text = kwargs['date_to']
    session.findById("wnd[0]").sendVKey(8)
    session.findById("wnd[0]/tbar[1]/btn[45]").press()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").Select()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = sapgui.SAP_TMP_PATH
    if 'file_name' in kwargs:
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = kwargs['file_name']
    else:
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = sapgui.SAP_TMP_FILE
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = "0000"
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").SetFocus()
    session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").caretPosition = 4
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[0]").sendVKey(3)
    session.findById("wnd[0]").sendVKey(3)