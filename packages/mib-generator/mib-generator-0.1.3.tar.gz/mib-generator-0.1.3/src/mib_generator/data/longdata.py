"""Here various data that would otherwise cluster the code elsewhere are stored.

This module includes mostly information about the structures of the MIB tables and characteristics
that are specified for each entry in them. For each MIB table, there is an module-wide attribute
here that through a list of dictionaries specifies, what the names and characteristics (type, length, whether
mandatory) entries in each column of this table should have. All of these lists are then joined in one
dictionary :obj:`tables_format` from which any characteristics of MIB tables can be extracted.

Attributes:
    
    pid (list): List of dictionaries each entry of which corresponds to information about an entry in one
        column in the pid table. Lists like this are stored in this module for every MIB table.
    sizes (dict): A lookup dictionary which links every number constant type with its bite-size.
    tables_format (dict): A dictionary created from list like :obj:`pid` above specified for each MIB tables.
        Allows for easy access to these information.
    unique_entries (dict): A dictionary which for each MIB table (specified by its name) states what colums or
        groups of columns should hole unique/non-repeating entries (e.g. there should be only one entry in pid
        column "PID_TYPE" for a packet of given type.).
    uint_pfc (list): List that states what pfc type (given by the order in the list) should be linked to a 
        integer constant of a given C-type.
    time_pfc (list): List that states what pfc type (given by the order in the list) should be linked to a 
        time-describing constant of a given allocation of bites for fine/course time.
    translation (dict): A lookup dictionary stating what descriptions should be given to each attribute of the
        Python representations of C-objects in order to make the entries more human-readable in the GUI visualisation.
"""
pid = [
    {"name": "PID_TYPE", "type": ["n", 3], "mandatory": True},
    {"name": "PID_STYPE", "type": ["n", 3], "mandatory": True},
    {"name": "PID_APID", "type": ["n", 5], "mandatory": True},
    {"name": "PID_PI1_VAL", "type": ["n", 10], "mandatory": False},
    {"name": "PIC_PI2_VAL", "type": ["n", 10], "mandatory": False},
    {"name": "PID_SPID", "type": ["n", 10], "mandatory": True},
    {"name": "PID_DESCR", "type": ["c", 64], "mandatory": False},
    {"name": "PID_UNIT", "type": ["c", 8], "mandatory": False},
    {"name": "PID_TPSD", "type": ["n", 10], "mandatory": False},
    {"name": "PID_DFHSIZE", "type": ["n", 12], "mandatory": True},
    {"name": "PID_TIME", "type": ["c", 1], "mandatory": False},
    {"name": "PID_INTER", "type": ["n", 8], "mandatory": False},
    {"name": "PID_VALID", "type": ["c", 1], "mandatory": False},
    {"name": "PID_CHECK", "type": ["n", 1], "mandatory": False},
    {"name": "PID_EVENT", "type": ["c", 1], "mandatory": False},
    {"name": "PIC_EVID", "type": ["c", 17], "mandatory": False},
]
pic = [
    {"name": "PIC_TYPE", "type": ["n", 3], "mandatory": True},
    {"name": "PIC_STYPE", "type": ["n", 3], "mandatory": True},
    {"name": "PIC_PI1_OFF", "type": ["n", 5], "mandatory": True},
    {"name": "PIC_PI1_WID", "type": ["n", 3], "mandatory": True},
    {"name": "PIC_PI2_OFF", "type": ["n", 5], "mandatory": True},
    {"name": "PIC_PI2_WID", "type": ["n", 3], "mandatory": True},
    {"name": "PIC_APID", "type": ["n", 5], "mandatory": False},
]
tpcf = [
    {"name": "TPCF_SPID", "type": ["n", 10], "mandatory": True},
    {"name": "TPCF_NAME", "type": ["c", 12], "mandatory": False},
    {"name": "TPCF_SIZE", "type": ["n", 8], "mandatory": False},
]
pcf = [
    {"name": "PCF_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "PCF_DESCR", "type": ["c", 24], "mandatory": False},
    {"name": "PCF_PID", "type": ["n", 10], "mandatory": False},
    {"name": "PCF_UNIT", "type": ["c", 4], "mandatory": False},
    {"name": "PCF_PTC", "type": ["n", 2], "mandatory": True},
    {"name": "PCF_PFC", "type": ["n", 5], "mandatory": True},
    {"name": "PCF_WIDTH", "type": ["n", 6], "mandatory": False},
    {"name": "PCF_VALID", "type": ["c", 8], "mandatory": False},
    {"name": "PCF_RELATED", "type": ["c", 8], "mandatory": False},
    {"name": "PCF_CATEG", "type": ["c", 1], "mandatory": True},
    {"name": "PCF_NATUR", "type": ["c", 1], "mandatory": True},
    {"name": "PCF_CURTX", "type": ["c", 10], "mandatory": False},
    {"name": "PCF_INTER", "type": ["c", 1], "mandatory": False},
    {"name": "PCF_USCON", "type": ["c", 1], "mandatory": False},
    {"name": "PCF_DECIM", "type": ["n", 3], "mandatory": False},
    {"name": "PCF_PARVAL", "type": ["c", 14], "mandatory": False},
    {"name": "PCF_SUBSYS", "type": ["c", 8], "mandatory": False},
    {"name": "PCF_VALPAR", "type": ["n", 5], "mandatory": False},
    {"name": "PCF_SPTYPE", "type": ["c", 1], "mandatory": False},
    {"name": "PCF_CORR", "type": ["c", 1], "mandatory": False},
    {"name": "PCF_OBTID", "type": ["n", 5], "mandatory": False},
    {"name": "PCF_DARC", "type": ["c", 1], "mandatory": False},
    {"name": "PCF_ENDIAN", "type": ["c", 1], "mandatory": False},
    {"name": "PCF_DESCR2", "type": ["c", 256], "mandatory": False},
]
plf = [
    {"name": "PLF_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "PLF_SPID", "type": ["n", 10], "mandatory": True},
    {"name": "PLF_OFFBY", "type": ["n", 5], "mandatory": True},
    {"name": "PLF_OFFBI", "type": ["n", 1], "mandatory": True},
    {"name": "PLF_NBOCC", "type": ["n", 4], "mandatory": False},
    {"name": "PLF_LGOCC", "type": ["n", 5], "mandatory": False},
    {"name": "PLF_TIME", "type": ["n", 9], "mandatory": False},
    {"name": "PLF_TDOCC", "type": ["n", 9], "mandatory": False},
]
vpd = [
    {"name": "VPD_TPSD", "type": ["n", 10], "mandatory": True},
    {"name": "VPD_POS", "type": ["n", 4], "mandatory": True},
    {"name": "VPD_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "VPD_GRPSIZE", "type": ["n", 3], "mandatory": False},
    {"name": "VPD_FIXREP", "type": ["n", 3], "mandatory": False},
    {"name": "VPD_CHOICE", "type": ["c", 1], "mandatory": False},
    {"name": "VPD_PIDREF", "type": ["c", 1], "mandatory": False},
    {"name": "VPD_DISDESC", "type": ["c", 16], "mandatory": True},
    {"name": "VPD_WIDTH", "type": ["n", 2], "mandatory": True},
    {"name": "VPD_JUSTIFY", "type": ["c", 1], "mandatory": False},
    {"name": "VPD_NEWLINE", "type": ["c", 1], "mandatory": False},
    {"name": "VPD_DCHAR", "type": ["n", 1], "mandatory": False},
    {"name": "VPD_FORM", "type": ["c", 1], "mandatory": False},
    {"name": "VPD_OFFSET", "type": ["n", 6], "mandatory": False},
]
grp = [
    {"name": "GRP_NAME", "type": ["c", 14], "mandatory": True},
    {"name": "GRP_DESCR", "type": ["n", 24], "mandatory": True},
    {"name": "GRP_GTYPE", "type": ["c", 2], "mandatory": True},
]
grpa = [
    {"name": "GRPA_GNAME", "type": ["c", 14], "mandatory": True},
    {"name": "GRPA_PANAME", "type": ["c", 8], "mandatory": True},
]
grpk = [
    {"name": "GRPK_GNAME", "type": ["c", 14], "mandatory": True},
    {"name": "GRPK_PKSPID", "type": ["n", 10], "mandatory": True},
]
dpf = [
    {"name": "DPF_NUMBE", "type": ["c", 8], "mandatory": True},
    {"name": "DPF_TYPE", "type": ["c", 1], "mandatory": True},
    {"name": "DPF_HEAD", "type": ["c", 32], "mandatory": False},
]
dpc = [
    {"name": "DPC_NUMBE", "type": ["c", 8], "mandatory": True},
    {"name": "DPC_NAME", "type": ["c", 8], "mandatory": False},
    {"name": "DPC_FLDN", "type": ["n", 2], "mandatory": True},
    {"name": "DPC_COMM", "type": ["n", 4], "mandatory": False},
    {"name": "DPC_MODE", "type": ["c", 1], "mandatory": False},
    {"name": "DPC_FORM", "type": ["c", 1], "mandatory": False},
    {"name": "DPC_TEXT", "type": ["c", 32], "mandatory": False},
]
gpf = [
    {"name": "GPF_NUMBE", "type": ["c", 8], "mandatory": True},
    {"name": "GPF_TYPE", "type": ["c", 1], "mandatory": True},
    {"name": "GPF_HEAD", "type": ["c", 32], "mandatory": False},
    {"name": "GPF_SCROL", "type": ["c", 1], "mandatory": False},
    {"name": "GPF_HCOPY", "type": ["c", 1], "mandatory": False},
    {"name": "GPF_DAYS", "type": ["n", 2], "mandatory": True},
    {"name": "GPF_HOURS", "type": ["n", 2], "mandatory": True},
    {"name": "GPF_MINUT", "type": ["n", 2], "mandatory": True},
    {"name": "GPF_AXCLR", "type": ["c", 1], "mandatory": True},
    {"name": "GPF_XTICK", "type": ["n", 2], "mandatory": True},
    {"name": "GPF_YTICK", "type": ["n", 2], "mandatory": True},
    {"name": "GPF_XGRID", "type": ["n", 2], "mandatory": True},
    {"name": "GPF_YGRID", "type": ["n", 2], "mandatory": True},
    {"name": "GPF_UPUN", "type": ["n", 2], "mandatory": False},
]
gpc = [
    {"name": "GPC_NUMBE", "type": ["c", 8], "mandatory": True},
    {"name": "GPC_POS", "type": ["n", 1], "mandatory": True},
    {"name": "GPC_WHERE", "type": ["c", 1], "mandatory": True},
    {"name": "GPC_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "GPC_RAW", "type": ["c", 1], "mandatory": False},
    {"name": "GPC_MINIM", "type": ["c", 14], "mandatory": True},
    {"name": "GPC_MAXIM", "type": ["c", 14], "mandatory": True},
    {"name": "GPC_PRCLR", "type": ["c", 1], "mandatory": True},
    {"name": "GPC_SYMBO", "type": ["c", 1], "mandatory": False},
    {"name": "GPC_LINE", "type": ["c", 1], "mandatory": False},
    {"name": "GPC_DOMAIN", "type": ["n", 5], "mandatory": False},
]
spf = [
    {"name": "SPF_NUMBE", "type": ["c", 8], "mandatory": True},
    {"name": "SPF_HEAD", "type": ["c", 32], "mandatory": False},
    {"name": "SPF_NPAR", "type": ["n", 1], "mandatory": True},
    {"name": "SPF_UPUN", "type": ["n", 2], "mandatory": False},
]
mcf = [
    {"name": "MCF_IDENT", "type": ["c", 10], "mandatory": True},
    {"name": "MCF_DESCR", "type": ["c", 32], "mandatory": False},
    {"name": "MCF_POL1", "type": ["c", 14], "mandatory": True},
    {"name": "MCF_POL2", "type": ["c", 14], "mandatory": False},
    {"name": "MCF_POL3", "type": ["c", 14], "mandatory": False},
    {"name": "MCF_POL4", "type": ["c", 14], "mandatory": False},
    {"name": "MCF_POL5", "type": ["c", 14], "mandatory": False},
]
spc = [
    {"name": "SPC_NUMBE", "type": ["c", 8], "mandatory": True},
    {"name": "SPC_POS", "type": ["n", 1], "mandatory": True},
    {"name": "SPC_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "SPC_UPDT", "type": ["c", 1], "mandatory": False},
    {"name": "SPC_MODE", "type": ["c", 1], "mandatory": False},
    {"name": "SPC_FORM", "type": ["c", 1], "mandatory": False},
    {"name": "SPC_BACK", "type": ["c", 1], "mandatory": False},
    {"name": "SPC_FORE", "type": ["c", 1], "mandatory": True},
]
ppf = [
    {"name": "PPF_NUMBE", "type": ["c", 4], "mandatory": True},
    {"name": "PPF_HEAD", "type": ["c", 32], "mandatory": False},
    {"name": "PPF_NBPR", "type": ["n", 2], "mandatory": False},
]
ppc = [
    {"name": "PPC_NUMBE", "type": ["c", 4], "mandatory": True},
    {"name": "PPC_POS", "type": ["n", 2], "mandatory": True},
    {"name": "PPC_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "PPC_FORM", "type": ["c", 1], "mandatory": False},
]
tcp = [
    {"name": "TCP_ID", "type": ["c", 8], "mandatory": True},
    {"name": "TCP_DESC", "type": ["c", 24], "mandatory": False},
]
pcpc = [
    {"name": "PCPC_PNAME", "type": ["c", 8], "mandatory": True},
    {"name": "PCPC_DESC", "type": ["c", 24], "mandatory": True},
    {"name": "PCPC_CODE", "type": ["c", 1], "mandatory": False},
]
pcdf = [
    {"name": "PCDF_TCNAME", "type": ["c", 8], "mandatory": True},
    {"name": "PCDF_DESC", "type": ["c", 24], "mandatory": False},
    {"name": "PCDF_TYPE", "type": ["c", 1], "mandatory": True},
    {"name": "PCDF_LEN", "type": ["n", 4], "mandatory": True},
    {"name": "PCDF_BIT", "type": ["n", 4], "mandatory": True},
    {"name": "PCDF_PNAME", "type": ["c", 8], "mandatory": False},
    {"name": "PCDF_VALUE", "type": ["c", 10], "mandatory": True},
    {"name": "PCDF_RADIX", "type": ["c", 1], "mandatory": False},
]
ccf = [
    {"name": "CCF_CNAME", "type": ["c", 8], "mandatory": True},
    {"name": "CCF_DESCR", "type": ["c", 24], "mandatory": True},
    {"name": "CCF_DESCR2", "type": ["c", 64], "mandatory": False},
    {"name": "CCF_CTYPE", "type": ["c", 8], "mandatory": False},
    {"name": "CCF_CRITICAL", "type": ["c", 1], "mandatory": False},
    {"name": "CCF_PKTID", "type": ["c", 8], "mandatory": True},
    {"name": "CCF_TYPE", "type": ["n", 3], "mandatory": False},
    {"name": "CCF_STYPE", "type": ["n", 3], "mandatory": False},
    {"name": "CCF_APID", "type": ["n", 5], "mandatory": False},
    {"name": "CCF_NPARS", "type": ["n", 3], "mandatory": False},
    {"name": "CCF_PLAN", "type": ["c", 1], "mandatory": False},
    {"name": "CCF_EXEC", "type": ["c", 1], "mandatory": False},
    {"name": "CCF_ILSCOPE", "type": ["c", 1], "mandatory": False},
    {"name": "CCF_ILSTAGE", "type": ["c", 1], "mandatory": False},
    {"name": "CCF_SUBSYS", "type": ["n", 3], "mandatory": False},
    {"name": "CCF_HIPRI", "type": ["c", 1], "mandatory": False},
    {"name": "CCF_MAPID", "type": ["n", 2], "mandatory": False},
    {"name": "CCF_DEFSET", "type": ["c", 8], "mandatory": False},
    {"name": "CCF_RAPID", "type": ["n", 5], "mandatory": False},
    {"name": "CCF_ACK", "type": ["n", 2], "mandatory": False},
    {"name": "CCF_SUBSCHEDID", "type": ["n", 5], "mandatory": False},
]
dst = [
    {"name": "DST_APID", "type": ["n", 5], "mandatory": True},
    {"name": "DST_ROUTE", "type": ["c", 30], "mandatory": True},
]
cpc = [
    {"name": "CPC_PNAME", "type": ["c", 8], "mandatory": True},
    {"name": "CPC_DESCR", "type": ["c", 24], "mandatory": False},
    {"name": "CPC_PTC", "type": ["n", 2], "mandatory": True},
    {"name": "CPC_PFC", "type": ["n", 5], "mandatory": True},
    {"name": "CPC_DISPFMT", "type": ["c", 1], "mandatory": False},
    {"name": "CPC_RADIX", "type": ["c", 1], "mandatory": False},
    {"name": "CPC_UNIT", "type": ["c", 4], "mandatory": False},
    {"name": "CPC_CATEG", "type": ["c", 1], "mandatory": False},
    {"name": "CPC_PRFREF", "type": ["c", 10], "mandatory": False},
    {"name": "CPC_CCAREF", "type": ["c", 10], "mandatory": False},
    {"name": "CPC_PAFREF", "type": ["c", 10], "mandatory": False},
    {"name": "CPC_INTER", "type": ["c", 1], "mandatory": False},
    {"name": "CPC_DEFVAL", "type": ["c", 999], "mandatory": False},
    {"name": "CPC_CORR", "type": ["c", 1], "mandatory": False},
    {"name": "CPC_OBTID", "type": ["n", 5], "mandatory": False},
    {"name": "CPC_DESCR2", "type": ["c", 256], "mandatory": False},
    {"name": "CPC_ENDIAN", "type": ["c", 1], "mandatory": False},
]
cdf = [
    {"name": "CDF_CNAME", "type": ["c", 8], "mandatory": True},
    {"name": "CDF_ELTYPE", "type": ["c", 1], "mandatory": True},
    {"name": "CDF_DESCR", "type": ["c", 24], "mandatory": False},
    {"name": "CDF_ELLEN", "type": ["n", 4], "mandatory": True},
    {"name": "CDF_BIT", "type": ["n", 4], "mandatory": True},
    {"name": "CDF_GRPSIZE", "type": ["n", 2], "mandatory": False},
    {"name": "CDF_PNAME", "type": ["c", 8], "mandatory": False},
    {"name": "CDF_INTER", "type": ["c", 1], "mandatory": False},
    {"name": "CDF_VALUE", "type": ["c", 999], "mandatory": False},
    {"name": "CDF_TMID", "type": ["c", 8], "mandatory": False},
]
ptv = [
    {"name": "PTV_CNAME", "type": ["c", 8], "mandatory": True},
    {"name": "PTV_PARNAM", "type": ["c", 8], "mandatory": True},
    {"name": "PTV_INTER", "type": ["c", 1], "mandatory": False},
    {"name": "PTV_VAL", "type": ["c", 17], "mandatory": True},
]
csf = [
    {"name": "CSF_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "CSF_DESC", "type": ["c", 24], "mandatory": True},
    {"name": "CSF_DESC2", "type": ["c", 64], "mandatory": False},
    {"name": "CSF_IFTT", "type": ["c", 1], "mandatory": False},
    {"name": "CSF_NFPARS", "type": ["n", 3], "mandatory": False},
    {"name": "CSF_ELEMS", "type": ["n", 5], "mandatory": False},
    {"name": "CSF_CRITICAL", "type": ["c", 1], "mandatory": False},
    {"name": "CSF_PLAN", "type": ["c", 1], "mandatory": False},
    {"name": "CSF_EXEC", "type": ["c", 1], "mandatory": False},
    {"name": "CSF_SUBSYS", "type": ["n", 3], "mandatory": False},
    {"name": "CSF_GENTIME", "type": ["c", 17], "mandatory": False},
    {"name": "CSF_DOCNAME", "type": ["c", 32], "mandatory": False},
    {"name": "CSF_ISSUE", "type": ["c", 10], "mandatory": False},
    {"name": "CSF_DATE", "type": ["c", 17], "mandatory": False},
    {"name": "CSF_DEFSET", "type": ["c", 8], "mandatory": False},
    {"name": "CSF_SUBSCHEDID", "type": ["n", 5], "mandatory": False},
]
css = [
    {"name": "CSS_SQNAME", "type": ["c", 8], "mandatory": True},
    {"name": "CSS_COMM", "type": ["c", 32], "mandatory": False},
    {"name": "CSS_ENTRY", "type": ["n", 5], "mandatory": True},
    {"name": "CSS_TYPE", "type": ["c", 1], "mandatory": True},
    {"name": "CSS_ELEMID", "type": ["c", 8], "mandatory": False},
    {"name": "CSS_NPARS", "type": ["n", 3], "mandatory": False},
    {"name": "CSS_MANDISP", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_RELTYPE", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_RELTIME", "type": ["c", 12], "mandatory": False},
    {"name": "CSS_EXTIME", "type": ["c", 17], "mandatory": False},
    {"name": "CSS_PREVREL", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_GROUP", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_BLOCK", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_ILSCOPE", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_ILSTAGE", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_DYNPTV", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_STAPTV", "type": ["c", 1], "mandatory": False},
    {"name": "CSS_CEV", "type": ["c", 1], "mandatory": False},
]
sdf = [
    {"name": "SDF_SQNAME", "type": ["c", 8], "mandatory": True},
    {"name": "SDF_ENTRY", "type": ["n", 5], "mandatory": True},
    {"name": "SDF_ELEMID", "type": ["c", 8], "mandatory": True},
    {"name": "SDF_POS", "type": ["n", 4], "mandatory": True},
    {"name": "SDF_PNAME", "type": ["c", 8], "mandatory": True},
    {"name": "SDF_FTYPE", "type": ["c", 1], "mandatory": False},
    {"name": "SDF_VTYPE", "type": ["c", 1], "mandatory": True},
    {"name": "SDF_VALUE", "type": ["c", 999], "mandatory": False},
    {"name": "SDF_VALSET", "type": ["c", 8], "mandatory": False},
    {"name": "SDF_REPPOS", "type": ["n", 4], "mandatory": False},
]
csp = [
    {"name": "CSP_SQNAME", "type": ["c", 8], "mandatory": True},
    {"name": "CSP_FPNAME", "type": ["c", 8], "mandatory": True},
    {"name": "CSP_FPNUM", "type": ["n", 5], "mandatory": True},
    {"name": "CSP_DESCR", "type": ["c", 24], "mandatory": False},
    {"name": "CSP_PTC", "type": ["n", 2], "mandatory": True},
    {"name": "CSP_PFC", "type": ["n", 5], "mandatory": True},
    {"name": "CSP_DISPFMT", "type": ["c", 1], "mandatory": False},
    {"name": "CSP_RADIX", "type": ["c", 1], "mandatory": False},
    {"name": "CSP_TYPE", "type": ["c", 1], "mandatory": True},
    {"name": "CSP:VTYPE", "type": ["c", 1], "mandatory": False},
    {"name": "CSP_DEFVAL", "type": ["c", 999], "mandatory": False},
    {"name": "CSP_CATEG", "type": ["c", 1], "mandatory": False},
    {"name": "CSP_PRFREF", "type": ["c", 10], "mandatory": False},
    {"name": "CSP_CCAREF", "type": ["c", 10], "mandatory": False},
    {"name": "CSP_PAFREF", "type": ["c", 10], "mandatory": False},
    {"name": "CSP_UNIT", "type": ["c", 4], "mandatory": False},
]
cvs = [
    {"name": "CVS_ID", "type": ["n", 5], "mandatory": True},
    {"name": "CVS_TYPE", "type": ["c", 1], "mandatory": True},
    {"name": "CVS_SOURCE", "type": ["c", 1], "mandatory": True},
    {"name": "CVS_START", "type": ["n", 5], "mandatory": True},
    {"name": "CVS_INTERVAL", "type": ["n", 5], "mandatory": True},
    {"name": "CVS_SPID", "type": ["n", 10], "mandatory": False},
    {"name": "CVS_UNCERTAINTY", "type": ["n", 5], "mandatory": False},
]
cve = [
    {"name": "CVE_DVSID", "type": ["n", 5], "mandatory": True},
    {"name": "CVE_PARNAM", "type": ["c", 8], "mandatory": True},
    {"name": "CVE_INTER", "type": ["c", 1], "mandatory": False},
    {"name": "CVE_VAL", "type": ["c", 17], "mandatory": False},
    {"name": "CVE_TOL", "type": ["c", 17], "mandatory": False},
    {"name": "CVE_CHECK", "type": ["c", 1], "mandatory": False},
]
cvp = [
    {"name": "CVP_TASK", "type": ["c", 8], "mandatory": True},
    {"name": "CVP_TYPE", "type": ["c", 1], "mandatory": False},
    {"name": "CVP_CVSID", "type": ["n", 5], "mandatory": True},
]
pst = [
    {"name": "PST_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "PST_DESCR", "type": ["c", 24], "mandatory": False},
]
psv = [
    {"name": "PSV_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "PSV_PVSID", "type": ["c", 8], "mandatory": True},
    {"name": "PSV_DESCR", "type": ["c", 24], "mandatory": False},
]
cps = [
    {"name": "CPS_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "CPS_PAR", "type": ["c", 8], "mandatory": True},
    {"name": "CPS_BIT", "type": ["n", 4], "mandatory": True},
]
pvs = [
    {"name": "PVS_ID", "type": ["c", 8], "mandatory": True},
    {"name": "PVS_PSID", "type": ["c", 8], "mandatory": True},
    {"name": "PVS_PNAME", "type": ["c", 8], "mandatory": True},
    {"name": "PVS_INTER", "type": ["c", 1], "mandatory": False},
    {"name": "PVS_VALS", "type": ["c", 999], "mandatory": False},
    {"name": "PVS_BIT", "type": ["n", 4], "mandatory": True},
]
psm = [
    {"name": "PSM_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "PSM_TYPE", "type": ["c", 1], "mandatory": True},
    {"name": "PSM_PARSET", "type": ["c", 8], "mandatory": True},
]
cca = [
    {"name": "CCA_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "CCA_DESCR", "type": ["c", 24], "mandatory": False},
    {"name": "CCA_ENGFMT", "type": ["c", 1], "mandatory": False},
    {"name": "CCA_RAWFMT", "type": ["c", 1], "mandatory": False},
    {"name": "CCA_RADIX", "type": ["c", 1], "mandatory": False},
    {"name": "CCA_UNIT", "type": ["c", 4], "mandatory": False},
    {"name": "CCA_NCURVE", "type": ["n", 3], "mandatory": False},
]
ccs = [
    {"name": "CCS_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "CCS_XVALS", "type": ["c", 999], "mandatory": True},
    {"name": "CCS_YVALS", "type": ["c", 999], "mandatory": True},
]
paf = [
    {"name": "PAF_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "PAF_DESCR", "type": ["c", 24], "mandatory": False},
    {"name": "PAF_RAWFMT", "type": ["c", 1], "mandatory": False},
    {"name": "PAF_NALIAS", "type": ["n", 3], "mandatory": False},
]
pas = [
    {"name": "PAS_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "PAS_ALTXT", "type": ["c", 999], "mandatory": True},
    {"name": "PAS_ALVAL", "type": ["c", 999], "mandatory": True},
]
prf = [
    {"name": "PRF_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "PRF_DESCR", "type": ["c", 24], "mandatory": False},
    {"name": "PRF_INTER", "type": ["c", 1], "mandatory": False},
    {"name": "PRF_DSPFMT", "type": ["c", 1], "mandatory": False},
    {"name": "PRF_RADIX", "type": ["c", 1], "mandatory": False},
    {"name": "PRF_NRANGE", "type": ["n", 3], "mandatory": False},
    {"name": "PRF_UNIT", "type": ["c", 4], "mandatory": False},
]
prv = [
    {"name": "PRV_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "PRV_MINVAL", "type": ["c", 999], "mandatory": True},
    {"name": "PRV_MAXVAL", "type": ["c", 999], "mandatory": False},
]
txf = [
    {"name": "TXF_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "TXF_DESCR", "type": ["c", 32], "mandatory": False},
    {"name": "TXF_RAWFMT", "type": ["c", 1], "mandatory": True},
    {"name": "TXF_NALIAS", "type": ["n", 3], "mandatory": False},
]
txp = [
    {"name": "TXP_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "TXP_FROM", "type": ["c", 14], "mandatory": True},
    {"name": "TXP_TO", "type": ["c", 14], "mandatory": True},
    {"name": "TXP_ALTXT", "type": ["c", 14], "mandatory": True},
]
caf = [
    {"name": "CAF_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "CAF_DESCR", "type": ["c", 32], "mandatory": False},
    {"name": "CAF_ENGFMT", "type": ["c", 1], "mandatory": True},
    {"name": "CAF_RAWFMT", "type": ["c", 1], "mandatory": True},
    {"name": "CAF_RADIX", "type": ["c", 1], "mandatory": False},
    {"name": "CAF_UNIT", "type": ["c", 4], "mandatory": False},
    {"name": "CAF_NCURVE", "type": ["n", 13], "mandatory": False},
    {"name": "CAF_INTER", "type": ["c", 1], "mandatory": False},
]
cap = [
    {"name": "CAP_NUMBR", "type": ["c", 10], "mandatory": True},
    {"name": "CAP_XVALS", "type": ["c", 14], "mandatory": True},
    {"name": "CAP_YVALS", "type": ["c", 14], "mandatory": True},
]
lgf = [
    {"name": "LGF_IDENT", "type": ["c", 10], "mandatory": True},
    {"name": "LGF_DESCR", "type": ["c", 32], "mandatory": False},
    {"name": "LGF_POL1", "type": ["c", 14], "mandatory": True},
    {"name": "LGF_POL2", "type": ["c", 14], "mandatory": False},
    {"name": "LGF_POL3", "type": ["c", 14], "mandatory": False},
    {"name": "LGF_POL4", "type": ["c", 14], "mandatory": False},
    {"name": "LGF_POL5", "type": ["c", 14], "mandatory": False},
]
cur = [
    {"name": "CUR_PNAME", "type": ["c", 8], "mandatory": True},
    {"name": "CUR_POS", "type": ["n", 2], "mandatory": True},
    {"name": "CUR_RLCHK", "type": ["c", 8], "mandatory": True},
    {"name": "CUR_VALPAR", "type": ["n", 5], "mandatory": True},
    {"name": "CUR_SELECT", "type": ["c", 10], "mandatory": True},
]
vdf = [
    {"name": "VDF_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "VDF_COMMENT", "type": ["c", 32], "mandatory": False},
    {"name": "VDF_DOMAINID", "type": ["n", 5], "mandatory": False},
    {"name": "VDF_RELEASE", "type": ["n", 5], "mandatory": False},
    {"name": "VDF_ISSUE", "type": ["n", 5], "mandatory": False},
]
ocf = [
    {"name": "OCF_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "OCF_NBCHCK", "type": ["n", 2], "mandatory": True},
    {"name": "OCF_NBOOL", "type": ["n", 2], "mandatory": True},
    {"name": "OCF_INTER", "type": ["c", 1], "mandatory": True},
    {"name": "OCF_CODIN", "type": ["c", 1], "mandatory": True},
]
ocp = [
    {"name": "OCP_NAME", "type": ["c", 8], "mandatory": True},
    {"name": "OCP_POS", "type": ["n", 2], "mandatory": True},
    {"name": "OCP_TYPE", "type": ["c", 1], "mandatory": True},
    {"name": "OCP_LVALU", "type": ["c", 14], "mandatory": False},
    {"name": "OCP_HVALU", "type": ["c", 14], "mandatory": False},
    {"name": "OCP_RLCHK", "type": ["c", 8], "mandatory": False},
    {"name": "OCP_VALPAR", "type": ["n", 5], "mandatory": False},
]
sizes = {
    "uint8_t": 8,
    "uint16_t": 16,
    "uint32_t": 32,
    "uint64_t": 64,
    "unsigned int": 32,
    "enum": 32,
}
tables_format = {
    "pic": pic,
    "pid": pid,
    "pcf": pcf,
    "tpcf": tpcf,
    "plf": plf,
    "mcf": mcf,
    "txf": txf,
    "txp": txp,
    "caf": caf,
    "cap": cap,
    "lgf": lgf,
    "cur": cur,
    "vpd": vpd,
    "grp": grp,
    "grpa": grpa,
    "grpk": grpk,
    "dpf": dpf,
    "dpc": dpc,
    "gpf": gpf,
    "gpc": gpc,
    "spf": spf,
    "spc": spc,
    "ppf": ppf,
    "ppc": ppc,
    "tcp": tcp,
    "pcpc": pcpc,
    "pcdf": pcdf,
    "ccf": ccf,
    "dst": dst,
    "cpc": cpc,
    "cdf": cdf,
    "ptv": ptv,
    "csf": csf,
    "css": css,
    "sdf": sdf,
    "csp": csp,
    "cvs": cvs,
    "cve": cve,
    "cvp": cvp,
    "pst": pst,
    "psv": psv,
    "cps": cps,
    "pvs": pvs,
    "psm": psm,
    "cca": cca,
    "ccs": ccs,
    "paf": paf,
    "pas": pas,
    "prf": prf,
    "prv": prv,
    "vdf": vdf,
    "ocf": ocf,
    "ocp": ocp,
}
# I'm not entirely sure about the entries in the following table so there might be mistakes.
unique_entries = {
    "pic": [[1, 2, 7]],
    "pid": [[1, 2, 3, 4, 5, 6]],
    "pcf": [[1]],
    "tpcf": [[1]],
    "plf": [[1, 2]],
    "mcf": [[1]],
    "txf": [[1]],
    "txp": [[1, 2]],
    "caf": [[1]],
    "cap": [[1, 2]],
    "lgf": [[1]],
    "cur": [[1, 2]],
    "vpd": [[1, 2]],
    "grp": [[1]],
    "grpa": [[1, 2]],
    "grpk": [[1, 2]],
    "dpf": [[1]],
    "dpc": [[1], [3]],
    "gpf": [[1]],
    "gpc": [[1, 2]],
    "spf": [[1]],
    "spc": [[1, 2]],
    "ppf": [[1]],
    "ppc": [[1, 2]],
    "tcp": [[1]],
    "pcpc": [[1]],
    "pcdf": [[1, 5]],
    "ccf": [[1]],
    "dst": [[1]],
    "cpc": [[1]],
    "cdf": [[1, 5, 6]],
    "ptv": [[1, 2]],
    "csf": [[1]],
    "css": [[1]],
    "sdf": [[1, 2, 4], [5]],
    "csp": [[1, 2]],
    "cvs": [[1]],
    "cve": [[1, 2]],
    "cvp": [[1, 2, 3]],
    "pst": [[1]],
    "psv": [[2]],
    "cps": [[1, 3]],
    "pvs": [[1, 6]],
    "psm": [[1, 2, 3]],
    "cca": [[1]],
    "ccs": [[1, 2], [1, 3]],
    "paf": [[1]],
    "pas": [[1, 2], [1, 3]],
    "prf": [[1]],
    "prv": [[1, 2]],
    "vdf": [],
    "ocf": [[1]],
    "ocp": [[1, 2]],
}
uint_pfc = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 24, 32, 48, 64]
time_pfc = [
    [-1, -1],
    [0, 6],
    [0, 8],
    [1, 0],
    [1, 1],
    [1, 2],
    [1, 3],
    [2, 0],
    [2, 1],
    [2, 3],
    [3, 0],
    [3, 1],
    [3, 2],
    [3, 3],
    [4, 0],
    [4, 1],
    [4, 2],
    [4, 3],
]
translation = {
    "type": "Type:",
    "start": "Start index:",
    "end": "End index:",
    "name": "Name:",
    "expression": "Expression:",
    "flav": "Specific type:",
    "array": "Array length:",
    "packed": "Is packed:",
    "form": "References to:",
    "bites": "Bite length:",
    "position": "Internal position:",
    "value": "Value:",
}
